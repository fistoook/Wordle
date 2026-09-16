import requests
# scary, I know. but what hid does it just resolve the previous directories path
# so that we can later access files in that directory.
# why not just wirte the path? well beacuse it change from machine to machine!
# so we resolve it dynamically, instead of assigning it realtively
from pathlib import Path
BACKEND_DIRECTORY = Path(__file__).resolve().parent
class wordleValidator():
    def __init__(self):
        valid_words_path = BACKEND_DIRECTORY / "wordCSV" / "valid-words.csv"
        with valid_words_path.open(encoding="utf-8") as valid_words_file:
            self.validWords = {line.strip().lower() for line in valid_words_file if line.strip()}

        self.APIurl = "https://wordotron.com/api/v1/check-word"

    def isValid(self, guess) -> bool:
        # local check first to save them rtts :)
        if (guess.lower() in self.validWords):
            return True

        # API based check from wordotron.com (FREE!) API :)
        try:
            response = requests.post(self.APIurl, json = {"word": guess.lower()}, timeout = 7)
        except:
            return False # if the api ain't working, your word ain't right! jk. thats why we have the local 11k check first :)

        return response.json()["valid"]
