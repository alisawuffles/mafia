# CSE Mafia

Specify game in `main.py` and run with `python -m main`.

The purpose of this tool is to support action resolution. The night is fully determined by a set of players performing actions on targets, and the script automatically executes the actions in the correct order. 

We do not verify the validity of the actions (e.g., checking that player uses an ability they have) or support functionality that would change the validity of actions the following night (e.g., doubling, enthralling book). Note we do not keep track of player roles at all, as they are irrelevant to the action resolution (vigilante and mafia kills are resolved the same way). Because of this, we also do not determine when the end-of-game criteria is met.

### TODO:
- [x] add support for investigation results
- [x] revised resolution of mailman and bus drive order
- [x] mail only succeeds (and does not throw an error) if the number of targets specified is exactly correct
- [ ] (maybe) add support for forensic investigation results
- [ ] add support for paranoid players (no idea how this is going to happen)
- [ ] maybe related: add support for TNT
- [ ] add support for logic gate (this will be a big undertaking as it requires re-rolling out subsequent actions after modifying the success of a former action)
- [ ] multiple bus drives and mailmen are likely not resolved in the most desirable way
- [ ] pretty-print all player information (alive/dead, modifiers)

## Design decisions
Ordering:
1. Blocks / jailkeeps on redirection players.
2. Mails targeting a redirection player.
3. Redirection actions.
4. Everything else.

### Choices made in the process
- A player can be saved from poisoning on either the day of poisoning or the following day
- A mailman needs to specify exactly the right number of targets matching the action they are mailing (they can specify as many recipients of mail as they'd like)
- Hider can inherit poisoning on the night of poisoning, but will not die on the day a poisoned player dies. An elite bodyguard poisons-back the poisoner.

### How to resolve blocks and redirections?
Blocks and redirections are resolved in the following order. This makes it so that mischief roles are blockable, yet blocks can travel through redirections.
1. Blocks targeting a redirection.
2. Redirection actions — modify the mapping for everything after.
3. Other blocks — flows through the revised mapping.

This leads to a reasonable ruling in all three cases:
- If A blocks B and X bus drives B and C, does the bus drive occur? Yes
- If A blocks B and B bus drives C and D, does the bus drive occur? No
- If A blocks B and B bus drives B and C, does the bus drive occur? No

### How to resolve mailmen and bus drives?
This should follow roughly the same intuition, which is that when resolving the order of two actions, the one affecting which action the other takes should come first. In this case, it means that if a mailman mails a bus driver, then the mail should come first. Otherwise, the bus drive comes first. In other words,
1. Mails targeting bus drive actions.
2. Bus drives.
3. Other mails.

This leads to a reasonable ruling in the following cases:
- If A bus drives B and C and X mails A to D and E, what happens? Mail first, so D and E are bus driven
- If A bus drives B and C and X mails B to D, what happens? Bus drive first, so C is mailed to D

### General rules of thumb
- Blocks should not land on players after their action has already been performed.