# PawPal+ Project Reflection

## 1. System Design

PawPal+ is a Streamlit app designed to help pet owners stay on top of their pet care routines. It lets users enter basic info about themselves and their pet, add and manage care tasks like walks, feeding, medications, grooming, and enrichment, and then generates a daily schedule based on their available time, task priorities, and preferences. It also explains the reasoning behind the plan it creates, so the owner understands why things were scheduled the way they were.

The three core actions, summarized: 
1. Enter a pet
2. Create tasks like walks, grooming, etc.
3. Generate a daiy schedule and view it

**a. Initial design**

- Briefly describe your initial UML design.
The system is built around four classes. The Owner holds the user's name, how many minutes they have available in a day, and care preferences. They can have one or more Pets, and each Pet stores basic info like name, species, and age, along with a list of Tasks that can be added, edited, or removed. Each Task captures the details of a single care activity: its title, category (like feeding or grooming), how long it takes, its priority level, and whether it's been completed. Finally, the Scheduler takes the Owner's time constraints and the Pet's task list and uses them together to produce a daily care plan.

- What classes did you include, and what responsibilities did you assign to each?

There are four classes, each with a focused responsibility:

Owner — represents the person using the app; holds their name, available time, and preferences, and keeps track of which pets they have.
Pet — represents the pet being cared for; stores basic info like name, species, and age, and manages the list of tasks associated with that pet.
Task — represents a single care activity; holds the details like title, category, duration, priority, and whether it's been completed.
Scheduler — the brain of the app; it reads the owner's time constraints and the pet's task list and uses that information to build a daily care plan.

**b. Design changes**

- Did your design change during implementation?
Yes! When I asked about bottlenecks in logic or missing relationships, it returned to me quite a few items. This was a really eye opening prompt.

- If yes, describe at least one change and why you made it.
Here is one change made to the Priority. Priority is now  IntEnum (new)
This replaces the free int field. Callers can now only pass Priority.LOW, Priority.MEDIUM, or Priority.HIGH. Before there could be ambiguous values passed in like 99 or -1 that made their way to build_plan().

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers three main constraints:

Time is the primary hard constraint — the owner's available_minutes budget acts as a cap. Tasks are greedily packed into the session starting from session_start_minutes, and any task whose duration exceeds the remaining time is skipped (deferred or marked as too-long).

Priority is the primary soft constraint — tasks are sorted by their Priority enum value (descending), so high-priority tasks are scheduled first and are least likely to get bumped when time runs short.

Preferences act as a tiebreaker — the owner's preferred task categories (e.g., "grooming", "exercise") are boosted in sort order so that preferred-category tasks slot in before non-preferred ones of equal priority and duration.

- How did you decide which constraints mattered most?

Priority was ranked first because a missed high-priority task (like medication) has real consequences for a pet's wellbeing, so it should always be scheduled before lower-priority ones regardless of preferences. Time comes next as a hard physical constraint. Preferences were treated last as a quality-of-life tiebreaker, since they improve the owner's experience but don't affect correctness or pet health the way priority and time do.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler uses a greedy first-fit approach — it picks tasks in priority order and immediately locks each one in if it fits. This is fast and simple, but it can leave time on the table. For example, one large low-priority task might get scheduled early and block several smaller high-priority tasks that could have fit in the same slot.

Another thing that is a tradeoff is the way my current scheduler is stacking tasks one right after the other with no break inbetween. I think that in a future iteration, it would be more schedule sensitive and allow the user to pick a time to make things happen. This is something I'm planning on adressing once I have had time to test the full program in the web UI.

- Why is that tradeoff reasonable for this scenario?
I could do something dynamic like knapsack optimization to maximize total value within the time budget, but I chose the greedy method was chosen for simplicity and predictability. I kind of want to be able to choose a simple option first and see how it plays out before making larger changes. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

The assignment asked for 

- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I came up with an interesting situation - the assignment asked me to create a test to detext task conflicts. The way my program was structured, everything was slotted in sequentially, making conflicts impossible. When I implemented this test as requested, it felt a little bit superficial since the situation where it would arise wouldn't occur in my program as designed. This felt like something I put in just for the sake of the assignment.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
