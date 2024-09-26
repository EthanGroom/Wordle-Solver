import random
from collections import Counter

ANSI_RESET = "\u001B[0m" + "\u001B[7m"
ANSI_GREEN = "\u001b[32m" + "\u001B[7m"
ANSI_YELLOW = "\u001B[33m" + "\u001B[7m"


class Menu:
    def __init__(self):
        self.word_list = []

    def start(self):
        self.create_word_list()
        print("1. Play Wordle\n2. AI plays Wordle\n3. AI plays every Wordle game")
        user_input = input()
        rand_num = random.randrange(14854)
        if user_input == "1":
            game = WordleGame(self.word_list[rand_num], True, self.word_list)
            game.start()
        elif user_input == "2":
            game = WordleGame(self.word_list[rand_num], False, self.word_list)
            game.start()
        elif user_input == "3":
            solves = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for word in self.word_list:
                game = WordleGame(word, False, self.word_list)
                solve = game.start()
                solves[solve] += 1
            for solve in solves:
                if solve != 0 and solve != 1:
                    print(f"Solved in {solve} moves: {solves[solve]}")
                if solve == 1:
                    print(f"Solved in {solve} move: {solves[solve]}")
                if solve == 0:
                    print(f"\nNo solution: {solves[solve]}")
        else:
            print("Invalid option")

    def create_word_list(self):
        file = open("words.txt", "r")
        data = file.read()
        self.word_list = data.upper().splitlines()
        file.close()


class WordleGame:
    def __init__(self, word, human_player, word_list):
        self.target = word
        self.human_player = human_player
        self.word_list = word_list
        self.letter_frequencies = {}
        self.word_scores = {}
        self.letters_not_in_word = set()
        self.prev_guess = ""
        self.green_letters = ['-'] * 5
        self.yellow_letters = ['-'] * 5
        self.no_more_occurrences = set()

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

            first_guess = max(
                (score, key)
                for score, key in zip(self.word_scores.values(), self.word_scores.keys())
                if len(set(key)) == len(key)
            )[1]

            print(f"Starting guess is: {first_guess}")
            i = 0
            while i < 6:
                print(f"Guess {i + 1}:")
                if i == 0:
                    guess = first_guess
                    self.prev_guess = guess
                else:
                    guess = self.generate_ai_guess()
                    self.prev_guess = guess
                if guess == self.target:
                    print(f"Solved in {i + 1} guesses!")
                    print(f"Word was {self.target}")
                    return i + 1
                else:
                    self.check_guess(guess)
                    i += 1
            print(f"Word was {self.target}")
            return 0

    def check_guess(self, guess):
        green = [False, False, False, False, False]
        marked = []
        colors = [ANSI_RESET, ANSI_RESET, ANSI_RESET, ANSI_RESET, ANSI_RESET]
        for count, letter in enumerate(guess):
            if letter is self.target[count]:
                green[count] = True
                self.green_letters[count] = letter
                marked.append(letter)
                colors[count] = ANSI_GREEN
        for count, letter in enumerate(guess):
            if letter in self.target and not green[count] and self.target.count(letter) > marked.count(letter):
                marked.append(letter)
                colors[count] = ANSI_YELLOW
                self.yellow_letters[count] = letter
            elif letter in self.target and not green[count] and self.target.count(letter) == marked.count(letter):
                self.no_more_occurrences.add(letter)
            elif letter not in self.target:
                self.letters_not_in_word.add(letter)

        for count, letter in enumerate(guess):
            print(colors[count] + letter, end="", flush=True)
        print("\u001B[0m")

    def generate_ai_guess(self) -> str:
        self.word_scores.pop(self.prev_guess)

        count_occurrences = Counter([letter for letter in self.green_letters if letter != '-'])
        count_yellow = Counter([letter for letter in self.yellow_letters if letter != '-'])

        words_to_remove = set()

        yellow_list = [letter for letter in self.yellow_letters if letter != '-']
        green_list = [letter for letter in self.green_letters if letter != '-']
        combined_list = yellow_list + green_list

        for word in list(self.word_scores.keys()):
            remove_word = False

            if any(letter in self.letters_not_in_word for letter in word):
                remove_word = True

            if not remove_word:
                for count, letter in enumerate(word):
                    if self.green_letters[count] != '-' and self.green_letters[count] != letter:
                        remove_word = True
                        break

            if not remove_word:
                word_list = [letter for letter in word]
                for letter in combined_list:
                    if letter in word_list:
                        word_list.remove(letter)
                    else:
                        remove_word = True
                else:
                    for count, letter in enumerate(word):
                        if self.yellow_letters[count] != '-' and self.yellow_letters[count] == letter:
                            remove_word = True
                            break

            if not remove_word:
                word_counter = Counter(word)
                for letter in self.no_more_occurrences:
                    if word_counter[letter] > (count_occurrences[letter] + count_yellow[letter]):
                        remove_word = True
                        break

            if remove_word:
                words_to_remove.add(word)

        for word in words_to_remove:
            self.word_scores.pop(word)

        self.yellow_letters = ['-'] * 5

        return max(
            (score, word)
            for word, score in self.word_scores.items()
        )[1]


if __name__ == "__main__":
    menu = Menu()
    menu.start()
