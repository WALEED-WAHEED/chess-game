import pygame as p
import tkinter as tk
from tkinter import messagebox
import os
from chessEngine import GameState, Move

CLIENT_NAME = "Foot Master"
Width = Height = 1080
Dimension = 8
SQ_SIZE = Height // Dimension
MAX_FPS = 15
IMAGES = {}
PIECE_SIZE = 100

def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "images")
    for piece in pieces:
        path = os.path.join(img_dir, piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(path), (PIECE_SIZE, PIECE_SIZE))

def main():
    user = login_window()
    if not user:
        return
    settings = settings_window()
    if settings is None:
        return
    base_seconds, increment_seconds, player_side = settings
    orientationWhiteBottom = (player_side == 'white')
    p.init()
    info = p.display.Info()
    max_fit = max(400, min(info.current_w, info.current_h) - 80)
    board_size = min(1080, max_fit)
    global Width, Height, SQ_SIZE, PIECE_SIZE
    Width = Height = board_size
    SQ_SIZE = Height // Dimension
    PIECE_SIZE = max(60, int(SQ_SIZE * (100/135)))
    screen = p.display.set_mode((Width, Height))
    p.display.set_caption(CLIENT_NAME)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    font = p.font.SysFont(None, 42)
    small_font = p.font.SysFont(None, 24)
    gs = GameState()
    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    validMoves = gs.getValidMoves()
    white_time_ms = int(base_seconds * 1000)
    black_time_ms = int(base_seconds * 1000)
    increment_ms = int(increment_seconds * 1000)
    game_over_text = ""
    move_history = []
    promotion_pending = None
    show_restart_menu = False
    while running:
        dt = clock.tick(MAX_FPS)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not game_over_text and not promotion_pending:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if not orientationWhiteBottom:
                    col = 7 - col
                    row = 7 - row
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = Move(playerClicks[0], playerClicks[1], gs.board)
                    if move in validMoves:
                        for vm in validMoves:
                            if vm == move:
                                move = vm
                                break
                        moved_white = gs.whiteToMove
                        gs.makeMove(move)
                        if moved_white:
                            white_time_ms += increment_ms
                        else:
                            black_time_ms += increment_ms
                        validMoves = gs.getValidMoves()
                        move_history.append(move.getChessNotation())
                        if move.isPawnPromotion:
                            promotion_pending = move
                        else:
                            if len(validMoves) == 0:
                                if gs.isInCheck(gs.whiteToMove):
                                    game_over_text = "Checkmate - " + ("White" if not gs.whiteToMove else "Black") + " wins"
                                else:
                                    game_over_text = "Stalemate"
                                show_restart_menu = True
                    sqSelected = ()
                    playerClicks = []
            elif e.type == p.MOUSEBUTTONDOWN and promotion_pending:
                location = p.mouse.get_pos()
                center_x, center_y = Width//2, Height//2
                piece_size = SQ_SIZE
                start_x = center_x - 2*piece_size
                start_y = center_y - piece_size//2
                if (start_x <= location[0] <= start_x + 4*piece_size and
                    start_y <= location[1] <= start_y + piece_size):
                    click_x = location[0] - start_x
                    choice_idx = click_x // piece_size
                    if 0 <= choice_idx < 4:
                        piece_choices = ['Q', 'R', 'B', 'N']
                        chosen_piece = piece_choices[choice_idx]
                        gs.board[promotion_pending.endRow][promotion_pending.endCol] = promotion_pending.pieceMoved[0] + chosen_piece
                        promotion_pending = None
                        validMoves = gs.getValidMoves()
                        if len(validMoves) == 0:
                            if gs.isInCheck(gs.whiteToMove):
                                game_over_text = "Checkmate - " + ("White" if not gs.whiteToMove else "Black") + " wins"
                            else:
                                game_over_text = "Stalemate"
                            show_restart_menu = True
            elif e.type == p.KEYDOWN:
                if e.key == p.K_u:
                    if len(gs.moveLog) > 0:
                        gs.undoMove()
                        validMoves = gs.getValidMoves()
                        if move_history:
                            move_history.pop()
                        promotion_pending = None
                        game_over_text = ""
                        show_restart_menu = False
                elif e.key == p.K_r or e.key == p.K_n:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    white_time_ms = int(base_seconds * 1000)
                    black_time_ms = int(base_seconds * 1000)
                    move_history = []
                    promotion_pending = None
                    game_over_text = ""
                    show_restart_menu = False
                    sqSelected = ()
                    playerClicks = []
        if not game_over_text:
            if gs.whiteToMove:
                white_time_ms -= dt
                if white_time_ms <= 0:
                    white_time_ms = 0
                    game_over_text = "White out of time - Black wins"
                    show_restart_menu = True
            else:
                black_time_ms -= dt
                if black_time_ms <= 0:
                    black_time_ms = 0
                    game_over_text = "Black out of time - White wins"
                    show_restart_menu = True
        drawGameState(screen, gs, sqSelected, validMoves, orientationWhiteBottom)
        drawMoveHistory(screen, small_font, move_history)
        drawClocks(screen, font, white_time_ms, black_time_ms)
        if promotion_pending:
            drawPromotionMenu(screen, font, orientationWhiteBottom, gs)
        if game_over_text:
            drawGameOver(screen, font, game_over_text)
        if show_restart_menu:
            drawRestartMenu(screen, font)
        p.display.flip()

