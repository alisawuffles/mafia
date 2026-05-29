from game import Game

N0_ACTIONS = [
    "Alexandra: watch(Willie)",
    "Aman: CPR(Nick)",
    "Audrey: mail(Alisa, Willie)",
    "Brandon: hide(Alexandra)",
    "Jason: poison(Henry)",
    "Jon: doctor(Audrey)",
    "Sam: kill(Stanley)",
    "Alisa: block(Joseph)",
    "Henry: kill(Nick)",
    "Joseph: kick_out_of_time(Alisa)",
    "Nick: investigate(Joseph)",
    "Stanley: double(Alisa)",
    "Willie: investigate(Joseph)",
]

N1_ACTIONS = [
    "Alexandra: watch(Audrey)",
    "Aman: CPR(Willie)",
    "Audrey: mail(Aman, Brandon)",
    "Brandon: hide(Joseph)",
    "Jason: poison(Audrey)",
    "Jon: doctor(Aman)",
    "Sam: kill(Nick)",
    "Henry: bus_drive(Aman, Jon)",
    "Joseph: kick_out_of_time(Joseph)",
    "Nick: kill(Joseph)",
    "Willie: block(Oscar)",
]

N2_ACTIONS = [
    "Alexandra: watch(Audrey)",
    "Aman: CPR(Brandon)",
    "Audrey: mail(Brandon, Jon)",
    "Brandon: hide(Oscar)",
    "Jason: kill(Jon)",
    "Jon: doctor(Audrey)",
    "Oscar: kill(Aman)",
    "Sam: imposter(Brandon, Audrey)",
]


def main():
    game = Game(
        players=[
            "Audrey",
            "Alexandra",
            "Aman",
            "Brandon",
            "Jason",
            "Jon",
            "Oscar",
            "Sam",
            "Alisa",
            "Henry",
            "Joseph",
            "Nick",
            "Stanley",
            "Willie",
        ],
        scum=["Sam", "Oscar", "Jason", "Joseph"],
        modifiers={"Henry": "stone", "Alisa": "suspicious"},
    )
    print("----- Night 0 -----")
    game.run_actions(N0_ACTIONS)
    print("----- Night 1 -----")
    game.run_actions(N1_ACTIONS)
    print("----- Night 2 -----")
    game.run_actions(N2_ACTIONS)

    # game = Game(players=list("ABC"))
    # actions = ["A: CPR(B)", "C: doctor(B)"]
    # game.run_actions(actions)

    # hider test cases
    # game = Game(players=list("AXY"))
    # actions = ["X: CPR(A)", "Y: kill(A)"]
    # game.run_actions(actions)

    # game = Game(players=list("AXY"))
    # actions = ["X: CPR(A)", "Y: doctor(A)"]
    # game.run_actions(actions)

    # CPR also saves hider
    # game = Game(players=list("ABXY"))
    # actions = ["X: CPR(A)", "Y: kill(A)", "B: hide(A)"]
    # game.run_actions(actions)

    # game = Game(players=list("ABXY"))
    # actions = ["X: CPR(B)", "B: hide(A)"]
    # game.run_actions(actions)

    # imposter test cases
    # imposter action is invisible to watcher/tracker
    # game = Game(players=list("ABXY"))
    # actions = ["X: imposter(A, B)", "Y: track(X)"]
    # game.run_actions(actions)

    # game = Game(players=list("ABXY"))
    # actions = ["X: imposter(A, B)", "Y: watch(A)"]
    # game.run_actions(actions)

    # imposter leads to fake visitation from A to B
    # game = Game(players=list("ABXY"))
    # actions = ["X: imposter(A, B)", "Y: watch(B)"]
    # game.run_actions(actions)

    # game = Game(players=list("ABXY"))
    # actions = ["X: imposter(A, B)", "Y: track(A)"]
    # game.run_actions(actions)


if __name__ == "__main__":
    main()
