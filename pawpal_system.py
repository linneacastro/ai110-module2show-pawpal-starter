from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional
from uuid import UUID, uuid4


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

    def __setattr__(self, name: str, value) -> None:
        """Validate duration and priority before setting any attribute."""
        if name == "duration" and value <= 0:
            raise ValueError(f"Task '{self.title}' duration must be greater than 0.")
        if name == "priority" and not isinstance(value, Priority):
            raise ValueError(f"Task '{self.title}' priority must be a Priority enum value.")
        object.__setattr__(self, name, value)

    def mark_complete(self) -> None:
        """Mark this task as completed, raising an error if already complete."""
        if self.completed:
            raise ValueError(f"Task '{self.title}' is already marked complete.")
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)
    owner: Optional[Owner] = field(default=None, repr=False)

    def __setattr__(self, name: str, value) -> None:
        """Validate age before setting any attribute."""
        if name == "age" and value < 0:
            raise ValueError(f"Pet '{self.name}' age cannot be negative.")
        object.__setattr__(self, name, value)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet, raising an error if already assigned elsewhere."""
        if task.assigned:
            raise ValueError(f"Task '{task.title}' is already assigned to another pet.")
        task.assigned = True
        self.tasks.append(task)

    def edit_task(self, task: Task) -> None:
        """Replace an existing task (matched by id) with the updated version."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                t.assigned = False
                task.assigned = True
                self.tasks[i] = task
                return
        raise ValueError(f"Task '{task.title}' not found for {self.name}.")

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet by id, unassigning it."""
        for i, t in enumerate(self.tasks):
            if t.id == task.id:
                self.tasks.pop(i)
                task.assigned = False
                return
        raise ValueError(f"Task '{task.title}' not found for {self.name}.")

    def get_tasks(self) -> List[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: List[str]):
        """Initialize an Owner with a name, daily time budget, and care preferences."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
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

    def add_pet(self, pet: Pet) -> None:
        """Register a pet to this owner, raising an error if already owned or duplicate name."""
        if pet.owner is not None:
            raise ValueError(f"'{pet.name}' already belongs to '{pet.owner.name}'. Remove it first.")
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"A pet named '{pet.name}' is already registered to {self.name}.")
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Unregister a pet from this owner, clearing its owner reference."""
        for i, p in enumerate(self.pets):
            if p.name == pet.name:
                self.pets.pop(i)
                pet.owner = None
                return
        raise ValueError(f"No pet named '{pet.name}' found for {self.name}.")


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialize the Scheduler with the owner whose pets and tasks will be planned."""
        self.owner = owner

    def build_plan(self) -> dict:
        """Build a prioritized schedule of pet tasks within the owner's available time budget."""
        preferences = {p.lower() for p in self.owner.preferences}

        candidate_tasks = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_tasks()
            if not task.completed
        ]

        candidate_tasks.sort(key=lambda pt: (
            -pt[1].priority,
            0 if pt[1].category.lower() in preferences else 1,
            pt[1].duration,
        ))

        scheduled = []
        first_pass_skipped = []
        remaining_minutes = self.owner.available_minutes

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
                scheduled.append(entry)
                remaining_minutes -= task.duration
            else:
                first_pass_skipped.append(entry)

        second_pass_skipped = []
        for entry in sorted(first_pass_skipped, key=lambda e: e["duration"]):
            if entry["duration"] <= remaining_minutes:
                scheduled.append(entry)
                remaining_minutes -= entry["duration"]
            else:
                second_pass_skipped.append(entry)

        too_long = [e for e in second_pass_skipped if e["duration"] > self.owner.available_minutes]
        deferred = [e for e in second_pass_skipped if e["duration"] <= self.owner.available_minutes]

        return {
            "owner": self.owner.name,
            "scheduled": scheduled,
            "deferred": deferred,
            "too_long": too_long,
            "total_scheduled_minutes": self.owner.available_minutes - remaining_minutes,
            "remaining_minutes": remaining_minutes,
        }
