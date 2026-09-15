import requests

class wordleValidator():
    def isValid(self, guess) -> bool:
        url = f"https://wordotron.com/api/v1/check-word"
        response = requests.post(
            url,
            json={"word": guess},
            timeout=5
        )

        return response.json()["valid"]