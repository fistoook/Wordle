import requests
import pandas as pd
class wordleValidator():
    def __init__(self):
        self.validWordDf = pd.read_csv("wordCSV/valid-words.csv", names = ["Words"])
        self.APIurl = "https://wordotron.com/api/v1/check-word"

    def isValid(self, guess) -> bool:
        # local check first to save them rtts :)
        if (self.validWordDf['Words'].isin([guess.lower()]).any()):
            return True

        # API based check from wordotron.com (FREE!) API :)
        try:
            response = requests.post(self.url, json = {"word": guess.lower()}, timeout = 7)
        except:
            return False # if the api ain't working, your word ain't right! jk. thats why we have the local 11k check first :)

        return response.json()["valid"]