"""
we do not really care about roles, only who performed what actions

input: actions
create mapping from source to target
run actions on mapping
return outcomes
"""

import re

from player import Player
from roles import ACTION_REGISTRY
from collections import defaultdict
from roles import Hitman

REDIRECTION_ACTIONS = {"bus_drive", "mail", "trolley_drive"}
BLOCK_ACTIONS = {"block", "jailkeep"}


class Game:
    def __init__(self, players, scum=None, modifiers=None):
        scum = scum or []
        modifiers = modifiers or {}

        self.index_to_player = {}
        for i, player_name in enumerate(players):
            self.index_to_player[i] = Player(player_name, i)

        self.name_to_player = {
            player.name: player for index, player in self.index_to_player.items()
        }

        for name, player in self.name_to_player.items():
            player.alignment = "guilty" if name in scum else "innocent"

        for identifier, mods in modifiers.items():
            player = self.resolve_player(str(identifier))
            if isinstance(mods, str):
                mods = [mods]
            for mod in mods:
                player.add_modifier(mod)

        self.mapping = defaultdict(list)

    def resolve_player(self, identifier):
        if identifier.isdigit():
            return self.index_to_player[int(identifier)]
        return self.name_to_player[identifier]

    def parse_action(self, action_str):
        match = re.match(r"(.+):\s*(\w+)\((.+)\)", action_str)
        source = self.resolve_player(match.group(1).strip())
        name = match.group(2)
        args = [arg.strip() for arg in match.group(3).split(",")]
        targets = [self.resolve_player(a) for a in args]
        return source, ACTION_REGISTRY[name](*targets)

    def sort_actions(self, actions):
        phase_order = list(ACTION_REGISTRY.keys())

        # if there is a Loki bus drive (that is not blocked), then we need to revise the created actions
        for player, action in actions:
            if action.get_name() == "loki_bus_drive":
                loki_blocked = any(
                    b.get_name() in BLOCK_ACTIONS and b.target == player
                    for _, b in actions
                )
                if not loki_blocked:
                    target_a, target_b = action.target_a, action.target_b

                    # find the actions belonging to target_a and target_b
                    a_entry = next(((p, a) for p, a in actions if p == target_a), None)
                    b_entry = next(((p, a) for p, a in actions if p == target_b), None)

                    # in order for LBD to succeed, both A and B must have performed an action with the same number of targets
                    if (
                        a_entry
                        and b_entry
                        and len(a_entry[1].get_targets())
                        == len(b_entry[1].get_targets())
                    ):
                        actions.remove((player, action))

                        # swap: a now performs b's action type on a's targets, and vice versa
                        actions.remove(a_entry)
                        actions.remove(b_entry)
                        a_player, a_action = a_entry
                        b_player, b_action = b_entry
                        actions.append(
                            (
                                a_player,
                                ACTION_REGISTRY[b_action.get_name()](
                                    *a_action.get_targets()
                                ),
                            )
                        )
                        actions.append(
                            (
                                b_player,
                                ACTION_REGISTRY[a_action.get_name()](
                                    *b_action.get_targets()
                                ),
                            )
                        )
                    # remove the Loki bus drive, since we have already applied it here
                    actions.remove((player, action))

        redirection_players = {
            p for p, a in actions if a.get_name() in REDIRECTION_ACTIONS
        }

        def sort_key(entry):
            player, action = entry
            name = action.get_name()
            if name in BLOCK_ACTIONS and action.target in redirection_players:
                return (0, 0)  # blocks on redirection players go first
            elif name in REDIRECTION_ACTIONS:
                return (1, phase_order.index(name))  # redirections go second
            else:
                return (2, phase_order.index(name))  # everything else in phase order

        return sorted(actions, key=sort_key)

    def run_actions(self, action_strs):
        # setup: populate intended mapping from source to target so we can modify with mischief roles
        actions = []
        for s in action_strs:
            player, action = self.parse_action(s)
            if isinstance(action, Hitman):
                player.role = "hitman"
            self.mapping[player] = action.get_targets()
            actions.append((player, action))

        actions = self.sort_actions(actions)
        print("Sorted actions:")
        self.print_actions(actions)
        print("----")

        # start night
        for player in self.index_to_player.values():
            player.start_night()

        # execute actions
        for player, action in actions:
            if self.mapping[player]:
                action.run(player, self.mapping)

        # end night
        for player in self.index_to_player.values():
            player.end_night()

    def get_game_state(self):
        return self.mapping

    def print_actions(self, actions):
        for player, action in actions:
            print(
                f"{player.name}: {action.get_name()}({', '.join([t.name for t in action.get_targets()])})"
            )

    def print_mapping(self):
        for source, targets in self.mapping.items():
            target_names = [t.name for t in targets]
            print(f"{source.name} -> {', '.join(target_names)}")
