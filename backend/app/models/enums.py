import enum


class EventType(str, enum.Enum):
    fixed = 'fixed'
    flexible = 'flexible'


class LockMode(str, enum.Enum):
    unlocked = 'unlocked'
    locked = 'locked'
    pinned_day = 'pinned_day'
    pinned_time = 'pinned_time'
    pinned_day_time = 'pinned_day_time'


class EnergyLevel(str, enum.Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'


class ScheduleMode(str, enum.Enum):
    full_auto = 'full_auto'
    respect_locks = 'respect_locks'
    fill_gaps = 'fill_gaps'
    rebalance = 'rebalance'


class TaskStatus(str, enum.Enum):
    todo = 'todo'
    in_progress = 'in_progress'
    done = 'done'


class GoalStatus(str, enum.Enum):
    active = 'active'
    completed = 'completed'
