"""
- godfather
- warlord

- incarnation of fury
- ninja
- poisoner
"""

from modifiers import Modifier


class Action:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def get_name(self):
        return self.name

    def get_targets(self):
        targets = []
        for key in ["target", "mail_from", "target_a", "mail_to", "target_b"]:
            if hasattr(self, key):
                targets.append(getattr(self, key))
        return targets


### actions that determine the mapping from source to target


class Block(Action):
    def __init__(self, target):
        super().__init__("block", "prevents the target from using their night action")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        if target.role != "hitman":
            print(f"{player.name} blocks {target.name}")
            mapping[target] = []


class JailKeep(Action):
    def __init__(self, target):
        super().__init__("jail keep", "simultaneously blocks and protects the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        if target.role != "hitman":
            print(f"{player.name} jail keeps {target.name}")
            mapping[target] = []
            target.protected = True


class LokiBusDrive(Action):
    def __init__(self, target_a, target_b):
        super().__init__(
            "loki_bus_drive", "target_a and target_b swap actions, but not targets"
        )
        self.target_a = target_a
        self.target_b = target_b


class BusDrive(Action):
    def __init__(self, target_a, target_b):
        super().__init__(
            "bus_drive",
            "all actions that land on target_a land on target_b instead, and vice versa",
        )
        self.target_a = target_a
        self.target_b = target_b

    def run(self, player, mapping):
        target_a, target_b = mapping[player]
        print(f"{player.name} bus drives {target_a.name} and {target_b.name}")
        for _, targets in mapping.items():
            for i, t in enumerate(targets):
                if t == target_a:
                    targets[i] = target_b
                elif t == target_b:
                    targets[i] = target_a


class TrolleyDrive(Action):
    def __init__(self, target_a, target_b):
        super().__init__("trolley driver", "switches the targets of two players")
        self.target_a = target_a
        self.target_b = target_b

    def run(self, player, mapping):
        target_a, target_b = mapping[player]
        print(f"{player.name} trolley drives {target_a.name} and {target_b.name}")
        mapping[target_a], mapping[target_b] = mapping[target_b], mapping[target_a]


class Mail(Action):
    def __init__(self, mail_from, mail_to):
        super().__init__("mail", "redirects mail_from's action to mail_to")
        self.mail_from = mail_from
        self.mail_to = mail_to

    def run(self, player, mapping):
        mail_from, mail_to = mapping[player]
        print(f"{player.name} mails {mail_from.name} to {mail_to.name}")
        mapping[mail_from] = [mail_to]


class KickOutOfTime(Action):
    def __init__(self, target):
        super().__init__("kick_out_of_time", "all actions on target fail")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} kicks {target.name} out of time")
        for _, targets in mapping.items():
            if target in targets:
                targets.remove(target)


### actions that flow through mapping


class Protect(Action):
    def __init__(self, target):
        super().__init__("protect", "protects the target from being killed")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        target.protected = True
        if target.poison_day != 0:
            print(
                f"{player.name} protects {target.name} -> {target.name} saved from poison"
            )
            target.poison_day = 0
        else:
            print(f"{player.name} protects {target.name}")


class Bodyguard(Action):
    def __init__(self, target):
        super().__init__(
            "bodyguard", "protects target at the expense of their own life"
        )
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} bodyguards {target.name}")
        target.bodyguarded_by = player


class EliteBodyguard(Action):
    def __init__(self, target):
        super().__init__(
            "elite_bodyguard",
            "protects target at the expense of their own life, and shoots back at killer",
        )
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} elite-bodyguards {target.name}")
        target.elite_bodyguarded_by = player


class Frame(Action):
    def __init__(self, target):
        super().__init__("frame", "frames the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} frames {target.name}")
        target.framed = True


class Imposter(Action):
    def __init__(self, imposters_as, visits):
        super().__init__("imposter", "imposters the target")
        self.imposters_as = imposters_as
        self.visits = visits

    def run(self, player, mapping):
        imposters_as, visits = mapping[player]
        print(f"{player.name} imposters as {imposters_as.name} visiting {visits.name}")


