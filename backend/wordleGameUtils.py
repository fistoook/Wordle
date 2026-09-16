import random
from pathlib import Path

WORD_BANK_PATH = Path(__file__).resolve().parent / "wordCSV" / "word-bank.csv"

class wordleGameEngineUtils():
    def pickWord(self) -> str:
        with WORD_BANK_PATH.open(encoding="utf-8") as word_bank_file:
            words = [line.strip() for line in word_bank_file if line.strip()]

        return random.choice(words)
