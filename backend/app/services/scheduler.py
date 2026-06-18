from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.enums import EnergyLevel, EventType, LockMode, ScheduleMode
from app.models.event import Event
from app.models.setting import UserSetting
from app.utils.time import daterange


@dataclass
class Interval:
    start: datetime
    end: datetime

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


def _subtract_intervals(base: Interval, blocked: list[Interval]) -> list[Interval]:
    result = [base]
    for b in sorted(blocked, key=lambda x: x.start):
        next_result: list[Interval] = []
        for r in result:
            if b.end <= r.start or b.start >= r.end:
                next_result.append(r)
                continue
            if b.start > r.start:
                next_result.append(Interval(r.start, b.start))
            if b.end < r.end:
                next_result.append(Interval(b.end, r.end))
        result = next_result
    return [r for r in result if r.minutes >= 15]


def _expand_with_buffers(interval: Interval, buffer_minutes: int) -> Interval:
    return Interval(interval.start - timedelta(minutes=buffer_minutes), interval.end + timedelta(minutes=buffer_minutes))


def _parse_days(preferred_days: str | None) -> set[int]:
    if not preferred_days:
        return set()
    day_map = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
    values = set()
    for token in preferred_days.lower().replace(' ', '').split(','):
        if token[:3] in day_map:
            values.add(day_map[token[:3]])
    return values


def _preferred_time_bucket(hour: int) -> str:
    if 5 <= hour < 12:
        return 'morning'
    if 12 <= hour < 17:
        return 'afternoon'
    if 17 <= hour < 22:
        return 'evening'
    return 'night'


def _parse_hhmm(value: str) -> int | None:
    parts = value.strip().split(':')
    if len(parts) != 2:
        return None
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return hour * 60 + minute


def _parse_preferred_ranges(preferred_times: str | None) -> list[tuple[int, int]]:
    if not preferred_times:
        return []

    legacy = {
        'morning': (5 * 60, 12 * 60),
        'afternoon': (12 * 60, 17 * 60),
        'evening': (17 * 60, 22 * 60),
        'night': (22 * 60, 5 * 60),
    }

    ranges: list[tuple[int, int]] = []
    for token in preferred_times.lower().split(','):
        raw = token.strip()
        if not raw:
            continue
        if raw in legacy:
            ranges.append(legacy[raw])
            continue
        if '-' not in raw:
            continue
        start_raw, end_raw = [part.strip() for part in raw.split('-', 1)]
        start = _parse_hhmm(start_raw)
        end = _parse_hhmm(end_raw)
        if start is None or end is None or start == end:
            continue
        ranges.append((start, end))
    return ranges


def _candidate_in_preferred_ranges(start: datetime, duration: int, ranges: list[tuple[int, int]]) -> bool:
    if not ranges:
        return True
    start_minute = start.hour * 60 + start.minute
    end_minute = start_minute + duration
    if end_minute > 24 * 60:
        return False

    for window_start, window_end in ranges:
        if window_start < window_end:
            if start_minute >= window_start and end_minute <= window_end:
                return True
            continue
        # Overnight window (e.g., 22:00-05:00)
        if start_minute >= window_start and end_minute <= 24 * 60:
            return True
        if start_minute >= 0 and end_minute <= window_end:
            return True
    return False


def _preferred_range_span_minutes(ranges: list[tuple[int, int]]) -> int:
    if not ranges:
        return 24 * 60
    total = 0
    for start, end in ranges:
        if start < end:
            total += end - start
        else:
            total += (24 * 60 - start) + end
    return total


def _energy_for_hour(hour: int, energy_windows: dict) -> EnergyLevel:
    for level in [EnergyLevel.high, EnergyLevel.medium, EnergyLevel.low]:
        for block in energy_windows.get(level.value, []):
            if block['start'] <= hour < block['end']:
                return level
    return EnergyLevel.low


def _required_energy(priority: int) -> EnergyLevel:
    if priority <= 2:
        return EnergyLevel.high
    if priority == 3:
        return EnergyLevel.medium
    return EnergyLevel.low


def _day_idx(week_start: date, dt: datetime) -> int:
    return max(0, min(6, (dt.date() - week_start).days))


def _within_min_gap(start: datetime, end: datetime, event: dict, min_gap: int) -> bool:
    e_start = datetime.fromisoformat(event['start_time'])
    e_end = datetime.fromisoformat(event['end_time'])
    if end <= e_start:
        gap = (e_start - end).total_seconds() / 60
        return gap < min_gap
    if e_end <= start:
        gap = (start - e_end).total_seconds() / 60
        return gap < min_gap
    return True


