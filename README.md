# Chess Game (Python + Pygame)

Main application folder. Run the game from **this folder**:

```
pip install -r requirements.txt
python chessMain.py
```

**Test login:** username `test`, password `test` (or use Register).

## Folder structure

```
chess/
├── chessMain.py      # Main game (login, board, moves, clock, GUI)
├── chessEngine.py    # Game state, move rules, check/checkmate
├── images/           # Piece sprites (12 PNG files)
├── users.csv         # Login data (username:password)
├── requirements.txt
└── README.md
```

For full testing steps see **HOW-TO-TEST.md** in the project root.
