from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum
from typing import List, Optional
from uuid import UUID, uuid4

VALID_FREQUENCIES = {"daily", "weekly"}


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    title: str
    category: str
    duration: int
    priority: Priority
    completed: bool = False
    id: UUID = field(default_factory=uuid4)
    assigned: bool = field(default=False, repr=False, init=False)
    frequency: Optional[str] = None
    due_date: Optional[date] = None

    def __setattr__(self, name: str, value) -> None:
        """Validate duration, priority, and frequency before setting any attribute."""
        title = getattr(self, "title", "(unknown)")
        if name == "duration" and value <= 0:
            raise ValueError(f"Task '{title}' duration must be greater than 0.")
        if name == "priority" and not isinstance(value, Priority):
            raise ValueError(f"Task '{title}' priority must be a Priority enum value.")
        if name == "frequency" and value is not None and value not in VALID_FREQUENCIES:
            raise ValueError(f"Task '{title}' frequency must be 'daily', 'weekly', or None.")
        object.__setattr__(self, name, value)

    def mark_complete(self) -> Optional[Task]:
        """Mark this task as completed and return the next occurrence if recurring.

        For a recurring task (frequency='daily' or 'weekly'), a new Task is
        returned with the same attributes but a fresh id, completed=False, and
        a due_date advanced by one day or one week using timedelta.  The base
        date for the calculation is due_date if set, otherwise today.

        Returns None for one-off tasks (frequency=None).
        Raises RuntimeError if the task is already marked complete.
        """
        if self.completed:
            raise RuntimeError(f"Task '{self.title}' is already marked complete.")
        self.completed = True
        if self.frequency is None:
            return None
        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        base = max(self.due_date, date.today()) if self.due_date is not None else date.today()
        next_due = base + delta
        return Task(
            title=self.title,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_due,
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_owner", None)

    @property
    def owner(self) -> Optional[Owner]:
        """Return the owner this pet is registered to, or None."""
        return getattr(self, "_owner", None)

    def __setattr__(self, name: str, value) -> None:
        """Validate age before setting any attribute."""
        if name == "age" and value < 0:
            pet_name = getattr(self, "name", "(unknown)")
            raise ValueError(f"Pet '{pet_name}' age cannot be negative.")
        object.__setattr__(self, name, value)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet, raising an error if already assigned elsewhere."""
        if task.assigned:
            raise ValueError(f"Task '{task.title}' is already assigned to a pet.")
        task.assigned = True
        self.tasks.append(task)

    def edit_task(self, task: Task) -> None:
        """Replace an existing task (matched by id) with the updated version."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                if t.completed:
                    raise RuntimeError(f"Task '{t.title}' is already completed and cannot be edited.")
                if task.completed:
                    raise ValueError(f"Cannot replace '{t.title}' with an already-completed task. Use complete_task() instead.")
                if task.assigned and t is not task:
                    raise ValueError(f"Task '{task.title}' is already assigned to another pet.")
                t.assigned = False
                task.assigned = True
                self.tasks[i] = task
                return
        raise ValueError(f"Task '{task.title}' not found for {self.name}.")

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet by id, unassigning it."""
        for t in self.tasks:
            if t.id == task.id:
                self.tasks.remove(t)
                t.assigned = False
                return
        raise ValueError(f"Task '{task.title}' not found for {self.name}.")

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if recurring, add the next occurrence to this pet.

        Returns the newly created next Task if the task recurs, or None if it
        was a one-off task.
        """
        for stored in self.tasks:
            if stored.id == task.id:
                next_task = stored.mark_complete()
                if next_task is not None:
                    self.add_task(next_task)
                return next_task
        raise ValueError(f"Task '{task.title}' not found for {self.name}.")

    def get_tasks(self) -> List[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: List[str], session_start: str = "08:00"):
        """Initialize an Owner with a name, daily time budget, care preferences, and session start time."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.session_start = session_start
        self.pets: List[Pet] = []

    @property
    def available_minutes(self) -> int:
        """Return the owner's daily available time budget in minutes."""
        return self._available_minutes

    @available_minutes.setter
    def available_minutes(self, value: int) -> None:
        """Set available_minutes, enforcing it must be greater than 0."""
        if value <= 0:
            raise ValueError("available_minutes must be greater than 0.")
        self._available_minutes = value

    @property
    def session_start(self) -> str:
        """Return the session start time as an HH:MM string."""
        return self._session_start

    @session_start.setter
    def session_start(self, value: str) -> None:
        """Set session_start, validating format and updating session_start_minutes."""
        try:
            parts = value.split(":")
            if len(parts) != 2:
                raise ValueError
            h, m = int(parts[0]), int(parts[1])
            if not (0 <= h <= 23 and 0 <= m <= 59):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError(f"session_start '{value}' must be a valid time in HH:MM format.")
        self._session_start = value
        self._session_start_minutes = h * 60 + m

    @property
    def session_start_minutes(self) -> int:
        """Return the session start time as total minutes since midnight."""
        return self._session_start_minutes

    def add_pet(self, pet: Pet) -> None:
        """Register a pet to this owner, raising an error if already owned or duplicate name."""
        if pet.owner is not None:
            raise ValueError(f"'{pet.name}' already belongs to '{pet.owner.name}'. Remove it first.")
        if any(p.name.lower() == pet.name.lower() for p in self.pets):
            raise ValueError(f"A pet named '{pet.name}' is already registered to {self.name}.")
        object.__setattr__(pet, "_owner", self)
        self.pets.append(pet)

    def get_tasks(self, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Return tasks across all pets, optionally filtered by completion status and/or pet name.

        Raises ValueError if pet_name is provided but no matching pet is found.
        """
        results = []
        found_pet = False
        for pet in self.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            found_pet = True
            for task in pet.tasks:
                if completed is None or task.completed == completed:
                    results.append(task)
        if pet_name is not None and not found_pet:
            raise ValueError(f"No pet named '{pet_name}' found for {self.name}.")
        return results

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner, clearing its owner reference."""
        for p in self.pets:
            if p is pet:
                self.pets.remove(p)
                object.__setattr__(pet, "_owner", None)
                return
        raise ValueError(f"No pet named '{pet.name}' found for {self.name}.")


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the Scheduler with the owner whose pets and tasks will be planned."""
        self.owner = owner

    def build_plan(self) -> dict:
        """Build a prioritized schedule of pet tasks within the owner's available time budget.

        Tasks are sorted by priority (descending), then by whether their category matches
        the owner's preferences, then by duration (descending). A greedy first pass schedules
        tasks in order; a second pass attempts to fit any that were skipped.

        Returns a dict with keys:
            - 'owner': owner name
            - 'scheduled': list of task entries that fit, each with a 'start_time'
            - 'deferred': skipped tasks that could fit in a longer session
            - 'too_long': skipped tasks that exceed the total available time budget
            - 'total_scheduled_minutes': total minutes consumed
            - 'remaining_minutes': unused minutes in the session
            - 'warnings': list of conflict warning strings from detect_conflicts

        Raises ValueError if the owner has no registered pets, or no incomplete tasks.
        """
        if not self.owner.pets:
            raise ValueError(f"'{self.owner.name}' has no registered pets to schedule.")
        preferences = {p.lower() for p in self.owner.preferences}

        candidate_tasks = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.tasks
            if not task.completed
        ]

        if not candidate_tasks:
            raise ValueError(f"'{self.owner.name}' has no incomplete tasks to schedule.")

        candidate_tasks.sort(key=lambda pt: (
            -pt[1].priority,
            0 if pt[1].category.lower() in preferences else 1,
            -pt[1].duration,
        ))

        scheduled = []
        first_pass_skipped = []
        remaining_minutes = self.owner.available_minutes

        session_start_minutes = self.owner.session_start_minutes
        current_minute = 0

        for pet, task in candidate_tasks:
            entry = {
                "id": task.id,
                "pet": pet.name,
                "task": task.title,
                "category": task.category,
                "duration": task.duration,
                "priority": task.priority.name,
                "preferred": task.category.lower() in preferences,
            }
            if task.duration <= remaining_minutes:
                total = session_start_minutes + current_minute
                scheduled.append({**entry, "start_time": f"{total // 60:02}:{total % 60:02}"})
                remaining_minutes -= task.duration
                current_minute += task.duration
            else:
                first_pass_skipped.append(entry)

        second_pass_skipped = []
        for entry in sorted(
            first_pass_skipped,
            key=lambda e: (-Priority[e["priority"]].value, 0 if e["preferred"] else 1, -e["duration"]),
        ):
            if entry["duration"] <= remaining_minutes:
                total = session_start_minutes + current_minute
                scheduled.append({**entry, "start_time": f"{total // 60:02}:{total % 60:02}"})
                remaining_minutes -= entry["duration"]
                current_minute += entry["duration"]
            else:
                second_pass_skipped.append(entry)

        too_long = [e for e in second_pass_skipped if e["duration"] > self.owner.available_minutes]
        deferred = [e for e in second_pass_skipped if e["duration"] <= self.owner.available_minutes]

        warnings = self.detect_conflicts(scheduled)

        return {
            "owner": self.owner.name,
            "scheduled": scheduled,
            "deferred": deferred,
            "too_long": too_long,
            "total_scheduled_minutes": self.owner.available_minutes - remaining_minutes,
            "remaining_minutes": remaining_minutes,
            "warnings": warnings,
        }

    def detect_conflicts(self, scheduled: list) -> list:
        """Check a list of scheduled task entries for time overlaps.

        Returns a list of warning strings describing each conflict found.
        An empty list means no conflicts were detected.
        """
        def to_minutes(time_str: str) -> int:
            h, m = time_str.split(":")
            return int(h) * 60 + int(m)

        warnings = []
        for i, a in enumerate(scheduled):
            for b in scheduled[i + 1:]:
                a_start = to_minutes(a["start_time"])
                a_end = a_start + a["duration"]
                b_start = to_minutes(b["start_time"])
                b_end = b_start + b["duration"]
                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"Conflict: '{a['task']}' ({a['pet']}, "
                        f"{a['start_time']}–{a_end // 60:02}:{a_end % 60:02}) overlaps with "
                        f"'{b['task']}' ({b['pet']}, "
                        f"{b['start_time']}–{b_end // 60:02}:{b_end % 60:02})"
                    )
        return warnings
