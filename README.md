# Quarto Simulator and AI Implementations

This repo is part of my Honours research project. 

Quarto is a two-player strategy board game that involves placing pieces on a 4x4 board.
The pieces have different attributes, such as size, color, shape, and hollow or solid, and the goal is to place a piece that forms a line of four pieces with at least one common attribute. A unique aspect to this game is not only do you decide where to place your piece, but you also decide which piece the opponents has to place next. This process repeats until a winner is determined, as the first person to get 4 in a row of any feature, i.e. 4 short pieces or 4 squares.

Here is a useful link explaining the rules of the game: https://www.ultraboardgames.com/quarto/game-rules.php

______________________
## QUARTO SIMULATOR GUIDE
____

#### Bit representation (from left to right)
| N^th^ Bit |   0   |   1   |
|-----------|-------|-------|
| 1 | dark | light |
| 2 | round | square |
| 3 | short | tall |
| 4 | hollow | solid |

#### Piece Representation
| VALUE | BINARY |
|-------|--------|
| 0 | 0000 | 
| 1 | 0001 |
| 2 | 0010 |
| 3 | 0011 |
| 4| 0100|
| 5| 0101|
| 6| 0110|
| 7| 0111|
| 8| 1000|
| 9| 1001|
| 10| 1010|
| 11| 1011|
| 12| 1100|
| 13| 1101|
| 14| 1110|
| 15| 1111|
| 16| NONE|

#### What does 16 represent?

For pieces, 16 denotes the null piece which is assigned to the current piece when there isn't a current piece selected.
In the case of board positions, 16 denotes an empty cell. The reason for using 0 to 15 to represent the pieces is to get the 4-bit piece representation.

#### Playing a game

To play a game, you need to pick two agents that match the superclass of a generic Quarto agent and then call the play method. See below:
```py
from quarto import *
import quarto_agents as qagents

game = QuartoGame(qagents.HumanPlayer(), qagents.RandomQuartoAgent(), gui_mode=True, bin_mode=True)
game.playRandomFirst()
#game.play()
```

There are currently two available premade agents: the human player agent which allows people to play by inputting moves, and a random agent which just selects random legal moves. You have the option of calling play() or playRandomFirst(). playRandomFirst() will play the first move (hence the first player's move) randomly, which involves randomly selecting a piece for Player 2. This is because that first move isn't really important and doesn't affect the game whatsoever.

gui_mode set to True shows a visual board after every move played.
bin_mode set to True will show the pieces in binary form. Only works if gui_mode=True.

#### Creating your own agent

It is very simple to create your own agent by means of the API provided. Just inherit from the GenericQuartoAgent and override the two methods provided.
The game information received in those two methods is called quartoGameState. This is the structure of that data:
```
[
    current quarto board (4x4 numpy array),
    current piece (integer),
    available pieces (set of integers),
    available positions (set of integers)
]
```
You can reference the game state data structure like an array to get the appropriate data. Check with the quarto class getGameState() method to make sure you are receiving the correct information.

After creating your agent and overriding those methods, just put your agent as an argument in the initialization of a quarto game.

