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
    id: UUID = field(default_factory=uuid4)
    completed: bool = False

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)
    owner: Optional[Owner] = field(default=None, repr=False)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        return list(self.tasks)


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: List[str]):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pets: List[Pet]):
        self.owner = owner
        self.pets = pets

    def build_plan(self) -> dict:
        pass
