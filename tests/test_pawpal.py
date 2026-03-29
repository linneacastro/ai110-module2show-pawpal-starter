import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Priority


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", category="Exercise", duration=30, priority=Priority.HIGH)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="Dog", age=4)
    task = Task(title="Breakfast", category="Feeding", duration=10, priority=Priority.HIGH)
    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1
