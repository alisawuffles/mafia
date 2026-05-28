# CSE Mafia

Specify game in `main.py` and run with `python -m main`.

The purpose of this tool is to support action resolution. Note that it does not produce mod notes (e.g., tracker/watcher results), which should be easy for the mod to read off. It also does not verify the validity of actions (e.g., checking that a player uses an ability they have) or perform functions that would change the validity of actions the next night (e.g., doubling).

Instead, the night is fully determined by players performing actions on targets. The script will automatically determine the order of actions. The role performing the action is irrelevant (vigilante and mafia kills are resolved the same way).

There is no support for determining whether end-of-game criteria is met.