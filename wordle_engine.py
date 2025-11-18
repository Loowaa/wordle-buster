# wordle_engine.py

from pathlib import Path
from dataclasses import dataclass


def load_word_list(path: str = "words.txt") -> list[str]:
    words: list[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) == 5 and w.isalpha():
                words.append(w)
    return words

WORD_LIST = load_word_list()


@dataclass
class GuessResult:
    word: str     # the guessed word, e.g. "aloud"
    pattern: str  # the pattern string, e.g. "ygbbb"

class WordleSession:
    """
    Represents one run of Wordle Buster.
    Knows the word list and all guesses so far.
    """
    def __init__(self, word_list: list[str]):
        self.word_list = word_list
        self.history: list[GuessResult] = []

    def add_guess(self, word: str, pattern: str) -> None:
        """Add a new guess to the board."""
        self.history.append(GuessResult(word=word, pattern=pattern))

    def get_history_tuples(self) -> list[tuple[str, str]]:
        """Convert GuessResult objects to (word, pattern) tuples for the engine."""
        return [(g.word, g.pattern) for g in self.history]

    def get_candidates(self) -> list[str]:
        """Return remaining candidates based on current history."""
        return filter_candidates(self.word_list, self.get_history_tuples())

COLOR_SYMBOLS = {
    "g": "G",   # later: could use colors / emojis
    "y": "Y",
    "b": ".",
}

def print_board(session: WordleSession) -> None:
    print("\nCurrent board:")
    max_rows = 6
    for i in range(max_rows):
        if i < len(session.history):
            gr = session.history[i]
            letters = " ".join(gr.word.upper())
            symbols = " ".join(COLOR_SYMBOLS[ch] for ch in gr.pattern)
            print(f"{letters}   {symbols}")
        else:
            # empty row
            print("_ _ _ _ _   _ _ _ _ _")
    print()



def score_guess(secret: str, guess: str) -> str:
    """
    Given a secret word and a guess (both 5 letters),
    return a 5-character pattern string with:
      'g' = green  (correct letter, correct position)
      'y' = yellow (correct letter, wrong position)
      'b' = grey/blank (letter not in word in that quantity)
    This matches how actual Wordle scoring works.
    """
    secret = secret.lower()
    guess = guess.lower()
    assert len(secret) == len(guess) == 5

    result = ["b"] * 5  # start with all grey
    secret_chars = list(secret)

    # First pass: mark greens
    for i in range(5):
        if guess[i] == secret_chars[i]:
            result[i] = "g"
            secret_chars[i] = None  # consume this letter

    # Second pass: mark yellows
    for i in range(5):
        if result[i] == "g":
            continue  # already handled
        if guess[i] in secret_chars:
            result[i] = "y"
            # consume one occurrence of that letter
            secret_chars[secret_chars.index(guess[i])] = None

    return "".join(result)


def word_matches_history(candidate: str, history: list[tuple[str, str]]) -> bool:
    """
    history is a list of (guess, pattern) tuples.
    pattern is a 5-char string like 'bgygb'.
    Return True if 'candidate' could be the secret word
    that would produce all those patterns.
    """
    for guess, pattern in history:
        if score_guess(candidate, guess) != pattern:
            return False
    return True


def filter_candidates(word_list: list[str], history: list[tuple[str, str]]) -> list[str]:
    """Return all words in word_list that match the given guess history."""
    return [
        w for w in word_list
        if word_matches_history(w, history)
    ]


def main():
    session = WordleSession(WORD_LIST)

    print("=== Wordle Buster (CLI prototype) ===")
    print("Enter your guesses and color patterns.")
    print("Pattern legend: g = green, y = yellow, b = grey")
    print("Press Enter on an empty guess to quit.\n")

    while True:
        print_board(session)

        guess = input("Guess word (5 letters, blank to exit): ").strip().lower()
        if guess == "":
            break
        if len(guess) != 5 or not guess.isalpha():
            print("  -> Please enter exactly 5 letters.\n")
            continue

        pattern = input("Pattern (5 chars, using g/y/b): ").strip().lower()
        if len(pattern) != 5 or any(ch not in "gyb" for ch in pattern):
            print("  -> Pattern must be 5 characters of g, y, or b (e.g. 'bgygg').\n")
            continue

        session.add_guess(guess, pattern)

        candidates = session.get_candidates()

        print(f"\nRemaining candidates: {len(candidates)}")
        print(candidates[:30], "\n")

    print("Goodbye from Wordle Buster!")


if __name__ == "__main__":
    main()
