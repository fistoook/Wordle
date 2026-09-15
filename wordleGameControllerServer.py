import socket
import threading
from wordleGameEngine import wordleGameEngine, CORRECT, PRESENT, ABSENT, LOST, IN_PROGRESS, WON

HOST = '127.0.0.1'
PORT = 4321

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
GREY = "\033[90m"
RESET = "\033[0m"

class wordleServer():
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # use AF_INET for ipv4 and SOCK_STREAM for TCP. love me some handshakes!
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # for easier restart. wihtout this the OS would lock the port when restarting to clear out previous messages
        self.server_socket.bind((HOST, PORT)) # bind that sucker
        self.users_connected = 0 # how else would I know if I am connected? :)

    def runServer(self):
        self.server_socket.listen()
        while True:
            client_socket, client_address = self.server_socket.accept()
            thread = threading.Thread(target = self.handleClient, args = (client_socket, client_address))
            thread.start()

    def handleClient(self, client_socket, client_address):
        print(f"Connected: {client_address}")
        wordle_game = wordleGameEngine(6, 5)
        self.greetClient(client_socket)

        try:
            while True:
                data = client_socket.recv(1024).strip()
                if (not data): break

                message = data.decode()
                response = wordle_game.handleGuess(message)
                response_status = response[0]
                response_results = response[1]
                response_attempts_left = response[2]
                response_game_status = response[3]
                response_guess = response[4]
                response_word = response[5]

                if (response_status == 'rejected'):
                    client_socket.sendall("Invalid input, try again\n".encode())
                    continue

                client_response = self.structureResponse(response_results, response_attempts_left, response_game_status, response_guess, response_word)
                client_socket.sendall(client_response.encode())
                if ((response_game_status == WON) or (response_game_status == LOST)):
                    break

        finally:
            client_socket.close()
            print(f"Disconnected: {client_address}")

    def greetClient(self, socket):
        banner = """
+--------------------+
|      W O R D L E   |
|     guess wisely   |
+--------------------+
""" # love me some banners! you know those ascii gorgeus one to get when using cli tools? they are awesome :)
        socket.sendall(banner.encode())

    def structureResponse(self, results, attempts_left, game_status, guess, word) -> str:
        output = ""
        index = 0
        for element in results:
            if (element == CORRECT):
                output += f"{GREEN}{guess[index]}{RESET}"
            elif (element == PRESENT):
                output += f"{YELLOW}{guess[index]}{RESET}"
            else:
                output += f"{GREY}{guess[index]}{RESET}"
            index += 1

        if (game_status == WON):
            output += f"\nCONGRATS! you got it :)"
        elif (game_status == LOST):
            output += f"\nAhh you are out of attempts, better luck next time!\nThe word was {word}"

        output += '\n'
        return output
