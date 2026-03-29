from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def print_schedule(plan: dict) -> None:
    width = 60
    print("\n" + "=" * width)
    print(f"  TODAY'S SCHEDULE FOR {plan['owner'].upper()}")
    print("=" * width)

    if plan["scheduled"]:
        print(f"\n  SCHEDULED  ({plan['total_scheduled_minutes']} min / {plan['remaining_minutes']} min remaining)\n")
        for entry in plan["scheduled"]:
            preferred_tag = " *" if entry["preferred"] else ""
            print(f"  [{entry['priority']:<6}]  {entry['task']:<28}  {entry['duration']:>3} min  ({entry['pet']}){preferred_tag}")
    else:
        print("\n  No tasks could be scheduled.")

    if plan["deferred"]:
        print(f"\n  DEFERRED  (fit in a longer session)\n")
        for entry in plan["deferred"]:
            print(f"  [{entry['priority']:<6}]  {entry['task']:<28}  {entry['duration']:>3} min  ({entry['pet']})")

    if plan["too_long"]:
        print(f"\n  TOO LONG  (exceeds total available time)\n")
        for entry in plan["too_long"]:
            print(f"  [{entry['priority']:<6}]  {entry['task']:<28}  {entry['duration']:>3} min  ({entry['pet']})")

    print("\n" + "=" * width + "\n")
    if plan["scheduled"] and any(e["preferred"] for e in plan["scheduled"]):
        print("  * preferred category\n")


# --- Setup ---

owner = Owner(
    name="Alex",
    available_minutes=60,
    preferences=["feeding", "exercise"],
)

dog = Pet(name="Biscuit", species="Dog", age=4)
cat = Pet(name="Mochi",   species="Cat", age=2)

owner.add_pet(dog)
owner.add_pet(cat)

# Biscuit's tasks
dog.add_task(Task(title="Morning walk",       category="Exercise",  duration=30, priority=Priority.HIGH))
dog.add_task(Task(title="Flea treatment",     category="Grooming",  duration=15, priority=Priority.MEDIUM))
dog.add_task(Task(title="Breakfast",          category="Feeding",   duration=10, priority=Priority.HIGH))

# Mochi's tasks
cat.add_task(Task(title="Litter box clean",   category="Hygiene",   duration=10, priority=Priority.HIGH))
cat.add_task(Task(title="Dinner",             category="Feeding",   duration=5,  priority=Priority.HIGH))
cat.add_task(Task(title="Laser pointer play", category="Exercise",  duration=20, priority=Priority.LOW))
cat.add_task(Task(title="Vet appointment",    category="Health",    duration=90, priority=Priority.HIGH))

# --- Run ---

scheduler = Scheduler(owner=owner)
plan = scheduler.build_plan()
print_schedule(plan)
