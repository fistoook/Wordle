import random
from pathlib import Path

WORD_BANK_PATH = Path(__file__).resolve().parent / "wordCSV" / "word-bank.csv"

with WORD_BANK_PATH.open(encoding="utf-8") as word_bank_file:
    WORD_BANK = tuple(line.strip() for line in word_bank_file if line.strip())


class wordleGameEngineUtils():
    def pickWord(self) -> str:
        return random.choice(WORD_BANK)
