from modifiers import Modifier


class Player:
    def __init__(self, name, index, modifiers=None):
        self.name = name
        self.index = index
        self.alignment = None
        self.alive = True
        self.modifiers = modifiers if modifiers is not None else []
        self.poison_day = 0
        self.all_visitors = []  # for forensic investigator
        self._reset_night_state()

    def _reset_night_state(self):
        self.is_hitman = False
        self.hidden_behind = None
        self.hiding = []
        self.bodyguarded_by = None
        self.elite_bodyguarded_by = None
        self.furious = False
        self.framed = False
        self.doubled = False
        self.protected = Modifier.BULLETPROOF in self.modifiers

    def start_night(self):
        self._reset_night_state()
        if self.poison_day == 1:
            self.poison_day = 2

    def end_night(self):
        if self.alive and self.poison_day == 2:
            print(f"{self.name} dies by poison")
            self.alive = False

    def add_modifier(self, modifier):
        if isinstance(modifier, str):
            modifier = Modifier(modifier)
        self.modifiers.append(modifier)

    def investigate(self):
        outcome = self.alignment
        if Modifier.SUSPICIOUS in self.modifiers or self.framed:
            outcome = "guilty"
        elif Modifier.GODFATHER in self.modifiers:
            outcome = "innocent"
        return outcome
