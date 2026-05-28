from game_state import Game

N0_ACTIONS = [
    "Alexandra: watch(Willie)",
    "Aman: CPR(Nick)",
    "Audrey: mail(Alisa, Willie)",
    "Brandon: hide(Alexandra)",
    "Jason: poison(Henry)",
    "Jon: protect(Audrey)",
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
    "Jon: protect(Aman)",
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
    "Jon: protect(Audrey)",
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
        modifiers={"Henry": "stone"},
    )
    print("----- Night 0 -----")
    game.run_actions(N0_ACTIONS)
    print("----- Night 1 -----")
    game.run_actions(N1_ACTIONS)
    print("----- Night 2 -----")
    game.run_actions(N2_ACTIONS)

    # game = Game(players=list("ABCXYZ"))
    # actions = ["A: track(Y)", "X: loki_bus_drive(A, B)", "B: bus_drive(Z, Z)"]
    # game.run_actions(actions)


if __name__ == "__main__":
    main()
