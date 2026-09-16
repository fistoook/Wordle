import json
import os
import sys
import threading
import uuid
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BACKEND_DIRECTORY = Path(__file__).resolve().parent
PROJECT_DIRECTORY = BACKEND_DIRECTORY.parent
FRONTEND_DIRECTORY = PROJECT_DIRECTORY / "forntend"

sys.path.insert(0, str(PROJECT_DIRECTORY))
sys.path.insert(0, str(BACKEND_DIRECTORY))

from backend.wordleGameEngine import (ABSENT, CORRECT, IN_PROGRESS, LOST, PRESENT, WON, wordleGameEngine,)


RESULT_NAMES = {CORRECT: "correct", PRESENT: "present", ABSENT: "absent",}

STATUS_NAMES = {LOST: "lost", IN_PROGRESS: "in_progress",WON: "won",}


class wordleHttpJsonApi:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.games = {} # dictonary of all running games
        self.games_lock = threading.Lock() # prevents two requests from changing the same game simultaneously

        handler = partial(_WordleRequestHandler, api=self, directory=str(FRONTEND_DIRECTORY))
        self.http_server = ThreadingHTTPServer((host, port), handler) # multiple users at once :)
        self.http_server.daemon_threads = True

    def run(self):
        previous_directory = os.getcwd()
        os.chdir(BACKEND_DIRECTORY)
        print(f"Wordle is running at http://{self.host}:{self.port}")

        try: self.http_server.serve_forever()
        finally: self.http_server.server_close(); os.chdir(previous_directory)

    def stop(self):
        self.http_server.shutdown()

    def start_game(self):
        game_id = uuid.uuid4().hex # generate random game id for the frontend to remember, kinda like a cookie
        game = wordleGameEngine(number_of_guesses=6, word_length=5)

        with self.games_lock: self.games[game_id] = game

        return {"gameId": game_id, "wordLength": game.word_length, "maxGuesses": game.number_of_guesses,}

    def submit_guess(self, game_id, guess):
        with self.games_lock:
            game = self.games.get(game_id) # identify the exact game. thats why we userd uuid 

            if (game is None):
                return 404, {"message": "Game not found. Start a new game."}

            if (game.game_status != IN_PROGRESS):
                return 409, {"message": "This game has already finished."}  # <- should not happen(hopefully)

            response = game.handleGuess(guess) # let our game engine handle the guess

        # parse the engine returned tuple. refrence the game engine pwease <3
        response_status = response[0]
        results = response[1]
        attempts_left = response[2]
        game_status = response[3]
        answer = response[5]

        if (response_status == "rejected"): # engine rturned invalid word (wrong length/not found in dictionary API)
            return 200, {"accepted": False, "message": "That word is not valid.", "attemptsLeft": attempts_left, "status": STATUS_NAMES[game_status],}
        body = {"accepted": True, "result": [RESULT_NAMES[result] for result in results], "attemptsLeft": attempts_left,"status": STATUS_NAMES[game_status],}

        # only once the game ends we send the answer
        # if we would always send it, an evil client could potentially
        # dig through the dev tools. hahah, good luck doing that :)
        if (game_status == LOST): body["answer"] = answer

        return 200, body


class _WordleRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, api, **kwargs):
        self.api = api
        super().__init__(*args, **kwargs)

    def do_POST(self):
        path = urlparse(self.path).path

        if (path == "/api/games"):
            # game created
            self.send_json(201, self.api.start_game())
            return

        path_parts = path.strip("/").split("/")
        if (len(path_parts) == 4 and path_parts[:2] == ["api", "games"] and path_parts[3] == "guesses"):
            request_body = self.read_json_body()
            if (request_body is None): return

            guess = request_body.get("guess")
            if (not isinstance(guess, str)):
                self.send_json(400, {"message": "Invalid input"}) # bro just pass a string
                return

            status_code, response_body = self.api.submit_guess(path_parts[2], guess)
            self.send_json(status_code, response_body)
            return

        self.send_json(404, {"message": "something went wrong..."})

    def do_GET(self):
        if (urlparse(self.path).path.startswith("/api/")):
            self.send_json(404, {"message": "something went wrong..."})
            return

        super().do_GET()

    def read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw_body = self.rfile.read(content_length)
            request_body = json.loads(raw_body)
        except (ValueError, json.JSONDecodeError):
            self.send_json(400, {"message": "The request body must be valid JSON."})
            return None

        if (not isinstance(request_body, dict)):
            self.send_json(400, {"message": "The JSON body must be an object."})
            return None

        return request_body

    def send_json(self, status_code, body):
        encoded_body = json.dumps(body).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded_body)))
        self.end_headers()
        self.wfile.write(encoded_body)


if (__name__ == "__main__"):
    wordleHttpJsonApi().run()
