# CSE Mafia

Specify game in `main.py` and run with `python -m main`.

The purpose of this tool is to support action resolution. It currently does not produce investigation results, which should be easy for the mod to read off based on the resolved actions. It also does not verify the validity of actions (e.g., checking that a player uses an ability they have) or perform functions that would change the validity of actions the next night (e.g., doubling).

The night is fully determined by a set of players performing actions on targets. The script automatically determines the correct order of actions. The role performing the action is irrelevant (vigilante and mafia kills are resolved the same way).

There is no support for determining whether end-of-game criteria is met.

**TODO:**
- [x] add support for investigation results. requires creating a separate `used_mapping` dictionary, which is modified each time an action is taken. this differs from `mapping` which tracks the current mapping.
- [ ] (maybe) add support for forensic investigation results. requires yet another dictionary global over nights.
- [ ] add support for paranoid players. no idea how this is going to happen.
- [ ] maybe related: add support for TNT.
- [ ] add support for logic gate. this will be a big undertaking as it requires re-rolling out subsequent actions after modifying the success of a former action.
- [ ] multiple bus drives and mailmen are likely not resolved in the most desirable way.
- [ ] pretty-print all player information (alive/dead, modifiers)

## Design decisions
### How to resolve blocks and redirections?
Blocks and redirections are resolved in the following order so that mischief roles are blockable, but blocks can travel through redirections.
1. Blocks targeting a redirection.
2. Redirection actions — modify the mapping for everything after.
3. Other blocks — flows through the revised mapping.

This leads to a reasonable ruling in all three cases:
- If A blocks B and X bus drives B and C, does the bus drive occur? Yes
- If A blocks B and B bus drives C and D, does the bus drive occur? No
- If A blocks B and B bus drives B and C, does the bus drive occur? No

### How to resolve mailmen and bus drives?