def _score_candidate(
    category: Category,
    start: datetime,
    duration: int,
    settings: UserSetting,
    week_start: date,
    proposed_flexible: list[dict],
    day_minutes: list[int],
    anchors_by_category: dict[int, list[datetime]],
) -> float:
    score = 100.0

    actual_energy = _energy_for_hour(start.hour, settings.energy_windows)
    desired_energy = _required_energy(category.priority)
    if actual_energy == desired_energy:
        score += 18
    elif actual_energy == EnergyLevel.medium:
        score += 5
    else:
        score -= 12

    preferred_days = _parse_days(category.preferred_days)
    if preferred_days and start.weekday() in preferred_days:
        score += 8

    preferred_ranges = _parse_preferred_ranges(category.preferred_times)
    if preferred_ranges:
        if _candidate_in_preferred_ranges(start, duration, preferred_ranges):
            score += 10
        else:
            # Strong bias against scheduling outside preferred windows.
            score -= 20

    day_index = _day_idx(week_start, start)
    avg_day_minutes = (sum(day_minutes) + duration) / 7.0
    score += max(-10.0, min(10.0, (avg_day_minutes - day_minutes[day_index]) / 18.0))

    anchors = anchors_by_category.get(category.id, [])
    if anchors:
        nearest = min(abs((start - a).total_seconds()) for a in anchors)
        if nearest <= 3600:
            score += 14
        elif nearest <= 3 * 3600:
            score += 6

    for event in proposed_flexible:
        e_start = datetime.fromisoformat(event['start_time'])
        e_end = datetime.fromisoformat(event['end_time'])
        near = abs((start - e_end).total_seconds()) <= 1800 or abs((e_start - (start + timedelta(minutes=duration))).total_seconds()) <= 1800
        if near and event.get('category_id') != category.id:
            score -= 7
        elif near:
            score -= 3

    return score


def _build_daily_free_slots(week_start: date, settings: UserSetting, blocked_intervals: list[Interval]) -> list[Interval]:
    free_slots: list[Interval] = []
    for day in daterange(week_start, 7):
        day_start = datetime.combine(day, time(hour=settings.workday_start_hour))
        day_end = datetime.combine(day, time(hour=settings.workday_end_hour % 24))
        if day_end <= day_start:
            day_end = day_start + timedelta(hours=12)
        base = Interval(day_start, day_end)
        day_blocked = [b for b in blocked_intervals if b.start.date() <= day <= b.end.date()]
        free_slots.extend(_subtract_intervals(base, day_blocked))
    return sorted(free_slots, key=lambda i: i.start)


def _ceil_to_increment(dt: datetime, minutes: int) -> datetime:
    floored = dt.replace(second=0, microsecond=0)
    remainder = floored.minute % minutes
    if remainder == 0:
        return floored
    return floored + timedelta(minutes=(minutes - remainder))


