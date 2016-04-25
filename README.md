# Space Tyckiting AI

This is a bot that was created for [Futurice's space tyckiting challenge](http://spacetyckiting.futurice.com/). We got 2nd place in the [Berlin event](http://challonge.com/spacetyckitingberlin). The repository contains different AIs of varying strength. The AI used for the actual matches is *stettin*.

Authors: Balthasar Martin, Carsten Walther, Marvin Bornstein<br>
Idea providers: Dimitri Schmidt, Lukas Wagner, Pascal Lange<br>
Client skeleton written by: Axel Eirola

### Requirements:
* node
* python3
* websocket-client
* numpy
* nose (for running tests)

### Install:
Go into the server directory and execute the following command:

`npm install`

### Execute:
`run.sh` is a convenient script to start a fight between two AIs.
An example command is:

`./run.sh gertrude stettin --verbose`

This starts a server, opens a spectator tab in the browser and starts the clients. *Gertrude* and *stettin* are two of the AIs that can be found in `clients/python/tyckiting_client/ai/`. The script was tested on Ubuntu and OS X.