class Investigate(Action):
    def __init__(self, target):
        super().__init__("investigate", "sees alignment of target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        outcome = target.alignment
        if Modifier.SUSPICIOUS in player.modifiers or player.framed:
            outcome = "guilty"
        elif Modifier.GODFATHER in player.modifiers:
            outcome = "innocent"
        print(f"{player.name} investigates {target.name} -> learns {outcome}")


class RoleInvestigate(Action):
    def __init__(self, target):
        super().__init__("role investigate", "sees role of target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} role investigates {target.name} -> learns {target.role}")


class Double(Action):
    def __init__(self, target):
        super().__init__("double", "doubles the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} doubles {target.name}")
        target.modifiers.append(Modifier.DOUBLED)


class Hide(Action):
    def __init__(self, target):
        super().__init__("hide", "hides the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        if target.alignment == "innocent":
            print(f"{player.name} hides behind {target.name} -> safe")
            player.hidden_behind = target
            target.hiding.append(player)
        else:
            print(f"{player.name} hides behind {target.name} -> {target.name} dies")
            player.alive = False


class Kill(Action):
    def __init__(self, target):
        super().__init__("kill", "kills the target")
        self.target = target
        self.kill_word = "kills"
        self.die_word = "dies"

    def kill_or_poison(self, target):
        target.alive = False

    def run(self, player, mapping):
        target = mapping[player][0]
        if target.protected:
            print(
                f"{player.name} {self.kill_word} {target.name} -> {target.name} protected"
            )
        elif target.hidden_behind:
            print(
                f"{player.name} {self.kill_word} {target.name} -> {target.name} protected by hiding"
            )
        elif target.bodyguarded_by:
            print(
                f"{player.name} {self.kill_word} {target.name} -> {target.name} saved by bodyguard, {target.bodyguarded_by.name} dies"
            )
            self.kill_or_poison(target.bodyguarded_by)
        elif target.elite_bodyguarded_by:
            print(
                f"{player.name} {self.kill_word} {target.name} -> {target.name} saved by elite bodyguard, {target.elite_bodyguarded_by.name} dies"
            )
            self.kill_or_poison(target.elite_bodyguarded_by)
            self.kill_or_poison(player)
        elif Modifier.STONE in target.modifiers:
            target.modifiers.remove(Modifier.STONE)
            print(
                f"{player.name} {self.kill_word} {target.name} -> {target.name} lives, loses stone"
            )
        else:
            self.kill_or_poison(target)
            message = f"{player.name} {self.kill_word} {target.name} -> {target.name} {self.die_word}"
            hiders = self.kill_hiders(target)
            if hiders:
                message += f" -> {', '.join([hider.name for hider in hiders])} {self.die_word} from hiding"
            print(message)

    def kill_hiders(self, target):
        hiders = []
        for hider in target.hiding:
            if not hider.protected:
                self.kill_or_poison(hider)
                hiders.append(hider)
        return hiders


class Poison(Kill):
    """
    Hiders get poisoned from hiding on the night of the poisoning, but do not die on the night someone dies from poison.
    """

    def __init__(self, target):
        super().__init__(target)
        self.name = "poison"
        self.description = "delayed kill"
        self.kill_word = "poisons"
        self.die_word = "poisoned"

    def kill_or_poison(self, player):
        # if target is already poisoned, we don't want to reset the poison
        if player.poison_day == 0:
            player.poison_day = 1


class NinjaKill(Kill):
    def __init__(self, target):
        super().__init__(target)
        self.name = "ninja_kill"
        self.description = "kills target while being invisible to trackers and watchers"
        self.kill_word = "ninja-kills"


class JanitorKill(Kill):
    def __init__(self, target):
        super().__init__(target)
        self.name = "janitor_kill"
        self.description = "victim's role and death note will not be revealed"
        self.kill_word = "janitor-kills"


class CPR(Action):
    def __init__(self, target):
        super().__init__("CPR", "saves target if killed, otherwise kills target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        if target.alive:
            print(f"{player.name} CPRs {target.name} -> {target.name} dies")
            target.alive = False
        else:
            print(f"{player.name} CPRs {target.name} -> {target.name} lives")
            target.alive = True


class Hitman(Kill):
    def __init__(self, target):
        super().__init__("hitman", "cannot be stopped by roleblock or protection")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} hitmans {target.name}")
        target.alive = False
        self.kill_hiders(target)
        print(
            f"{player.name} {self.kill_word} {target.name} -> {target.name + ', '.join([''] + [hider.name for hider in target.hiding])} die(s)"
        )


class Track(Action):
    def __init__(self, target):
        super().__init__("track", "tracks the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} tracks {target.name}")


class Watch(Action):
    def __init__(self, target):
        super().__init__("watch", "watches the target")
        self.target = target

    def run(self, player, mapping):
        target = mapping[player][0]
        print(f"{player.name} watches {target.name}")


ACTION_REGISTRY = {
    "block": Block,
    "jailkeep": JailKeep,
    "loki_bus_drive": LokiBusDrive,
    "bus_drive": BusDrive,
    "trolley_drive": TrolleyDrive,
    "mail": Mail,
    "kick_out_of_time": KickOutOfTime,
    "protect": Protect,
    "bodyguard": Bodyguard,
    "elite_bodyguard": EliteBodyguard,
    "frame": Frame,
    "imposter": Imposter,
    "investigate": Investigate,
    "role_investigate": RoleInvestigate,
    "double": Double,
    "hide": Hide,
    "kill": Kill,
    "ninja_kill": NinjaKill,
    "janitor_kill": JanitorKill,
    "poison": Poison,
    "CPR": CPR,
    "hitman": Hitman,
    "track": Track,
    "watch": Watch,
}
