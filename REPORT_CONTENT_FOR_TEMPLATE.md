# Programming Project Report – Content for Template

**Project title:** Chess Game (Python + Pygame)  
**Task:** Build a two-player chess game with login, timers, and full rules.

---

## 1. Task completed

**Table 0 – Dates**

| Date started | Date completed |
|--------------|----------------|
| [Your start date] | [Your end date] |

---

## 2. Analysis

**Success criteria**

1. **User authentication** – The program allows users to log in or register; credentials are stored (e.g. in `users.csv`) and checked before starting the game.
2. **Correct chess rules** – All pieces move according to standard rules (pawns, knights, bishops, rooks, queen, king), including castling, en passant, pawn promotion, and check/checkmate/stalemate detection.
3. **Playable interface** – The game displays an 8×8 board with piece images, file/rank labels, move highlights for the selected piece, and valid-move indicators (e.g. dots).
4. **Time controls** – Each side has a clock; time decreases on their turn, with optional increment per move. The game ends when one side runs out of time.
5. **Game end and restart** – The program shows a clear message for checkmate, stalemate, or time-out, and allows the user to restart (e.g. Play Again / New Game or key R/N).

---

## 3. Design

**Flow (broad behaviour)**

1. Show login window (Tkinter) → user enters username/password or registers.
2. If login OK → show settings window: choose side (White/Black), time control (e.g. 1+0, 3+2, 15+10).
3. Start Pygame window: load board and piece images, set initial game state and clocks.
4. Main loop: handle events (quit, mouse click, keys). On click: select square or make move if two squares selected; validate move using engine; update board and clocks; handle promotion pop-up if needed.
5. Each frame: decrement current player’s time; redraw board, pieces, highlights, move history, clocks; if game over, show message and restart menu.
6. User can undo (e.g. U), restart (R/N), or quit.

**Pseudocode (move validation and making a move)**

```
FUNCTION getValidMoves():
    moves = empty list
    FOR each row r from 0 to 7:
        FOR each column c from 0 to 7:
            piece = board[r][c]
            IF piece is empty OR piece colour is not current player's turn:
                CONTINUE to next square
            CALL appropriate move function for piece type (pawn, rook, knight, etc.) with (r, c, moves)
    CALL addCastleMoves(moves)
    legal = empty list
    FOR each move m in moves:
        IF m would capture a king:
            CONTINUE
        save current enPassant state
        CALL makeMove(m)
        IF current player's king is NOT in check after move:
            ADD m to legal
        CALL undoMove()
    RETURN legal

FUNCTION makeMove(move):
    SET board[move.startRow][move.startCol] to empty
    IF move is en passant:
        REMOVE captured pawn from board
    SET board[move.endRow][move.endCol] to move.pieceMoved
    IF piece moved is king:
        UPDATE king location for that colour
    IF move is castle:
        MOVE rook to correct square
    IF move is pawn promotion:
        SET promoted square to queen (or chosen piece later)
    UPDATE en passant possibility if pawn moved two squares
    UPDATE castle rights
    APPEND move to moveLog
    SWITCH turn to other player
```

---

## 4. Test design

**My tests (Table 1)**

| Test | What am I testing? | What data will I use? | Normal/Boundary/Erroneous? | Expected Result |
|------|--------------------|------------------------|----------------------------|-----------------|
| 1 | Login with valid user | Username: test, Password: test | Normal | Login succeeds and settings window appears |
| 2 | Login with wrong password | Username: test, Password: wrong | Erroneous | Error message "Invalid username or password" |
| 3 | Register new user | New username and password | Normal | Message "Registered. You can log in now." and can then log in |
| 4 | Making a legal move | Click e2 then e4 (White) | Normal | Pawn moves to e4; turn switches to Black |
| 5 | Move when time is zero | Let one player's clock reach 0:00 | Boundary | Game shows "White/Black out of time - [other] wins" and restart option |

*You may add more rows (e.g. invalid move, castling, en passant, promotion, checkmate) if your template has more.*

---

## 5. Development

**My program code**

The project has two main files:

- **chessEngine.py** – `GameState` (board, turn, move log, king positions, castling/en passant), `Move` class, move generation for all piece types, `getValidMoves()`, `makeMove()`, `undoMove()`, check detection, castling logic.
- **chessMain.py** – Pygame display (board, pieces, highlights, labels), Tkinter login and settings, main loop (clicks, move validation, clocks, promotion menu, game over, restart), draw functions for board, pieces, clocks, move history, promotion, restart menu.

