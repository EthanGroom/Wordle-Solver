import random

ANSI_RESET = "\u001B[0m" + "\u001B[7m"
ANSI_GREEN = "\u001b[32m" + "\u001B[7m"
ANSI_YELLOW = "\u001B[33m" + "\u001B[7m"


class Menu:
    def __init__(self):
        self.word_list = []
        self.letter_frequencies = {}
        self.word_scores = {}

    def start(self):
        self.create_word_list()
        print("1. Play Wordle\n2. AI plays Wordle")
        user_input = input()
        rand_num = random.randrange(14854)
        if user_input == "1":
            game = WordleGame(self.word_list[rand_num], True, self.word_list)
            game.start()
        elif user_input == "2":
            game = WordleGame(self.word_list[rand_num], False, self.word_list)
            game.start()
        else:
            print("Invalid option")

    def create_word_list(self):
        file = open("words.txt", "r")
        data = file.read()
        self.word_list = data.upper().splitlines()
        print(self.word_list)
        file.close()

        for word in self.word_list:
            for letter in word:
                if letter in self.letter_frequencies:
                    self.letter_frequencies[letter] += 1
                else:
                    self.letter_frequencies[letter] = 1

        for word in self.word_list:
            score = 0
            for letter in word:
                score += self.letter_frequencies[letter]
            self.word_scores[word] = score

        print(self.letter_frequencies)
        print(self.word_scores)
        print(max(zip(self.word_scores.values(), self.word_scores.keys()))[1])


class WordleGame:
    def __init__(self, word, human_player, word_list):
        self.target = word
        self.human_player = human_player
        self.word_list = word_list

    def start(self):
        print("Starting Wordle Game")
        if self.human_player:
            i = 0
            while i < 6:
                print(f"Guess {i + 1}:")
                guess = input().upper()
                if len(guess) != 5 or guess not in self.word_list:
                    print("Invalid guess!")
                    continue
                if guess == self.target:
                    print(f"Solved in {i + 1} guesses!")
                    break
                else:
                    self.check_guess(guess)
                    i += 1
            print(f"Word was {self.target}")

        if not self.human_player:
            pass

    def check_guess(self, guess):
        green = [False, False, False, False, False]
        marked = []
        colors = [ANSI_RESET, ANSI_RESET, ANSI_RESET, ANSI_RESET, ANSI_RESET]
        for count, letter in enumerate(guess):
            if letter is self.target[count]:
                green[count] = True
                marked.append(letter)
                colors[count] = ANSI_GREEN
        for count, letter in enumerate(guess):
            if letter in self.target and not green[count] and self.target.count(letter) > marked.count(letter):
                marked.append(letter)
                colors[count] = ANSI_YELLOW

        for count, letter in enumerate(guess):
            print(colors[count] + letter, end="", flush=True)
        print("\u001B[0m")


if __name__ == "__main__":
    menu = Menu()
    menu.start()
