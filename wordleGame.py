import pandas as pd

GREEN = "\033[32m"
YELLOW = "\033[33m"
GREY = "\033[90m"
RESET = "\033[0m"

class wordleGame():
    def __init__(self, number_of_guesses):
        self.word = self.pickWord()
        self.number_of_guesses = number_of_guesses

    def pickWord(self) -> str:
        wordBankDf = pd.read_csv("word-bank.csv", names=['Words'])
        return wordBankDf.sample(1).iloc[0]['Words']

    def getWord(self) -> str:
        return self.word

    def play(self):
        for i in range(self.number_of_guesses):
            guess = input("Enter you guess: ")
            output = ''
            if (len(guess) == 5):
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
                if (correct == 5):
                    print("Correct!")
                    return
            else:
                print("Invalid input length")
        print("Out of tries! the word was: ", self.word)

