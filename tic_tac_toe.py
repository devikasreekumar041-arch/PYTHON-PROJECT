# Tic-Tac-Toe Game
# Two Player Console Based Game
# Python Mini Project

def display_board(board):
    print("\n")
    print(" " + board[0] + " | " + board[1] + " | " + board[2])
    print("---|---|---")
    print(" " + board[3] + " | " + board[4] + " | " + board[5])
    print("---|---|---")
    print(" " + board[6] + " | " + board[7] + " | " + board[8])
    print("\n")


def check_winner(board, player):
    winning_combinations = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ]

    for combination in winning_combinations:
        if all(board[i] == player for i in combination):
            return True

    return False


def play_game():
    board = [str(i) for i in range(1, 10)]
    current_player = "X"

    print("\n===== TIC TAC TOE GAME =====")
    print("Player 1: X")
    print("Player 2: O")

    while True:
        display_board(board)

        if current_player == "X":
            print("Player 1's Turn (X)")
        else:
            print("Player 2's Turn (O)")

        choice = input("Enter a position (1-9): ").strip()

        # Input validation
        if choice == "":
            print("Input cannot be empty! Try again.")
            continue

        if not choice.isdigit():
            print("Invalid input! Please enter a number.")
            continue

        position = int(choice)

        if position < 1 or position > 9:
            print("Invalid position! Choose between 1 and 9.")
            continue

        index = position - 1

        if board[index] in ["X", "O"]:
            print("Position already occupied! Try again.")
            continue

        board[index] = current_player

        # Check winner
        if check_winner(board, current_player):
            display_board(board)
            if current_player == "X":
                print("Congratulations! Player 1 (X) Wins!")
            else:
                print("Congratulations! Player 2 (O) Wins!")
            break

        # Check draw
        if all(cell in ["X", "O"] for cell in board):
            display_board(board)
            print("Game Draw!")
            break

        # Change player
        if current_player == "X":
            current_player = "O"
        else:
            current_player = "X"


# Main program with play again option
while True:
    play_game()

    play_again = input("\nDo you want to play again? (yes/no): ").strip().lower()

    if play_again not in ["yes", "y"]:
        print("\nThank you for playing Tic-Tac-Toe!")
        print("Goodbye!")
        break
