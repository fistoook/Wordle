import pandas as pd

class wordleGameEngineUtils():
    def pickWord(self) -> str:
        wordBankDf = pd.read_csv("wordCSV/word-bank.csv", names=['Words'])
        return wordBankDf.sample(1).iloc[0]['Words']