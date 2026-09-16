import json
from pathlib import Path
from urllib.request import Request, urlopen

BACKEND_DIRECTORY = Path(__file__).resolve().parent
VALID_WORDS_PATH = BACKEND_DIRECTORY / "wordCSV" / "valid-words.csv"
WORD_API_URL = "https://wordotron.com/api/v1/check-word"

with VALID_WORDS_PATH.open(encoding="utf-8") as valid_words_file:
    VALID_WORDS = frozenset(line.strip().lower() for line in valid_words_file if line.strip())


class wordleValidator():
    def __init__(self):
        self.validWords = VALID_WORDS

    def isValid(self, guess) -> bool:
        guess = guess.lower()
        if guess in self.validWords:
            return True

        request = Request(
            WORD_API_URL,
            data=json.dumps({"word": guess}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=7) as response:
                result = json.load(response)
        except (OSError, ValueError):
            return False

        return isinstance(result, dict) and result.get("valid") is True