def generate_schedule(db: Session, user_id: int, week_start: date, mode: ScheduleMode) -> tuple[list[dict], dict]:
    settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if not settings:
        settings = UserSetting(user_id=user_id)
        db.add(settings)
        db.flush()

    week_start_dt = datetime.combine(week_start, time.min)
    week_end_dt = week_start_dt + timedelta(days=7)

    categories = db.query(Category).filter(Category.user_id == user_id).all()
    events = (
        db.query(Event)
        .filter(Event.user_id == user_id, Event.start_time < week_end_dt, Event.end_time > week_start_dt)
        .all()
    )

    blocked: list[Interval] = []
    proposed: list[dict] = []

    buffer_minutes = settings.break_buffer_minutes + settings.commute_buffer_minutes + settings.prep_buffer_minutes

    anchors_by_category: dict[int, list[datetime]] = {}

    for event in events:
        is_immovable = event.event_type == EventType.fixed or event.lock_mode != LockMode.unlocked
        if is_immovable:
            blocked.append(_expand_with_buffers(Interval(event.start_time, event.end_time), buffer_minutes))
            proposed.append(
                {
                    'title': event.title,
                    'description': event.description,
                    'notes': event.notes,
                    'start_time': event.start_time.isoformat(),
                    'end_time': event.end_time.isoformat(),
                    'event_type': event.event_type.value,
                    'lock_mode': event.lock_mode.value,
                    'recurrence_rule': event.recurrence_rule,
                    'location': event.location,
                    'category_id': event.category_id,
                }
            )
            continue

        if mode == ScheduleMode.fill_gaps:
            blocked.append(Interval(event.start_time, event.end_time))
            proposed.append(
                {
                    'title': event.title,
                    'description': event.description,
                    'notes': event.notes,
                    'start_time': event.start_time.isoformat(),
                    'end_time': event.end_time.isoformat(),
                    'event_type': event.event_type.value,
                    'lock_mode': event.lock_mode.value,
                    'recurrence_rule': event.recurrence_rule,
                    'location': event.location,
                    'category_id': event.category_id,
                }
            )

        if mode == ScheduleMode.rebalance and event.category_id:
            anchors_by_category.setdefault(event.category_id, []).append(event.start_time)

    free_slots = _build_daily_free_slots(week_start, settings, blocked)

    existing_minutes_by_category: dict[int, int] = {}
    for event in events:
        if event.category_id is None:
            continue
        keep_existing = (
            event.event_type == EventType.fixed
            or event.lock_mode != LockMode.unlocked
            or mode == ScheduleMode.fill_gaps
        )
        if not keep_existing:
            continue
        minutes = int((event.end_time - event.start_time).total_seconds() // 60)
        existing_minutes_by_category[event.category_id] = existing_minutes_by_category.get(event.category_id, 0) + minutes

    proposed_flexible = [e for e in proposed if e['event_type'] == EventType.flexible.value]
    day_minutes = [0] * 7
    day_cat_count: dict[tuple[int, int], int] = {}

    for item in proposed_flexible:
        start = datetime.fromisoformat(item['start_time'])
        end = datetime.fromisoformat(item['end_time'])
        minutes = int((end - start).total_seconds() // 60)
        idx = _day_idx(week_start, start)
        day_minutes[idx] += minutes
        if item.get('category_id'):
            key = (idx, int(item['category_id']))
            day_cat_count[key] = day_cat_count.get(key, 0) + 1

    preferred_ranges_by_category: dict[int, list[tuple[int, int]]] = {
        category.id: _parse_preferred_ranges(category.preferred_times) for category in categories
    }

    # Schedule categories with explicit preferred windows first, then by narrowest window.
    # This avoids unconstrained categories consuming scarce preferred slots.
    sorted_categories = sorted(
        categories,
        key=lambda c: (
            c.priority,
            0 if preferred_ranges_by_category.get(c.id) else 1,
            _preferred_range_span_minutes(preferred_ranges_by_category.get(c.id, [])),
            -c.weekly_target_hours,
        ),
    )

    for category in sorted_categories:
        target_minutes = int(category.weekly_target_hours * 60)
        base_minutes = existing_minutes_by_category.get(category.id, 0)
        remaining = max(0, target_minutes - base_minutes)
        if remaining <= 0:
            continue

        block_size = max(15, int(category.session_length_minutes or 60))
        blocks_to_place = math.ceil(remaining / block_size)
        preferred_ranges = preferred_ranges_by_category.get(category.id, [])
        placed_blocks_for_category = 0
        category_daily_cap = max(1, int(category.max_blocks_per_day or settings.max_same_category_blocks_per_day))

        for _ in range(blocks_to_place):
            duration = block_size
            best_choice: tuple[float, int, datetime] | None = None
            # Phase 1: if a preferred time frame exists, try strict matching only.
            # Phase 2: fallback to any slot if no strict match is possible.
            if preferred_ranges and mode == ScheduleMode.respect_locks:
                # In respect_locks mode, never violate explicit preferred time ranges.
                phases = [True]
            else:
                phases = [True, False] if preferred_ranges else [False]
            for prefer_only in phases:
                for idx, slot in enumerate(free_slots):
                    if slot.minutes < duration:
                        continue
                    cursor = _ceil_to_increment(slot.start, 15)
                    while cursor + timedelta(minutes=duration) <= slot.end:
                        day_index = _day_idx(week_start, cursor)
                        if day_minutes[day_index] + duration > settings.max_flexible_minutes_per_day:
                            cursor += timedelta(minutes=15)
                            continue

                        key = (day_index, category.id)
                        if day_cat_count.get(key, 0) >= category_daily_cap:
                            cursor += timedelta(minutes=15)
                            continue

                        candidate_start = cursor
                        candidate_end = cursor + timedelta(minutes=duration)

                        if prefer_only and not _candidate_in_preferred_ranges(candidate_start, duration, preferred_ranges):
                            cursor += timedelta(minutes=15)
                            continue

                        violates_gap = False
                        for item in proposed_flexible:
                            if _within_min_gap(candidate_start, candidate_end, item, settings.min_gap_between_flexible_minutes):
                                violates_gap = True
                                break
                        if violates_gap:
                            cursor += timedelta(minutes=15)
                            continue

                        score = _score_candidate(
                            category,
                            candidate_start,
                            duration,
                            settings,
                            week_start,
                            proposed_flexible,
                            day_minutes,
                            anchors_by_category,
                        )
                        if best_choice is None or score > best_choice[0]:
                            best_choice = (score, idx, candidate_start)

                        cursor += timedelta(minutes=15)

                if best_choice is not None:
                    break

            # Safety fallback for respect_locks:
            # if strict preferred windows would schedule zero blocks for this category,
            # allow out-of-window placement so the category is not dropped entirely.
            if (
                best_choice is None
                and preferred_ranges
                and mode == ScheduleMode.respect_locks
                and placed_blocks_for_category == 0
            ):
                for idx, slot in enumerate(free_slots):
                    if slot.minutes < duration:
                        continue
                    cursor = _ceil_to_increment(slot.start, 15)
                    while cursor + timedelta(minutes=duration) <= slot.end:
                        day_index = _day_idx(week_start, cursor)
                        if day_minutes[day_index] + duration > settings.max_flexible_minutes_per_day:
                            cursor += timedelta(minutes=15)
                            continue

                        key = (day_index, category.id)
                        if day_cat_count.get(key, 0) >= category_daily_cap:
                            cursor += timedelta(minutes=15)
                            continue

                        candidate_start = cursor
                        candidate_end = cursor + timedelta(minutes=duration)

                        violates_gap = False
                        for item in proposed_flexible:
                            if _within_min_gap(candidate_start, candidate_end, item, settings.min_gap_between_flexible_minutes):
                                violates_gap = True
                                break
                        if violates_gap:
                            cursor += timedelta(minutes=15)
                            continue

                        score = _score_candidate(
                            category,
                            candidate_start,
                            duration,
                            settings,
                            week_start,
                            proposed_flexible,
                            day_minutes,
                            anchors_by_category,
                        )
                        if best_choice is None or score > best_choice[0]:
                            best_choice = (score, idx, candidate_start)

                        cursor += timedelta(minutes=15)

            if best_choice is None:
                break

            _, slot_index, start_time = best_choice
            end_time = start_time + timedelta(minutes=duration)
            chosen_slot = free_slots[slot_index]

            proposed_event = {
                'title': category.name,
                'description': category.description,
                'notes': None,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'event_type': EventType.flexible.value,
                'lock_mode': LockMode.unlocked.value,
                'recurrence_rule': None,
                'location': category.default_location,
                'category_id': category.id,
            }
            proposed.append(proposed_event)
            proposed_flexible.append(proposed_event)

            idx = _day_idx(week_start, start_time)
            day_minutes[idx] += duration
            key = (idx, category.id)
            day_cat_count[key] = day_cat_count.get(key, 0) + 1
            placed_blocks_for_category += 1

            new_parts = []
            if chosen_slot.start < start_time:
                new_parts.append(Interval(chosen_slot.start, start_time))
            if end_time < chosen_slot.end:
                new_parts.append(Interval(end_time, chosen_slot.end))
            free_slots = free_slots[:slot_index] + new_parts + free_slots[slot_index + 1 :]
            free_slots = sorted([s for s in free_slots if s.minutes >= 15], key=lambda s: s.start)

    proposed_sorted = sorted(proposed, key=lambda e: e['start_time'])

    totals_by_category: dict[int, int] = {}
    blocks_by_category: dict[int, int] = {}
    for item in proposed_sorted:
        if not item.get('category_id'):
            continue
        category_id = int(item['category_id'])
        minutes = int((datetime.fromisoformat(item['end_time']) - datetime.fromisoformat(item['start_time'])).total_seconds() // 60)
        totals_by_category[category_id] = totals_by_category.get(category_id, 0) + minutes
        if item['event_type'] == EventType.flexible.value:
            blocks_by_category[category_id] = blocks_by_category.get(category_id, 0) + 1

    per_category = []
    total_target = 0.0
    total_scheduled = 0.0
    for category in categories:
        target = float(category.weekly_target_hours)
        scheduled_hours = totals_by_category.get(category.id, 0) / 60.0
        total_target += target
        total_scheduled += scheduled_hours
        per_category.append(
            {
                'category_id': category.id,
                'category_name': category.name,
                'target_hours': round(target, 2),
                'scheduled_hours': round(scheduled_hours, 2),
                'deficit_hours': round(max(0.0, target - scheduled_hours), 2),
                'excess_hours': round(max(0.0, scheduled_hours - target), 2),
                'blocks_scheduled': blocks_by_category.get(category.id, 0),
            }
        )

    diagnostics = {
        'per_category': per_category,
        'total_target_hours': round(total_target, 2),
        'total_scheduled_hours': round(total_scheduled, 2),
        'average_daily_flexible_hours': round(sum(day_minutes) / 60.0 / 7.0, 2),
    }

    return proposed_sorted, diagnostics
