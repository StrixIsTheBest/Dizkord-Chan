from discordbot.utils.emojis import SPLIT, STOP, ALPHABET, ARROW_LEFT, CHECKMARK, REPEAT, QUESTION

TIMEOUT = 60 * 5

MINIGAMES = ["Blackjack", "Chess", "Connect4", "Flood", "Mastermind", "Hangman", "Quiz", "Scramble"]

QUIZ_CATEGORIES = ["General Knowledge", "Sports", "Films", "Music", "Video Games"]

BLACKJACK_RULES = f"**Blackjack**\n" \
                  f"{ALPHABET['h']} to ask for extra card ('hit').\n" \
                  f"{ALPHABET['s']} to signal that you have enough cards ('stand').\n" \
                  f"{SPLIT} to split your hand when both your cards are of the same rank at the start of the game.\n" \
                  f"{STOP} to end the game (automatically results in loss)."

CHESS_RULES = f"**Chess**\n" \
              f"Click letters and numbers to create your move.\n" \
              f"{STOP} to end the game (automatically results in loss for player who pressed it)."

CONNECT4_RULES = f"**Connect4**\n" \
                 f"Click a number to indicate the column for your coin.\n" \
                 f"{STOP} to end the game (automatically results in loss for player who pressed it)."

HANGMAN_RULES = f"**Hangman**\n" \
                f"Click letters to make your guess.\n" \
                f"{STOP} to end the game (automatically results in loss)."

QUIZ_RULES = f"**Quiz**\n" \
             f"There are 4 categories available: General Knowledge, Sports, Films, Music and Video Games.\n" \
             f"First select your category, then select the right answer for your question.\n" \
             f"{STOP} to end the game (automatically results in loss)."

SCRAMBLE_RULES = f"**Scramble**\n" \
                 f"Unscramble the given word by clicking on the letters in the correct order.\n" \
                 f"{ARROW_LEFT} to undo your last move.\n" \
                 f"{STOP} to end the game (automatically results in loss)."

FLOOD_RULES = f"**Flood**\n" \
              f"Try to get the whole grid to be the same color within the given number of moves, by repeatedly flood-filling the top left corner in different colors.\n" \
              f"Click one of the colors in the reactions to flood-fill the top left corner with that color.\n" \
              f"{STOP} to end the game (automatically results in loss)."

MASTERMIND_RULES = f"**Mastermind**\n" \
                   f"Try to guess the hidden combination of colors. You will be given limited information about each guess you make, enabling you to refine the next guess.\n" \
                   f"{CHECKMARK} to indicate the amount of colors that are in the correct place.\n" \
                   f"{REPEAT} to indicate the amount of colors that are correct but in the wrong place.\n" \
                   f"Click one of the colors in the reactions to make your guess.\n" \
                   f"{ARROW_LEFT} to remove your last added color.\n" \
                   f"{CHECKMARK} to confirm your guess.\n" \
                   f"{STOP} to end the game (automatically results in loss)."

AKINATOR_RULES = f"**Akinator**\n" \
                 f"Think of character and by asking yes/no questions the Akinator will guess who it is. Character can be fictional or real.\n" \
                 f"{ALPHABET['y']} to answer the question with 'yes'.\n" \
                 f"{ALPHABET['n']} to answer the question with 'no'.\n" \
                 f"{QUESTION} if you don't know the answer.\n" \
                 f"{STOP} to end the game."
