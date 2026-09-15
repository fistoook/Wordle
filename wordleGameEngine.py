from wordleValidator import wordleValidator
from wordleGameUtils import wordleGameEngineUtils

LOST = -1
IN_PROGRESS = 0
WON = 1

CORRECT = 10
PRESENT = 11
ABSENT = 12 

class wordleGameEngine():
    def __init__(self, number_of_guesses, word_length):
        self.validator = wordleValidator()
        self.utils = wordleGameEngineUtils()
        self.word = self.utils.pickWord()
        self.number_of_guesses = number_of_guesses
        self.word_length = word_length
        self.attempts_left = number_of_guesses
        self.current_results = None
        self.game_status = IN_PROGRESS

    def handleGuess(self, guess) -> tuple:
        if not self.validateGuess(guess.lower()):
            return ('rejected', [], self.attempts_left, self.game_status, guess, self.word)
        
        self.attempts_left -= 1
        (correct, results) = self.checkGuess(guess.lower())
        self.current_results = results
        if (correct == self.word_length): self.game_status = WON
        elif (self.attempts_left == 0): self.game_status = LOST

        return ('accepted', results, self.attempts_left, self.game_status, guess, self.word)

    def validateGuess(self, guess) -> bool:
        if (len(guess) != self.word_length): return False
        if (not self.validator.isValid(guess)): return False
        return True

    def checkGuess(self, guess) -> int:
        # build occurence 
        occurence_dict = {}
        for letter in self.word:
            if letter in occurence_dict: occurence_dict[letter] += 1
            else: occurence_dict[letter] = 1
    
        results = [""] * self.word_length
        correct = 0

        # first pass for those green dopamine hits.
        # this is done to avoid the cases where we set letters as yellow, 
        # and then discover they are later in the word. oopsy :)
        for i in range(len(guess)):
            curr = guess[i]
            if (curr == self.word[i]):
                results[i] = CORRECT
                occurence_dict[curr] -= 1
                correct += 1

        # second pass for those yellows abnd greys
        for j in range(len(guess)):
            curr = guess[j]
            if (curr == self.word[j]):
                continue
            elif (curr in self.word):
                if occurence_dict[curr] > 0:
                    results[j] = PRESENT
                    occurence_dict[curr] -= 1
                else:
                    results[j] = ABSENT
            else:
                results[j] = ABSENT

        return (correct, results)
