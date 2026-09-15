from wordleGame import wordleGame

if __name__ == "__main__":
    game = wordleGame(6, 5)
    print(game.getWord())
    game.play()