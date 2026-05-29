# CSE Mafia

Specify game in `main.py` and run with `python -m main`.

The purpose of this tool is to support action resolution. The night is fully determined by a set of players performing actions on targets, and the script automatically executes the actions in the correct order. 

We do not verify the validity of the actions (e.g., checking that player uses an ability they have) or support functionality that would change the validity of actions the following night (e.g., doubling, enthralling book). Note we do not keep track of player roles at all, as they are irrelevant to the action resolution (vigilante and mafia kills are resolved the same way). Because of this, we also do not determine when the end-of-game criteria is met.

### TODO:
- [x] support investigation results
- [x] resolve mailman and bus drive correctly
- [x] mail only succeeds if the number of targets specified is exactly correct
- [ ] support multiple actions from the same player
- [ ] imposter should change what investigators see
- [ ] support paranoid players
- [ ] maybe related: support TNT
- [ ] support logic gate (this will be a big undertaking as it requires re-rolling out subsequent actions after modifying the success of a former action)
- [ ] support multiple bus drives (in-progress `BatchedBusDrive`)
- [ ] pretty-print all player information (alive/dead, modifiers)
- [x] fix hider logic

## Design decisions
Ordering:
1. Blocks / jailkeeps on redirection players
2. Mails targeting a redirection player
3. Redirection actions
4. Everything else

### Rulings
- A player can be saved from poisoning on either the day of poisoning or the following day.
- A mailman needs to specify exactly the right number of targets matching the action they are mailing (they can specify as many recipients of mail as they'd like), otherwise the mail fails.
- Hider can inherit poisoning on the night of poisoning, but will not die on the day a poisoned player dies.
- An elite bodyguard poisons-back the poisoner.
- Only single-target abilities can be paranoid.
- If there are two bus drives A <-> B and B <-> C, then actions on B land on both A and C, while actions on either A or C lands on B.
- A CPR resolves like a regular kill if the target is otherwise alive. This means that CPR-kill on a hider would miss, and CPR-kill on someone would also kill their hider(s). If target should otherwise die, then the CPR saves them and also their hider(s).

### How to resolve blocks and redirections?
Blocks and redirections are resolved in the following order. This makes it so that mischief roles are blockable, yet blocks can travel through redirections.
1. Blocks targeting a redirection
2. Redirection actions — modify the mapping for everything after
3. Other blocks — flows through the revised mapping

This leads to reasonable rulings in all three cases:
- If A blocks B and X bus drives B and C, does the bus drive occur? Yes
- If A blocks B and B bus drives C and D, does the bus drive occur? No
- If A blocks B and B bus drives B and C, does the bus drive occur? No

### How to resolve mailmen and bus drives?
If a mailman mails a bus driver, then the mail should come first. Otherwise, the bus drive comes first. In other words,
1. Mails targeting bus drive actions
2. Bus drives
3. Other mails

This leads to a reasonable ruling in the following cases:
- If A bus drives B and C and X mails A to D and E, what happens? Mail first, so D and E are bus driven
- If A bus drives B and C and X mails B to D, what happens? Bus drive first, so C is mailed to D

### Alisa's design principles
These are the design principles that motivate my rulings.
- Blocks should not land on players after their action has already been performed.
- When resolving the order of two actions, the one affecting which action the other takes should generally come first.
- Actions of the same type should be resolved "simultaneously". For instance, if A and B block each other, then both are blocked and visit each other. If two bus drives A <-> B and B <-> C occurs, the resolution should treat both bus drives with equal status.
- Avoid randomness and arbitrariness whenever possible. We refuse to import `random` in this repo. :)