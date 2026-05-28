"""
we do not really care about roles, only who performed what actions

input: actions
create mapping from source to target
run actions on mapping
return outcomes
"""

import re

from player import Player
from action import (
    Hitman,
    BatchBusDrive,
    ACTION_REGISTRY,
    BLOCK_ACTIONS,
    REDIRECTION_ACTIONS,
)
from collections import defaultdict


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

        self._reset_mapping()

    def _reset_mapping(self):
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

        # TODO: this code is broken
        # if multiple bus drives, consolidate into a single BatchBusDrive
        # and duplicate actions whose targets expand (e.g. kill(B) -> kill(A), kill(C))
        bus_drive_entries = [(p, a) for p, a in actions if a.get_name() == "bus_drive"]
        if len(bus_drive_entries) > 1:
            # build swap graph to know which targets expand
            swaps = defaultdict(set)
            for _, bd_action in bus_drive_entries:
                swaps[bd_action.target_a].add(bd_action.target_b)
                swaps[bd_action.target_b].add(bd_action.target_a)

            for entry in bus_drive_entries:
                actions.remove(entry)
            batch = BatchBusDrive(bus_drive_entries)
            actions.append((bus_drive_entries[0][0], batch))

            # duplicate actions whose targets expand to multiple players
            new_actions = []
            for player, action in actions:
                if action.get_name() in REDIRECTION_ACTIONS:
                    new_actions.append((player, action))
                    continue
                targets = action.get_targets()
                if (
                    len(targets) == 1
                    and targets[0] in swaps
                    and len(swaps[targets[0]]) > 1
                ):
                    # target expands to multiple — create one action per expanded target
                    actions.remove((player, action))
                    for new_target in swaps[targets[0]]:
                        new_actions.append(
                            (player, ACTION_REGISTRY[action.get_name()](new_target))
                        )
                else:
                    new_actions.append((player, action))
            actions = new_actions

        redirection_players = {
            p for p, a in actions if a.get_name() in REDIRECTION_ACTIONS
        }

        # find bus/trolley drivers that are being mailed
        mailed_redirection_players = set()
        for _, action in actions:
            if action.get_name() == "mail":
                targets = action.get_targets()
                if targets[0] in redirection_players:
                    mailed_redirection_players.add(targets[0])

        def sort_key(entry):
            player, action = entry
            name = action.get_name()
            # (1) blocks on redirection players
            if name in BLOCK_ACTIONS and action.target in redirection_players:
                return (0, 0)
            # (2) mails on redirection players
            elif name == "mail" and action.mail_from in redirection_players:
                return (1, 0)
            # (3) mailed redirections
            elif name in REDIRECTION_ACTIONS and player in mailed_redirection_players:
                return (1, 2)
            # (4) other redirections
            elif name in REDIRECTION_ACTIONS:
                return (1, 1, phase_order.index(name))
            # everything else
            else:
                return (2, phase_order.index(name))

        return sorted(actions, key=sort_key)

    def run_actions(self, action_strs):
        # populate intended mapping from source to target so we can modify with mischief roles
        self._reset_mapping()
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
        print("-- Actions --")

        # start night
        for player in self.index_to_player.values():
            player.start_night()

        # execute actions
        for player, action in actions:
            if self.mapping[player] and action.get_name() != "batched_bus_drive":
                action.run(player, self.mapping)

        # record global visitors for forensic investigator
        for source, targets in self.mapping.items():
            for target in targets:
                target.all_visitors.append(source)

        # end night
        for player in self.index_to_player.values():
            player.end_night()

    def print_actions(self, actions):
        for player, action in actions:
            print(
                f"{player.name}: {action.get_name()}({', '.join([t.name for t in action.get_targets()])})"
            )

    def print_mapping(self):
        for source, targets in self.mapping.items():
            target_names = [t.name for t in targets]
            print(f"{source.name} -> {', '.join(target_names)}")

    def print_night_summary(self):
        print("-- Visit summary --")
        self.print_mapping()
