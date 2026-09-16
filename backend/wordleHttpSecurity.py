import json
import socket
import threading
import time
import uuid
from http.server import ThreadingHTTPServer


class HttpRequestError(Exception):
    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class wordleHttpSecurity:
    def __init__(
        self,
        max_games=1000,
        game_ttl_seconds=1800,
        max_body_bytes=1024,
        request_timeout_seconds=10,
        max_connections=50,
        clock=time.monotonic,
    ):
        self.max_games = max_games
        self.game_ttl_seconds = game_ttl_seconds
        self.max_body_bytes = max_body_bytes
        self.request_timeout_seconds = request_timeout_seconds
        self.max_connections = max_connections
        self._clock = clock
        self._games = {}
        self._games_lock = threading.Lock()

    def add_game(self, game):
        now = self._clock()
        with self._games_lock:
            self._remove_expired_games(now)
            if len(self._games) >= self.max_games:
                return None

            game_id = uuid.uuid4().hex
            self._games[game_id] = {
                "game": game,
                "created_at": now,
                "lock": threading.Lock(),
            }
            return game_id

    def get_game(self, game_id):
        now = self._clock()
        with self._games_lock:
            self._remove_expired_games(now)
            return self._games.get(game_id)

    def secure_connection(self, connection):
        connection.settimeout(self.request_timeout_seconds)
        deadline = threading.Timer(
            self.request_timeout_seconds,
            self._close_connection,
            args=(connection,),
        )
        deadline.daemon = True
        deadline.start()
        return deadline

    def read_json_body(self, handler):
        if handler.headers.get("Transfer-Encoding"):
            raise HttpRequestError(400, "Transfer-Encoding is not supported.")

        raw_content_length = handler.headers.get("Content-Length")
        try:
            content_length = int(raw_content_length)
        except (TypeError, ValueError):
            raise HttpRequestError(400, "Content-Length must be a number.")

        if content_length <= 0:
            raise HttpRequestError(400, "The request body cannot be empty.")
        if content_length > self.max_body_bytes:
            raise HttpRequestError(413, "The request body is too large.")

        try:
            raw_body = handler.rfile.read(content_length)
        except TimeoutError:
            raise HttpRequestError(408, "The request body took too long to arrive.")

        if len(raw_body) != content_length:
            raise HttpRequestError(400, "The request body is incomplete.")

        try:
            request_body = json.loads(raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise HttpRequestError(400, "The request body must be valid JSON.")

        if not isinstance(request_body, dict):
            raise HttpRequestError(400, "The JSON body must be an object.")

        return request_body

    def _remove_expired_games(self, now):
        expired_game_ids = [
            game_id
            for game_id, session in self._games.items()
            if now - session["created_at"] >= self.game_ttl_seconds
        ]
        for game_id in expired_game_ids:
            del self._games[game_id]

    @staticmethod
    def _close_connection(connection):
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()


class BoundedThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address, handler, max_connections):
        self._connection_slots = threading.BoundedSemaphore(max_connections)
        super().__init__(server_address, handler)

    def process_request(self, request, client_address):
        if not self._connection_slots.acquire(blocking=False):
            request.close()
            return

        try:
            super().process_request(request, client_address)
        except Exception:
            self._connection_slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._connection_slots.release()
