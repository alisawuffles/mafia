from modifiers import Modifier


class Player:
    def __init__(self, name, index, modifiers=None):
        self.name = name
        self.index = index
        self.alignment = None
        self.role = None
        self.alive = True
        self.modifiers = modifiers if modifiers is not None else []

        # for tracking night actions
        self.hidden_behind = None
        self.hiding = []
        self.bodyguarded_by = None
        self.elite_bodyguarded_by = None
        self.protected = Modifier.BULLETPROOF in self.modifiers
        self.poison_day = 0
        self.furious = False
        self.framed = False

    def start_night(self):
        self.hidden_behind = None
        self.hiding = []
        self.bodyguarded_by = None
        self.elite_bodyguarded_by = None
        self.furious = False
        self.framed = False
        self.protected = Modifier.BULLETPROOF in self.modifiers
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
