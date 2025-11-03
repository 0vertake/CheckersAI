from game import GameLogic

while True:
    choice = input("Do you want to play with mandatory takes? (y/n): ")
    if choice.lower() == "y":
        must_take = True
        break
    elif choice.lower() == "n":
        must_take = False
        break
    print("Invalid input. Please enter 'y' or 'n'.\n")

print("\nStarting game...")
print("Instructions:")
print("- Click on a piece to select it")
print("- Click on a highlighted square to move")
print("- You are playing as BLUE")
print("- The bot plays as RED")
print()
input("Press Enter to start the game...")

game = GameLogic(must_take)
game.start()
