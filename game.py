import random
from collections import Counter

ANSI_RESET = "\u001B[0m" + "\u001B[7m"
ANSI_GREEN = "\u001b[32m" + "\u001B[7m"
ANSI_YELLOW = "\u001B[33m" + "\u001B[7m"

ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']


class Menu:
    def __init__(self):
        self.word_list = []
        self.word_scores = {}
        self.letter_frequencies = {}
        self.positional_letter_frequencies = [0] * 130
        self.positional_word_scores = {}

    def start(self):
        self.create_word_list()
        print("1. Play Wordle\n2. AI plays Wordle\n3. AI plays every Wordle game")
        user_input = input()
        rand_num = random.randrange(14854)
        if user_input == "1":
            game = WordleGame(self.word_list[rand_num], True, self.word_list, 0, None, None)
            game.start()
        elif user_input == "2":
            print("Choose heuristic:\n1. Non-positional frequency: always use highest score\n"
                  "2. Non-positional frequency: use highest score with unique letters for first word\n"
                  "3. Non-positional frequency: use highest score with unique letters for first two words\n"
                  "4. Positional frequency: always use highest score\n"
                  "5. Positional frequency: use highest score with unique letters for first word\n"
                  "6. Positional frequency: use highest score with unique letters for first two words\n"
                  "7. Positional frequency: use words with all different letters for first two guesses\n"
                  "8. Positional frequency: use highest score with unique letters for first two words and rescoring\n"
                  "9. Positional frequency: use highest score with all different letters for first two guesses and"
                  "rescoring")
            user_heuristic = input()
            game = WordleGame(self.word_list[rand_num], False, self.word_list, self.word_scores,
                              self.positional_word_scores, user_heuristic)
            game.start()
        elif user_input == "3":
            print("Choose heuristic:\n1. Non-positional frequency: always use highest score\n"
                  "2. Non-positional frequency: use highest score with unique letters for first word\n"
                  "3. Non-positional frequency: use highest score with unique letters for first two words\n"
                  "4. Positional frequency: always use highest score\n"
                  "5. Positional frequency: use highest score with unique letters for first word\n"
                  "6. Positional frequency: use highest score with unique letters for first two words\n"
                  "7. Positional frequency: use words with all different letters for first two guesses"
                  "8. Positional frequency: use highest score with unique letters for first two words and rescoring\n"
                  "9. Positional frequency: use highest score with all different letters for first two guesses and"
                  "rescoring")
            user_heuristic = input()
            solves = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
            for word in self.word_list:
                game = WordleGame(word, False, self.word_list, self.word_scores, self.positional_word_scores,
                                  user_heuristic)
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

        for word in self.word_list:
            for count, letter in enumerate(word):
                if letter in self.letter_frequencies:
                    self.letter_frequencies[letter] += 1
                else:
                    self.letter_frequencies[letter] = 1

                index = ((ALPHABET.index(letter) * 5) + 1) + count
                self.positional_letter_frequencies[index - 1] += 1

        for word in self.word_list:
            score = 0
            positional_score = 0
            for count, letter in enumerate(word):
                # score += self.letter_frequencies[letter]

                score_index = ((ALPHABET.index(letter) * 5) + 1) + count
                positional_score += self.positional_letter_frequencies[score_index - 1]

            self.word_scores[word] = score
            self.positional_word_scores[word] = positional_score


