# Chess game state and move logic (GameState, Move, piece movement, check, castling, en passant)

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {
            'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
            'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves
        }
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.enPassantPossible = None
        self.castleRights = {'wks': True, 'wqs': True, 'bks': True, 'bqs': True}
        self.castleRightsLog = [self.castleRights.copy()]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        if move.isCastleMove:
            if move.endCol == 6:
                self.board[move.endRow][5] = self.board[move.endRow][7]
                self.board[move.endRow][7] = "--"
            else:
                self.board[move.endRow][3] = self.board[move.endRow][0]
                self.board[move.endRow][0] = "--"
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enPassantPossible = None
        self.updateCastleRights(move)
        self.castleRightsLog.append(self.castleRights.copy())
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self):
        if len(self.moveLog) == 0:
            return
        move = self.moveLog.pop()
        self.board[move.startRow][move.startCol] = move.pieceMoved
        moved = move.pieceMoved
        if move.isPawnPromotion:
            moved = moved[0] + 'p'
            self.board[move.startRow][move.startCol] = moved
        if move.isEnPassantMove:
            self.board[move.endRow][move.endCol] = "--"
            self.board[move.startRow][move.endCol] = move.pieceCaptured
        else:
            self.board[move.endRow][move.endCol] = move.pieceCaptured
        if moved == 'wK':
            self.whiteKingLocation = (move.startRow, move.startCol)
        elif moved == 'bK':
            self.blackKingLocation = (move.startRow, move.startCol)
        if move.isCastleMove:
            if move.endCol == 6:
                self.board[move.endRow][7] = self.board[move.endRow][5]
                self.board[move.endRow][5] = "--"
            else:
                self.board[move.endRow][0] = self.board[move.endRow][3]
                self.board[move.endRow][3] = "--"
        self.castleRightsLog.pop()
        self.castleRights = self.castleRightsLog[-1].copy()
        self.enPassantPossible = move.enPassantPossibleBefore
        self.whiteToMove = not self.whiteToMove

    def getValidMoves(self):
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == "--" or (piece[0] == 'w') != self.whiteToMove:
                    continue
                self.moveFunctions[piece[1]](r, c, moves)
        self.addCastleMoves(moves)
        legal = []
        for m in moves:
            if m.pieceCaptured and (m.pieceCaptured == 'wK' or m.pieceCaptured == 'bK'):
                continue
            m.enPassantPossibleBefore = self.enPassantPossible
            self.makeMove(m)
            if not self.isInCheck(not self.whiteToMove):
                legal.append(m)
            self.undoMove()
        return legal

    def squareInBounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def getPawnMoves(self, r, c, moves):
        piece = self.board[r][c]
        direction = -1 if piece[0] == 'w' else 1
        startRow = 6 if piece[0] == 'w' else 1
        if self.squareInBounds(r + direction, c) and self.board[r + direction][c] == "--":
            moves.append(Move((r, c), (r + direction, c), self.board))
            if r == startRow and self.board[r + 2*direction][c] == "--":
                moves.append(Move((r, c), (r + 2*direction, c), self.board))
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target != "--" and target[0] != piece[0]:
                moves.append(Move((r, c), (nr, nc), self.board))
        if self.enPassantPossible:
            ep_r, ep_c = self.enPassantPossible
            if (r + direction, c - 1) == (ep_r, ep_c) and self.board[r][c-1] != "--" and self.board[r][c-1][0] != piece[0]:
                moves.append(Move((r, c), (ep_r, ep_c), self.board, isEnPassant=True))
            if (r + direction, c + 1) == (ep_r, ep_c) and self.board[r][c+1] != "--" and self.board[r][c+1][0] != piece[0]:
                moves.append(Move((r, c), (ep_r, ep_c), self.board, isEnPassant=True))

    def getRookMoves(self, r, c, moves):
        self._getSlidingMoves(r, c, moves, [(-1,0),(1,0),(0,-1),(0,1)])
    def getBishopMoves(self, r, c, moves):
        self._getSlidingMoves(r, c, moves, [(-1,-1),(-1,1),(1,-1),(1,1)])
    def getQueenMoves(self, r, c, moves):
        self._getSlidingMoves(r, c, moves, [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])

    def _getSlidingMoves(self, r, c, moves, directions):
        ownColor = self.board[r][c][0]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while self.squareInBounds(nr, nc):
                target = self.board[nr][nc]
                if target == "--":
                    moves.append(Move((r, c), (nr, nc), self.board))
                else:
                    if target[0] != ownColor:
                        moves.append(Move((r, c), (nr, nc), self.board))
                    break
                nr += dr
                nc += dc

    def getKnightMoves(self, r, c, moves):
        ownColor = self.board[r][c][0]
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = r + dr, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target == "--" or target[0] != ownColor:
                moves.append(Move((r, c), (nr, nc), self.board))

    def getKingMoves(self, r, c, moves):
        ownColor = self.board[r][c][0]
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            nr, nc = r + dr, c + dc
            if not self.squareInBounds(nr, nc):
                continue
            target = self.board[nr][nc]
            if target == "--" or target[0] != ownColor:
                moves.append(Move((r, c), (nr, nc), self.board))

    def isInCheck(self, forWhite=None):
        if forWhite is None:
            forWhite = self.whiteToMove
        king_r, king_c = self.whiteKingLocation if forWhite else self.blackKingLocation
        return self.squareAttacked(king_r, king_c, byWhite=not forWhite)

    def squareAttacked(self, r, c, byWhite):
        attackerColor = 'w' if byWhite else 'b'
        dr = -1 if byWhite else 1
        for dc in (-1, 1):
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'p':
                return True
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'N':
                return True
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            rr, cc = r + dr, c + dc
            while self.squareInBounds(rr, cc):
                piece = self.board[rr][cc]
                if piece != "--":
                    if piece[0] == attackerColor and piece[1] in 'BQ':
                        return True
                    break
                rr += dr
                cc += dc
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            rr, cc = r + dr, c + dc
            while self.squareInBounds(rr, cc):
                piece = self.board[rr][cc]
                if piece != "--":
                    if piece[0] == attackerColor and piece[1] in 'RQ':
                        return True
                    break
                rr += dr
                cc += dc
        for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            rr, cc = r + dr, c + dc
            if self.squareInBounds(rr, cc) and self.board[rr][cc] == attackerColor + 'K':
                return True
        return False

    def addCastleMoves(self, moves):
        if self.whiteToMove:
            r = 7
            if not self.isInCheck(True):
                if self.castleRights['wks'] and self.board[r][5] == "--" and self.board[r][6] == "--":
                    if not self.squareAttacked(r, 5, byWhite=False) and not self.squareAttacked(r, 6, byWhite=False):
                        moves.append(Move((r,4),(r,6), self.board, isCastle=True))
                if self.castleRights['wqs'] and self.board[r][1] == "--" and self.board[r][2] == "--" and self.board[r][3] == "--":
                    if not self.squareAttacked(r, 2, byWhite=False) and not self.squareAttacked(r, 3, byWhite=False):
                        moves.append(Move((r,4),(r,2), self.board, isCastle=True))
        else:
            r = 0
            if not self.isInCheck(False):
                if self.castleRights['bks'] and self.board[r][5] == "--" and self.board[r][6] == "--":
                    if not self.squareAttacked(r, 5, byWhite=True) and not self.squareAttacked(r, 6, byWhite=True):
                        moves.append(Move((r,4),(r,6), self.board, isCastle=True))
                if self.castleRights['bqs'] and self.board[r][1] == "--" and self.board[r][2] == "--" and self.board[r][3] == "--":
                    if not self.squareAttacked(r, 2, byWhite=True) and not self.squareAttacked(r, 3, byWhite=True):
                        moves.append(Move((r,4),(r,2), self.board, isCastle=True))

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.castleRights['wks'] = self.castleRights['wqs'] = False
        elif move.pieceMoved == 'bK':
            self.castleRights['bks'] = self.castleRights['bqs'] = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7 and move.startCol == 0: self.castleRights['wqs'] = False
            elif move.startRow == 7 and move.startCol == 7: self.castleRights['wks'] = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0 and move.startCol == 0: self.castleRights['bqs'] = False
            elif move.startRow == 0 and move.startCol == 7: self.castleRights['bks'] = False
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 0: self.castleRights['wqs'] = False
        if move.pieceCaptured == 'wR' and move.endRow == 7 and move.endCol == 7: self.castleRights['wks'] = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 0: self.castleRights['bqs'] = False
        if move.pieceCaptured == 'bR' and move.endRow == 0 and move.endCol == 7: self.castleRights['bks'] = False

class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassant=False, isCastle=False):
        self.startRow, self.startCol = startSq[0], startSq[1]
        self.endRow, self.endCol = endSq[0], endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isEnPassantMove = isEnPassant
        if self.isEnPassantMove:
            self.pieceCaptured = 'bp' if self.pieceMoved[0] == 'w' else 'wp'
        self.isCastleMove = isCastle
        self.isPawnPromotion = (self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7))
        self.enPassantPossibleBefore = None

    def getChessNotation(self):
        return self.colsToFiles[self.startCol] + self.rowsToRanks[self.startRow] + self.colsToFiles[self.endCol] + self.rowsToRanks[self.endRow]

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return (self.startRow, self.startCol, self.endRow, self.endCol) == (other.startRow, other.startCol, other.endRow, other.endCol)
