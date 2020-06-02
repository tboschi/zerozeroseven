# zerozeroseven

Zerozeroseven is an advanced version of the rock paper scissors game that can be played by more players at the same time.

As in the well-known game, there are three basic moves:
* Load, in which you load your gun.
* Shield, in which you defend yourself from someone else attacking.
* Fire, in which you attack/shoot an another player.

The rules are also simple and for each action they are:
* Load:
  1. You have to load at least once before shooting.
  1. Loading is not cumulative, you always load to 1 bullet.
  1. If someone shoots at you while loading, you loose.
* Shield:
  1. You cannot defend more than three times in a row.
  1. If someone shoots at you while shielding, you do not loose.
* Fire:
  1. You have to have loaded before shooting another player.
  1. Once you shoot, you cannot shoot anymore before loading again.
  1. If someone shoots at you while firing, you loose unless you are shooting at that player.

The last player in game wins.

As in rock rock paper scissors players cast their choice simultaneously, typically chanting before "zero zero seven!".
However, differently from rock paper scissors, this is not purely a game of chance and simple short-term memory can help a player win.


## Client -- Server model

This program is an online implementation of the zero zero seven game, written in python.

It relies on a simple client--server model to connect the players between each other and make decisions.
The client command line version works on python3 with linux.

Run first the server
```bash
python gameserver.py <n>
```
where ```n``` is an optional number of bot players which take choices randomly.

After that run the client
```bash
python userclient.py
```
which connects to the server.
The server runs by default on ```localhost:5000```. To change the port, just modify the python script under the ```main section```.
I will make the choice of address and port more user friendly.

## GUI

There is a functioning GUI version as well, based on [pygame](https://www.pygame.org/wiki/GettingStarted).

If there is a server running somewhere, just run the GUI with
```bash
python userview.py
```
By default it connects to ```localhost:5000```.
A user friendly choice of address will be added soon.