class WordleGame:
    def __init__(self, word, human_player, word_list, word_scores, positional_word_scores, heuristic):
        self.target = word
        self.human_player = human_player
        self.starting_word_list = word_list
        self.heuristic = heuristic
        self.letter_frequencies = {}
        self.word_scores = {}
        self.letters_not_in_word = set()
        self.green_letters = ['-'] * 5
        self.yellow_letters = ['-'] * 5
        self.no_more_occurrences = set()
        self.starting_word_scores = word_scores
        self.starting_positional_word_scores = positional_word_scores
        self.letter_frequencies = {}
        self.positional_letter_frequencies = [0] * 130
        self.first_guess = ""

        self.positional_word_scores = {}
        self.word_scores = {}
        self.word_list = []

    def start(self):
        print("Starting Wordle Game")
        if self.human_player:
            i = 0
            while i < 6:
                print(f"Guess {i + 1}:")
                guess = input().upper()
                if len(guess) != 5 or guess not in self.starting_word_list:
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
            i = 0
            self.word_scores = self.starting_word_scores.copy()
            self.positional_word_scores = self.starting_positional_word_scores.copy()
            self.word_list = self.starting_word_list.copy()
            while i < 6:
                print(f"Guess {i + 1}:")
                self.prune_words()
                guess = self.generate_word(i + 1, self.heuristic)
                if guess == self.target:
                    self.check_guess(guess)
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

    def prune_words(self):
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
            self.positional_word_scores.pop(word)
            self.word_list.remove(word)

        self.yellow_letters = ['-'] * 5

    def rescore(self):
        letter_frequencies = {}
        positional_frequencies = [0] * 130
        positional_scores = {}
        for word in self.word_list:
            for count, letter in enumerate(word):
                if letter in letter_frequencies:
                    letter_frequencies[letter] += 1
                else:
                    letter_frequencies[letter] = 1

                index = ((ALPHABET.index(letter) * 5) + 1) + count
                positional_frequencies[index - 1] += 1

        for word in self.word_list:
            score = 0
            for count, letter in enumerate(word):
                score_index = ((ALPHABET.index(letter) * 5) + 1) + count
                score += positional_frequencies[score_index - 1]

            positional_scores[word] = score

        self.positional_word_scores = positional_scores

    def generate_word(self, try_count, heuristic):
        if heuristic == '1':
            return max(
                (score, word)
                for word, score in self.word_scores.items()
            )[1]
        elif heuristic == '2':
            if try_count == 1:
                return max(
                    (score, key)
                    for score, key in zip(self.word_scores.values(), self.word_scores.keys())
                    if len(set(key)) == len(key)
                )[1]
            else:
                return max(
                    (score, word)
                    for word, score in self.word_scores.items()
                )[1]
        elif heuristic == '3':
            if try_count == 1 or try_count == 2:
                try:
                    return max(
                        (score, key)
                        for score, key in zip(self.word_scores.values(), self.word_scores.keys())
                        if len(set(key)) == len(key)
                    )[1]
                except ValueError:
                    return max(
                        (score, word)
                        for word, score in self.word_scores.items()
                    )[1]
            else:
                return max(
                    (score, word)
                    for word, score in self.word_scores.items()
                )[1]
        elif heuristic == '4':
            return max(
                (score, word)
                for word, score in self.positional_word_scores.items()
            )[1]
        elif heuristic == '5':
            if try_count == 1:
                return max(
                    (score, key)
                    for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                    if len(set(key)) == len(key)
                )[1]
            else:
                return max(
                    (score, word)
                    for word, score in self.positional_word_scores.items()
                )[1]
        elif heuristic == '6':
            if try_count == 1 or try_count == 2:
                try:
                    return max(
                        (score, key)
                        for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                        if len(set(key)) == len(key)
                    )[1]
                except ValueError:
                    return max(
                        (score, word)
                        for word, score in self.positional_word_scores.items()
                    )[1]
            else:
                return max(
                    (score, word)
                    for word, score in self.positional_word_scores.items()
                )[1]
        elif heuristic == '7':
            if try_count == 1:
                self.first_guess = max(
                    (score, key)
                    for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                    if len(set(key)) == len(key)
                )[1]
                return self.first_guess
            elif try_count == 2:
                return max(
                    (score, key)
                    for score, key in zip(self.starting_positional_word_scores.values(),
                                          self.starting_positional_word_scores.keys())
                    if len(set(key)) == len(key) and len(set(key).intersection(set(self.first_guess))) == 0
                )[1]
            else:
                return max(
                    (score, word)
                    for word, score in self.positional_word_scores.items()
                )[1]
        elif heuristic == '8':
            if try_count == 1:
                try:
                    return max(
                        (score, key)
                        for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                        if len(set(key)) == len(key)
                    )[1]
                except ValueError:
                    return max(
                        (score, word)
                        for word, score in self.positional_word_scores.items()
                    )[1]
            elif try_count == 2:
                self.rescore()
                print(self.word_list)
                print(self.positional_word_scores)
                try:
                    return max(
                        (score, key)
                        for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                        if len(set(key)) == len(key)
                    )[1]
                except ValueError:
                    return max(
                        (score, word)
                        for word, score in self.positional_word_scores.items()
                    )[1]
            else:
                self.rescore()
                print(self.word_list)
                print(self.positional_word_scores)
                return max(
                    (score, word)
                    for word, score in self.positional_word_scores.items()
                )[1]
        elif heuristic == '9':
            if try_count == 1:
                self.first_guess = max(
                    (score, key)
                    for score, key in zip(self.positional_word_scores.values(), self.positional_word_scores.keys())
                    if len(set(key)) == len(key)
                )[1]
                return self.first_guess
            elif try_count == 2:
                return max(
                    (score, key)
                    for score, key in zip(self.starting_positional_word_scores.values(),
                                          self.starting_positional_word_scores.keys())
                    if len(set(key)) == len(key) and len(set(key).intersection(set(self.first_guess))) == 0
                )[1]
            else:
                self.rescore()
                return max(
                    (score, word)
                    for word, score in self.positional_word_scores.items()
                )[1]


if __name__ == "__main__":
    menu = Menu()
    menu.start()
