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
            if not self.validateInput(guess): i-=1; continue

            correct = self.handleInput(guess)
            if (correct == self.word_length):
                print(f"CONGRATS")
                return 
            
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
        output = ''
        correct = 0
        for j in range(len(guess)):
            curr = guess[j]
            if (curr == self.word[j]):
                output += f"{GREEN}{curr}{RESET}"
                correct+=1
            elif (curr in self.word):
                output += f"{YELLOW}{curr}{RESET}"
            else:
                output += f"{GREY}{curr}{RESET}"
        print(output)
        
        return correct