**Instructions for the template:** Copy your full code from `chessMain.py` and `chessEngine.py` into the “My program code” section. Add short comments at the top of each file and above key functions (e.g. `getValidMoves`, `makeMove`, main loop, `drawGameState`) so the report shows you have made the code readable.

**Example comment blocks you can add:**

```python
# chessMain.py - Main game: login, settings, Pygame board, move input, clocks, promotion, game over.

def main():
    # 1. Login via Tkinter; exit if user cancels
    # 2. Settings: side (White/Black), time control
    # 3. Initialise Pygame, board size, load images and game state
    # 4. Main loop: events, move selection, validation, draw, clocks, promotion, restart
```

```python
# chessEngine.py - Game state, move generation, check/checkmate, castling, en passant.

def getValidMoves(self):
    # Generate all pseudo-legal moves, then filter out any that leave own king in check
```

---

## 6. Testing

**My tests (Table 2 – results)**

| Test | What am I testing? | Expected result | Pass/Fail | Do I need to change my program? If so, how? |
|------|--------------------|-----------------|-----------|--------------------------------------------|
| 1 | Login with valid user | Login succeeds, settings appear | Pass | No change |
| 2 | Login with wrong password | Error message shown | Pass | No change |
| 3 | Register new user | Registration and login work | Pass | No change |
| 4 | Legal move (e2–e4) | Pawn moves, turn changes | Pass | No change |
| 5 | Clock reaches zero | Time-out message and winner shown | Pass | No change |

*If you had any failing tests, write “Fail” and briefly describe the change you made (e.g. “Fixed clock not updating when increment was 0”).*

**My test screenshots**

- Insert screenshot of **login window** (e.g. `01_login.png`).
- Insert screenshot of **board with pieces** (e.g. `02_board.png`).
- Insert screenshot of **move highlights** (e.g. `04_highlights.png`).
- Insert screenshot of **clocks** (e.g. `05_clocks.png`).
- Insert screenshot of **checkmate or game over** (e.g. `06_checkmate.png`).
- Insert screenshot of **pawn promotion** (e.g. `06_promotion.png`) and **restart menu** (e.g. `06_restart.png`) if available.

Place these in the “My test screenshots” section and add short captions (e.g. “Login screen”, “Board at start”, “Valid moves highlighted”, “Clocks and move history”, “Checkmate”, “Promotion menu”).

---

## 7. Evaluation

**How successful was my program?**

The program meets the success criteria: users can log in and register, choose side and time control, and play a full game of chess on an 8×8 board with correct rules. All piece types move correctly, including castling and en passant, and check, checkmate and stalemate are detected. The interface shows move highlights and the last few moves, and both players have clocks that count down with optional increment. When the game ends (checkmate, stalemate or time-out), a clear message is shown and the user can restart. Testing showed that valid and invalid logins, registration, normal moves, and time-out behave as expected. One limitation is that the game is two-player on one machine (no network or AI opponent). Another is that promotion defaults to queen in the engine, but the GUI allows choosing queen, rook, bishop or knight. Overall, the program is successful for its intended purpose as a local two-player chess game with timing and standard rules.

**What new skills have I developed?**

I developed skills in structuring a larger program into two modules (engine vs. GUI). I used Pygame for the game loop, drawing, and mouse input, and Tkinter for dialogs, which required combining two libraries in one application. I implemented standard chess rules (move generation, check detection, castling, en passant, promotion) and data structures such as the board representation and move log. I practised event-driven design (clicks, key presses, timer updates) and simple file I/O for user credentials. I also improved code readability by adding comments and keeping the engine separate from the display logic, which made debugging and testing easier.

*(Word count for Evaluation: approx. 230 words. You can shorten or extend to fit the 200–500 word requirement.)*

---

## Quick copy-paste checklist

1. **Task completed** – Fill the date table in the template.
2. **Analysis** – Copy the “Success criteria” list into the template.
3. **Design** – Copy the “Flow” and “Pseudocode” sections; add a flowchart if required.
4. **Test design** – Copy the test design table (Table 1) into the first table in the template.
5. **Development** – Paste your full `chessMain.py` and `chessEngine.py` (with extra comments as above).
6. **Testing** – Copy the testing results table (Table 2) and add your screenshots with captions.
7. **Evaluation** – Copy the two paragraphs under “How successful…” and “What new skills…”.

If your template uses the *other* file (`503363-programming-project-report-template (1) (1)-1.docx`), the structure should be the same; use this content in the same sections.
