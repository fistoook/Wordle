const WORD_LENGTH = 5;
const MAX_GUESSES = 6;
const KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", ["backspace", ..."zxcvbnm", "enter"]];
const STATE_PRIORITY = { absent: 1, present: 2, correct: 3 };

const board = document.querySelector("#board");
const keyboard = document.querySelector("#keyboard");
const message = document.querySelector("#message");
const newGameButton = document.querySelector("#new-game-button");

let gameId;
let currentGuess = "";
let submittedGuesses = [];
let letterStates = {};
let gameStatus = "loading";
let isSubmitting = false;

const gameApi = createHttpGameApi("");

async function startGame() {
    currentGuess = "";
    submittedGuesses = [];
    letterStates = {};
    gameStatus = "loading";
    newGameButton.hidden = true;
    setMessage("Loading game…");
    render();

    try {
        const game = await gameApi.startGame();
        gameId = game.gameId;
        gameStatus = "in_progress";
        setMessage("Guess the five-letter word.");
    } catch (error) {
        gameStatus = "error";
        setMessage(error.message, true);
    }

    render();
}

function handleKey(key) {
    if (gameStatus !== "in_progress" || isSubmitting) return;

    if (key === "enter") {
        submitGuess();
    } else if (key === "backspace") {
        currentGuess = currentGuess.slice(0, -1);
        setMessage("");
        renderBoard();
    } else if (/^[a-z]$/.test(key) && currentGuess.length < WORD_LENGTH) {
        currentGuess += key;
        setMessage("");
        renderBoard();
    }
}

async function submitGuess() {
    if (currentGuess.length !== WORD_LENGTH) {
        setMessage("Enter five letters first.", true);
        return;
    }

    isSubmitting = true;
    setMessage("Checking…");
    renderKeyboard();

    try {
        const response = await gameApi.submitGuess(gameId, currentGuess);

        if (!response.accepted) {
            setMessage(response.message || "That word is not valid.", true);
            return;
        }

        submittedGuesses.push({ word: currentGuess, result: response.result });
        updateLetterStates(currentGuess, response.result);
        currentGuess = "";
        gameStatus = response.status;

        if (gameStatus === "won") {
            setMessage("You got it!");
            newGameButton.hidden = false;
        } else if (gameStatus === "lost") {
            setMessage(`The word was ${response.answer.toUpperCase()}.`);
            newGameButton.hidden = false;
        } else {
            setMessage(`${response.attemptsLeft} guesses left.`);
        }
    } catch (error) {
        setMessage(error.message, true);
    } finally {
        isSubmitting = false;
        render();
    }
}

function updateLetterStates(word, result) {
    result.forEach((state, index) => {
        const letter = word[index];
        const oldPriority = STATE_PRIORITY[letterStates[letter]] || 0;
        if (STATE_PRIORITY[state] > oldPriority) letterStates[letter] = state;
    });
}

function render() {
    renderBoard();
    renderKeyboard();
}

function renderBoard() {
    board.replaceChildren();

    for (let rowIndex = 0; rowIndex < MAX_GUESSES; rowIndex += 1) {
        const row = document.createElement("div");
        row.className = "board-row";
        const submitted = submittedGuesses[rowIndex];
        const word = submitted?.word || (rowIndex === submittedGuesses.length ? currentGuess : "");

        for (let columnIndex = 0; columnIndex < WORD_LENGTH; columnIndex += 1) {
            const tile = document.createElement("div");
            const letter = word[columnIndex] || "";
            const result = submitted?.result[columnIndex];
            tile.className = `tile${letter ? " filled" : ""}${result ? ` ${result}` : ""}`;
            tile.textContent = letter;
            row.append(tile);
        }

        board.append(row);
    }
}

function renderKeyboard() {
    keyboard.replaceChildren();

    KEYBOARD_ROWS.forEach((keys) => {
        const row = document.createElement("div");
        row.className = "keyboard-row";

        for (const key of keys) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `key${key.length > 1 ? " wide" : ""}`;
            button.dataset.key = key;
            button.textContent = key === "backspace" ? "⌫" : key;
            button.disabled = gameStatus !== "in_progress" || isSubmitting;
            if (letterStates[key]) button.classList.add(letterStates[key]);
            row.append(button);
        }

        keyboard.append(row);
    });
}

function setMessage(text, isError = false) {
    message.textContent = text;
    message.classList.toggle("error", isError);
}

keyboard.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-key]");
    if (button) handleKey(button.dataset.key);
});

document.addEventListener("keydown", (event) => {
    const key = event.key.toLowerCase();
    if (key === "enter" || key === "backspace" || /^[a-z]$/.test(key)) {
        event.preventDefault();
        handleKey(key);
    }
});

newGameButton.addEventListener("click", startGame);

function createHttpGameApi(baseUrl) {
    async function request(path, options = {}) {
        const response = await fetch(`${baseUrl}${path}`, {
            headers: { "Content-Type": "application/json" },
            ...options,
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || "The server returned an error.");
        return data;
    }

    return {
        startGame: () => request("/api/games", { method: "POST" }),
        submitGuess: (id, guess) => request(`/api/games/${id}/guesses`, {
            method: "POST",
            body: JSON.stringify({ guess }),
        }),
    };
}

startGame();
