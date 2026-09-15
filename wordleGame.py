import pandas as pd
from wordleValidator import wordleValidator

GREEN = "\033[32m"
YELLOW = "\033[33m"
GREY = "\033[90m"
RED = "\033[31m"
RESET = "\033[0m"


class wordleGame():
    def __init__(self, number_of_guesses, word_length):
        self.word = self.pickWord()
        self.number_of_guesses = number_of_guesses
        self.word_length = word_length
        self.validator = wordleValidator()

    def pickWord(self) -> str:
        wordBankDf = pd.read_csv("wordCSV/word-bank.csv", names=['Words'])
        return wordBankDf.sample(1).iloc[0]['Words']

    def getWord(self) -> str:
        return self.word

    def play(self):
        i = 1
        while i <= self.number_of_guesses:
            guess = input("Enter you guess: ")
            if not self.validateInput(guess.lower()): i-=1; continue

            correct = self.handleInput(guess.lower())
            if (correct == self.word_length): print(f"CONGRATS"); return 
            
        print("Out of tries! the word was: ", self.word)

    def validateInput(self, guess) -> bool:
        if (len(guess) != self.word_length):
            print(f"{RED}Invalid input: length does not match. it should be {self.word_length}{RESET}")
            return False
        if (not self.validator.isValid(guess)):
            print(f"{RED}{guess} ain't a word!{RESET}")
            return False
        return True

    def handleInput(self, guess) -> int:
        # build occurence 
        occurence_dict = {}
        for letter in self.word:
            if letter in occurence_dict:
                occurence_dict[letter] += 1
            else:
                occurence_dict[letter] = 1
    
        output = [""] * self.word_length
        correct = 0

        # first pass for those green dopamine hits.
        # this is done to avoid the cases where we set letters as yellow, 
        # and then discover they are later in the word. oopsy :)
        for i in range(len(guess)):
            curr = guess[i]
            if (curr == self.word[i]):
                output[i] = f"{GREEN}{curr}{RESET}"
                occurence_dict[curr] -= 1
                correct += 1

        # second pass for those yellows abnd greys
        for j in range(len(guess)):
            curr = guess[j]
            if (curr == self.word[j]):
                continue
            elif (curr in self.word):
                if occurence_dict[curr] > 0:
                    output[j] = f"{YELLOW}{curr}{RESET}"
                    occurence_dict[curr] -= 1
            else:
                output[j] = f"{GREY}{curr}{RESET}"

        for letter in output:
            print(letter, end='')
        print()

        return correct
