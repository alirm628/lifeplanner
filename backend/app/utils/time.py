from datetime import date, datetime, time, timedelta


def week_bounds(week_start: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(week_start, time.min)
    end_dt = start_dt + timedelta(days=7)
    return start_dt, end_dt


def daterange(start: date, days: int = 7):
    for i in range(days):
        yield start + timedelta(days=i)


def overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def minutes_between(start: datetime, end: datetime) -> int:
    return int((end - start).total_seconds() // 60)
