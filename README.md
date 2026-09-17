We all know and love wordle...
So there is no need for any further explanation

what you will find in this repo is this:
1) the backend. this is where the clean and seperated game engine leaves. it contains just the game logic and is really simple and strightforward, making it compatible to any interface you can write such as
2) the frontend. Look, I will be honest, I am not much of a web dev. the html and css you will found is really similar to the ones you will find in the dev tools of the NY times wordle site. the js however, is the one responsible for connecting the pretty ui to the backend. here, I used a really strightforward json API. just passing the needed thing back and forth, engine <-> js.

you will also find a raw tcp socket server implmented in the backend, if you do not want to sping up the web server.

if you wanty to play around, you can just clone the repo and form there you have 3 options:
1) fire up the socket server by running main.py, and the open up a powershell and netcat into localhost:4321 (I like netcat, but use whatever you like). this is for you cli lovers.

2) fire up the web server by runnning WordleHttpJsonAPI.py, and then got to your web browser and type in localhost:8000. this is for you gui lovers.

3) just take the engine, and code whatever interface you feel like. The heck? code the engine as well! It won't take more then an evening if you have some programming background. and it fun! you can always take inspration from here, or anywhere you like!