def drawGameState(screen, gs, sqSelected, validMoves, whiteBottom):
    drawBoard(screen, whiteBottom)
    drawHighlights(screen, sqSelected, validMoves, whiteBottom)
    drawPieces(screen, gs.board, whiteBottom)
    drawLabels(screen, whiteBottom)

def drawBoard(screen, whiteBottom):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(Dimension):
        for c in range(Dimension):
            color = colors[(r+c) % 2]
            dr = r if whiteBottom else 7 - r
            dc = c if whiteBottom else 7 - c
            p.draw.rect(screen, color, p.Rect(dc*SQ_SIZE, dr*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board, whiteBottom):
    for r in range(Dimension):
        for c in range(Dimension):
            piece = board[r][c]
            if piece != "--":
                dr = r if whiteBottom else 7 - r
                dc = c if whiteBottom else 7 - c
                x = dc*SQ_SIZE + (SQ_SIZE - PIECE_SIZE)//2
                y = dr*SQ_SIZE + (SQ_SIZE - PIECE_SIZE)//2
                screen.blit(IMAGES[piece], (x, y))

def drawHighlights(screen, sqSelected, validMoves, whiteBottom):
    if sqSelected == ():
        return
    r, c = sqSelected
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    s.set_alpha(100)
    s.fill(p.Color('yellow'))
    dr = r if whiteBottom else 7 - r
    dc = c if whiteBottom else 7 - c
    screen.blit(s, (dc*SQ_SIZE, dr*SQ_SIZE))
    for m in validMoves:
        if (m.startRow, m.startCol) == (r, c):
            dr2 = m.endRow if whiteBottom else 7 - m.endRow
            dc2 = m.endCol if whiteBottom else 7 - m.endCol
            center = (dc2*SQ_SIZE + SQ_SIZE//2, dr2*SQ_SIZE + SQ_SIZE//2)
            p.draw.circle(screen, p.Color('red'), center, SQ_SIZE//8)

def drawLabels(screen, whiteBottom):
    small = p.font.SysFont(None, 24)
    files = ['a','b','c','d','e','f','g','h']
    ranks = ['1','2','3','4','5','6','7','8']
    for c in range(8):
        fileChar = files[c] if whiteBottom else files[7-c]
        text = small.render(fileChar, True, p.Color('black'))
        screen.blit(text, (c*SQ_SIZE + 4, Height - text.get_height() - 4))
    for r in range(8):
        rankChar = ranks[7-r] if whiteBottom else ranks[r]
        text = small.render(rankChar, True, p.Color('black'))
        screen.blit(text, (4, r*SQ_SIZE + 4))

def drawClocks(screen, font, white_ms, black_ms):
    def fmt(ms):
        total = max(0, ms//1000)
        m = total//60
        s = total%60
        return f"{m:02d}:{s:02d}"
    black_surf = font.render(f"Black: {fmt(black_ms)}", True, p.Color('black'))
    white_surf = font.render(f"White: {fmt(white_ms)}", True, p.Color('black'))
    screen.blit(black_surf, (10, 10))
    screen.blit(white_surf, (10, Height - 10 - white_surf.get_height()))

def drawGameOver(screen, font, text):
    s = p.Surface((Width, Height))
    s.set_alpha(140)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))
    t = font.render(text, True, p.Color('red'))
    rect = t.get_rect(center=(Width//2, Height//2))
    screen.blit(t, rect)

def drawMoveHistory(screen, font, moves):
    x, y = 10, 50
    screen.blit(font.render("Moves:", True, p.Color('black')), (x, y))
    y += 22
    for i, move in enumerate(moves[-8:]):
        text = font.render(f"{i+1}. {move}", True, p.Color('black'))
        screen.blit(text, (x, y))
        y += 20

def drawPromotionMenu(screen, font, whiteBottom, gs):
    s = p.Surface((Width, Height))
    s.set_alpha(200)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))
    center_x, center_y = Width//2, Height//2
    piece_size = SQ_SIZE
    start_x = center_x - 2*piece_size
    start_y = center_y - piece_size//2
    pieces = ['Q', 'R', 'B', 'N']
    for i, piece in enumerate(pieces):
        x = start_x + i*piece_size
        y = start_y
        p.draw.rect(screen, p.Color('lightgray'), p.Rect(x, y, piece_size, piece_size))
        p.draw.rect(screen, p.Color('black'), p.Rect(x, y, piece_size, piece_size), 2)
        piece_color = 'w' if gs.whiteToMove else 'b'
        piece_name = piece_color + piece
        if piece_name in IMAGES:
            piece_img = p.transform.scale(IMAGES[piece_name], (piece_size-10, piece_size-10))
            screen.blit(piece_img, (x+5, y+5))
        label = font.render(piece, True, p.Color('black'))
        label_rect = label.get_rect(center=(x + piece_size//2, y + piece_size + 20))
        screen.blit(label, label_rect)
    inst_text = font.render("Choose promotion piece:", True, p.Color('black'))
    inst_rect = inst_text.get_rect(center=(center_x, center_y - piece_size))
    screen.blit(inst_text, inst_rect)

def drawRestartMenu(screen, font):
    s = p.Surface((Width, Height))
    s.set_alpha(200)
    s.fill(p.Color('white'))
    screen.blit(s, (0, 0))
    center_x, center_y = Width//2, Height//2
    button_width, button_height = 200, 50
    play_again_rect = p.Rect(center_x - button_width//2, center_y - 60, button_width, button_height)
    p.draw.rect(screen, p.Color('lightgreen'), play_again_rect)
    p.draw.rect(screen, p.Color('black'), play_again_rect, 2)
    play_text = font.render("Play Again", True, p.Color('black'))
    screen.blit(play_text, play_text.get_rect(center=play_again_rect.center))
    new_game_rect = p.Rect(center_x - button_width//2, center_y + 10, button_width, button_height)
    p.draw.rect(screen, p.Color('lightblue'), new_game_rect)
    p.draw.rect(screen, p.Color('black'), new_game_rect, 2)
    new_text = font.render("New Game", True, p.Color('black'))
    screen.blit(new_text, new_text.get_rect(center=new_game_rect.center))
    inst_text = font.render("Press R or N for Restart", True, p.Color('black'))
    screen.blit(inst_text, inst_text.get_rect(center=(center_x, center_y + 80)))

def login_window():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "users.csv")
    users = {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('"'):
                    continue
                parts = line.split(':', 1) if ':' in line else line.split(',', 1)
                if len(parts) == 2:
                    users[parts[0].strip()] = parts[1].strip()
    except FileNotFoundError:
        pass
    result = {"user": None}
    root = tk.Tk()
    root.title(f"{CLIENT_NAME} - Login")
    tk.Label(root, text="Username").grid(row=0, column=0)
    tk.Label(root, text="Password").grid(row=1, column=0)
    u = tk.Entry(root)
    pwd = tk.Entry(root, show='*')
    u.grid(row=0, column=1)
    pwd.grid(row=1, column=1)
    def do_login():
        name, pw = u.get().strip(), pwd.get().strip()
        if name in users and users[name] == pw:
            result["user"] = name
            root.destroy()
        else:
            messagebox.showerror("Error", "Invalid username or password")
    def do_register():
        name, pw = u.get().strip(), pwd.get().strip()
        if not name or not pw:
            messagebox.showerror("Error", "Please enter username and password")
            return
        if name in users:
            messagebox.showerror("Error", "User exists")
            return
        users[name] = pw
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"{name}:{pw}\n")
        messagebox.showinfo("OK", "Registered. You can log in now.")
    tk.Button(root, text="Login", command=do_login).grid(row=2, column=0, sticky='we')
    tk.Button(root, text="Register", command=do_register).grid(row=2, column=1, sticky='we')
    root.mainloop()
    return result["user"]

def settings_window():
    result = {"done": False, "base": 180, "inc": 0, "side": 'white'}
    root = tk.Tk()
    root.title(f"{CLIENT_NAME} - Game Settings")
    tk.Label(root, text="Choose Side").pack(anchor='w')
    side_var = tk.StringVar(value='white')
    tk.Radiobutton(root, text='White', variable=side_var, value='white').pack(anchor='w')
    tk.Radiobutton(root, text='Black', variable=side_var, value='black').pack(anchor='w')
    tk.Label(root, text="Time Control").pack(anchor='w', pady=(8,0))
    time_var = tk.StringVar(value='blitz3+0')
    options = [
        ('Bullet 1+0', 'bullet1+0', 60, 0), ('Bullet 2+1', 'bullet2+1', 120, 1),
        ('Blitz 3+0', 'blitz3+0', 180, 0), ('Blitz 3+2', 'blitz3+2', 180, 2),
        ('Blitz 5+0', 'blitz5+0', 300, 0), ('Rapid 15+10', 'rapid15+10', 900, 10),
        ('Rapid 30+0', 'rapid30+0', 1800, 0), ('Classical 60+0', 'class60+0', 3600, 0),
    ]
    radios = []
    for label, key, base, inc in options:
        r = tk.Radiobutton(root, text=label, variable=time_var, value=key)
        r.pack(anchor='w')
        radios.append((r, base, inc))
    def start():
        key = time_var.get()
        base, inc = 180, 0
        for r, b, i in radios:
            if r.cget('value') == key:
                base, inc = b, i
                break
        result["done"] = True
        result["base"] = base
        result["inc"] = inc
        result["side"] = side_var.get()
        root.destroy()
    tk.Button(root, text='Start', command=start).pack(fill='x', pady=(8,0))
    tk.Button(root, text='Cancel', command=root.destroy).pack(fill='x')
    root.mainloop()
    if not result["done"]:
        return None
    return (result["base"], result["inc"], result["side"])

if __name__ == "__main__":
    main()
