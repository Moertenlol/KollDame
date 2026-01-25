import pygame
from PIL import Image
import random
import sys
import os
import ollama
from ollamainteract import format_ai_move
from Button import Button
from homemadeai import select_best_move, rate_move
pygame.init()

# KI Variable Area


# Preset Bereich
turnAfterCapture = False  # Track whether the current turn is part of a capture sequence
assetpath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'assets'))
base_font = pygame.font.Font(None, 32) 
display = pygame.display.Info()
screen = pygame.display.set_mode((display.current_w, display.current_h - 60), 0,0,0)
pygame.display.set_caption("Dame")
pygame.display.set_icon(pygame.image.load(os.path.join(assetpath, 'icon.jpg')))
clock = pygame.time.Clock() 
screen.fill((255,255,255))
pygame.display.flip()
gamewidth = display.current_h - 300
rows = 8
cols = 8
boardedgefromleft = (display.current_w - gamewidth) // 2
boardedgefromtop = (display.current_h - gamewidth) // 2
capturingPiece = None  # Track the piece that just captured
highlightedPiece = None
currMove = 'Green'
playingas = '' #MERKEN DAS SCHWARZ WARUM AUCH IMMER ALS ERSTES DRAN IST NICHT VERGESSEN IDK WIE LANGE NOCH 
playingagainstai = False
enemyai = "llama3.2"
enemyselected = False
aimoverequested = False
colorontop = "Red"
score_list = []

# Getter Bereich


tempred = Image.open(os.path.join(assetpath, 'red.png'))
red = tempred.resize((gamewidth // rows, gamewidth // cols))
red.save(os.path.join(assetpath, "newred.png"))
red = pygame.image.load(os.path.join(assetpath, "newred.png"))
tempgreen = Image.open(os.path.join(assetpath, 'green.png'))
green = tempgreen.resize((gamewidth // rows, gamewidth // cols))
green.save(os.path.join(assetpath, "newgreen.png"))
green = pygame.image.load(os.path.join(assetpath, "newgreen.png"))
tempreddame = Image.open(os.path.join(assetpath, 'reddame.png'))
reddame = tempreddame.resize((gamewidth // rows, gamewidth // cols))
reddame.save(os.path.join(assetpath, "newreddame.png"))
reddame = pygame.image.load(os.path.join(assetpath, "newreddame.png"))
tempgreendame = Image.open(os.path.join(assetpath, 'greendame.png'))
greendame = tempgreendame.resize((gamewidth // rows, gamewidth // cols))
greendame.save(os.path.join(assetpath, "newgreendame.png"))
greendame = pygame.image.load(os.path.join(assetpath, "newgreendame.png"))


# main
    
def onexit():
    global assetpath
    os.remove(os.path.join(assetpath, "newred.png"))
    os.remove(os.path.join(assetpath, "newgreen.png"))
    os.remove(os.path.join(assetpath, "newreddame.png"))
    os.remove(os.path.join(assetpath, "newgreendame.png"))


class Gridspot:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = int(row * width + boardedgefromleft)
        self.y = int(col * width + boardedgefromtop)
        self.colour = (255,255,255)
        self.piece = None

    def draw(self, screen):
        """
        Draws the Tile and piece on the screen.
        Args:
            screen: The pygame screen to draw on.
        """
        pygame.draw.rect(screen, self.colour, (self.x, self.y, gamewidth / rows, gamewidth / cols))
        if self.piece:
            screen.blit(self.piece.image, (self.x, self.y))

def draw_board(screen, boardgrid, rows, width):
    """
    Draws the entire board on the screen.
    Agrs:
        screen: The pygame screen to draw on.
        boardgrid: The grid representing the board state.
        rows: Number of rows in the board.
        width: Width of the board.
    """
    for row in boardgrid:
        for spot in row:
            spot.draw(screen)
    draw_board_grid(screen, rows, width)
    draw_letters_and_numbers(screen, rows, width)
    pygame.display.update()

def make_board_grid(rows, cols, width):
    """
    Creates the initial board grid with pieces in starting positions.
    Args:
        rows: Number of rows in the board.
        cols: Number of columns in the board.
        width: Width of the board.
    """
    boardgrid = []
    gap = width // rows
    count = 0
    for i in range(rows):
        boardgrid.append([])
        for j in range(cols):
            gridspot = Gridspot(j, i, gap)
            if (i - j) % 2 == 1:
                gridspot.colour = (0, 0, 0)
            if ((i + j) % 2 == 1) and (i < 3):
                gridspot.piece = Piece("Red")
                gridspot.piece.type = "MAN"  # Set type for regular pieces
            elif ((i + j) % 2 == 1) and i > 4:
                gridspot.piece = Piece("Green")
                gridspot.piece.type = "MAN"  # Set type for regular pieces
            count += 1
            boardgrid[i].append(gridspot)
    return boardgrid

def draw_board_grid(screen, rows, width):
    """
    Draws the grid lines on the board.
    Args:
        screen: The pygame screen to draw on.
        rows: Number of rows in the board.
        width: Width of the board.
    """
    gap = width // rows
    for i in range(rows+1):
        pygame.draw.line(screen, (0,0,0), (boardedgefromleft, i * gap + boardedgefromtop), (width + boardedgefromleft -5, i * gap +boardedgefromtop ))
        for j in range(cols+1):
            pygame.draw.line(screen, (0,0,0), (j * gap + boardedgefromleft, boardedgefromtop), (j * gap + boardedgefromleft , width + boardedgefromtop -5))

def draw_letters_and_numbers(screen, rows, width):
    """
    Draws the letters and numbers around the board for notation.
    Args:
        screen: The pygame screen to draw on.
        rows: Number of rows in the board.
        width: Width of the board.
    """
    global playingas 
    gap = width // rows
    font = pygame.font.SysFont("Times New Roman" , 36)
    if playingas == "Red":
        letters = ['a','b','c','d','e','f','g','h']
        numbers = ['8','7','6','5','4','3','2','1']
    else:
        letters = ['h','g','f','e','d','c','b','a']
        numbers = ['1','2','3','4','5','6','7','8']
    for i in range(rows):
        letter_surf = font.render(letters[i], True, (0,0,0))
        screen.blit(letter_surf, (boardedgefromleft + i * gap + gap // 2 - letter_surf.get_width() // 2, boardedgefromtop + width + 5))
        number_surf = font.render(numbers[i], True, (0,0,0))
        screen.blit(number_surf, (boardedgefromleft -36, boardedgefromtop + i * gap + gap // 2 - number_surf.get_height() // 2))

class Piece:
    def __init__(self, team):
        self.team = team
        if self.team=="Red": self.image = red  
        else: self.image = green
        self.type = "MAN"

    def project(self, x, y):
        """
        Draws the piece at the given coordinates.
        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        screen.blit(self.image, (x + boardedgefromleft,y + boardedgefromtop))

    def set_type(self, type):
        """
        Sets Piece type
        Args:
            type: Type of the piece
        """
        self.type = type
        
    def get_type(self):
        """
        Gets Piece type
        """
        return self.type


def get_board_grid_pos(rows, width):
    """
    Gets the board grid position based on mouse click.
    Args:
        rows: Number of rows in the board.
        width: Width of the board.
    """
    gap = width//rows
    spot = pygame.mouse.get_pos()
    spot = list(spot)
    spot[0] -= boardedgefromleft
    spot[1] -= boardedgefromtop
    spot = tuple(spot)
    RowX,RowY = spot
    Row = RowX//gap 
    Col = RowY//gap
    if Row >= rows or Col >= cols or Row < 0 or Col < 0:
        return None
    else:
        return (Col,Row)

def reset_colours(boardgrid, node):
    """
    Resets the colours of the board grid after a move.
    Args:
        boardgrid: The grid representing the board state.
        node: The position to reset colours from.
    """
    if node:
        captures, moves = generate_potential_moves(node, boardgrid)  # Unpack captures and moves
        positions = captures + moves  # Combine captures and moves into a single list
        positions.append(node)  # Add the current node to the list

        for colouredNodes in positions:
            posX, posY = colouredNodes
            boardgrid[posX][posY].colour = (0, 0, 0) if (posX - posY) % 2 == 1 else (255, 255, 255)

def highlight_potential_moves(piecePosition, boardgrid):
    """
    Highlights potential moves for a selected piece.
    Args:
        piecePosition: The position of the selected piece.
        boardgrid: The grid representing the board state.
    """
    global turnAfterCapture
    captures, moves = generate_potential_moves(piecePosition, boardgrid)
    if turnAfterCapture or captures:  # Highlight only capturing moves if in a capture sequence or captures are available
        for position in captures:
            Column, Row = position
            boardgrid[Column][Row].colour = (75, 250, 240)
    else:
        # Highlight both capturing and regular moves during a normal turn
        for position in captures:
            Column, Row = position
            boardgrid[Column][Row].colour = (75, 250, 240)
        for position in moves:
            Column, Row = position
            boardgrid[Column][Row].colour = (75, 250, 240)

def opposite(team):
    """
    Returns the opposite team color.
    Args:
        team: Team color.
    """
    return "Red" if team=="Green" else "Green"

def generate_potential_moves(nodePosition, boardgrid):
    """
    Generates potential moves and captures for a piece at the given position.
    Args:
        nodePosition: The position of the piece.
        boardgrid: The grid representing the board state.
    """
    global colorontop, currMove
    checker = lambda x, y: 0 <= x + y < 8  # Ensure the position is within bounds
    captures = []
    moves = []
    column, row = nodePosition
    if boardgrid[column][row].piece:
        piece = boardgrid[column][row].piece
        if piece.get_type() == 'Dame':
            # Dame (king) can move in all directions
            vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]
        else:
            # Regular pieces can only move forward
            vectors = [[1, -1], [1, 1]] if piece.team == colorontop else [[-1, -1], [-1, 1]]
        for vector in vectors:
            columnVector, rowVector = vector
            newColumn = column + columnVector
            newRow = row + rowVector
            if checker(columnVector, column) and checker(rowVector, row) and 0 <= newColumn < 8 and 0 <= newRow < 8:
                if not boardgrid[newColumn][newRow].piece:
                    # Add to regular moves if the position is empty
                    moves.append((newColumn, newRow))
                    
                elif boardgrid[newColumn][newRow].piece and boardgrid[newColumn][newRow].piece.team == opposite(piece.team):
                    # Check for a jump over an opponent's piece
                    jumpColumn = column + 2 * columnVector
                    jumpRow = row + 2 * rowVector
                    if 0 <= jumpColumn < 8 and 0 <= jumpRow < 8:  # Ensure landing spot is within bounds
                        if not boardgrid[jumpColumn][jumpRow].piece:
                            # Add to captures only if the landing spot is empty
                            captures.append((jumpColumn, jumpRow))
    return captures, moves

def analyze_board_state(boardgrid):
    """
    Analyzes the board state and returns a 2D list representation.
    Args:
        boardgrid: The grid representing the board state.
    """
    board_state = []
    for row in boardgrid:
        board_row = []
        for spot in row:
            if spot.piece:
                if spot.piece.team == colorontop:
                    if spot.piece.get_type() == 'Dame':
                        board_row.append(10)  # Ai Dame
                    else:
                        board_row.append(1)
                else:
                    if spot.piece.get_type() == 'Dame':
                        board_row.append(20)  # player Dame
                    else:
                        board_row.append(2)
            else:
                board_row.append(0)
        board_state.append(board_row)
    return board_state
"""
Error with locating opssible moves row col error
"""
def highlight(ClickedNode, boardgrid, OldHighlight, currMove):
    """
    Highlights the selected piece and its potential moves.
    Args:
        ClickedNode: The position of the clicked piece.
        boardgrid: The grid representing the board state.
        OldHighlight: The previously highlighted piece position.
        currMove: The current player's turn.
    """
    Column, Row = ClickedNode
    if boardgrid[Column][Row].piece and boardgrid[Column][Row].piece.team == currMove:
        if OldHighlight:
            reset_colours(boardgrid, OldHighlight)  # Reset the old highlight
        highlight_potential_moves(ClickedNode, boardgrid)  # Highlight potential moves
        return (Column, Row)  # Update the highlighted piece
    return OldHighlight  # Return the old highlight if the piece doesn't belong to the current player

def move(boardgrid, piecePosition, newPosition):
    """
    Moves a piece from its current position to a new position.
    Args:
        boardgrid: The grid representing the board state.
        piecePosition: The current position of the piece.
        newPosition: The new position to move the piece to.
    """
    global capturingPiece  # Use the global capturingPiece variable
    reset_colours(boardgrid, piecePosition)
    newColumn, newRow = newPosition
    oldColumn, oldRow = piecePosition

    piece = boardgrid[oldColumn][oldRow].piece
    boardgrid[newColumn][newRow].piece = piece
    boardgrid[oldColumn][oldRow].piece = None

    if newColumn == 7 and boardgrid[newColumn][newRow].piece.team == colorontop:
        boardgrid[newColumn][newRow].piece.set_type('Dame')
        if colorontop == "Red":
            boardgrid[newColumn][newRow].piece.image = reddame
        else:
            boardgrid[newColumn][newRow].piece.image = greendame
    if newColumn == 0 and boardgrid[newColumn][newRow].piece.team != colorontop:
        boardgrid[newColumn][newRow].piece.set_type('Dame')
        if colorontop == "Red":
            boardgrid[newColumn][newRow].piece.image = greendame
        else:
            boardgrid[newColumn][newRow].piece.image = reddame

    if abs(newColumn - oldColumn) == 2 or abs(newRow - oldRow) == 2:
        # A capture occurred
        boardgrid[int((newColumn + oldColumn) / 2)][int((newRow + oldRow) / 2)].piece = None
        capturingPiece = (newColumn, newRow)  # Update capturingPiece to the new position
        return boardgrid[newColumn][newRow].piece.team

    capturingPiece = None  # Reset capturingPiece if no capture occurred
    return opposite(boardgrid[newColumn][newRow].piece.team)

def get_all_capturing_pieces(currMove, boardgrid):
    """
    Returns a list of all pieces that can make capturing moves.
    Args:
        currMove: The current player's turn.
        boardgrid: The grid representing the board state.
    """
    capturingPieces = []
    for rowIndex, row in enumerate(boardgrid):
        for colIndex, spot in enumerate(row):
            if spot.piece and spot.piece.team == currMove:
                captures, _ = generate_potential_moves((rowIndex, colIndex), boardgrid)
                if captures:
                    capturingPieces.append((rowIndex, colIndex))
    return capturingPieces

def position_to_notation(row, col, colorontop):
    """
    Transform board coordinates to notation based on perspective.
    Args:        
        row: Row index.
        col: Column index.
        colorontop: The color on top of the board.
    """
    letters = 'abcdefgh'
    if colorontop == "Green":
        # Red's perspective (top to bottom)
        return f"{letters[col]}{8 - row}"
    else:
        # Green's perspective (bottom to top)
        return f"{letters[7 - col]}{row + 1}"

def notation_to_position(row, col, colorontop):
    """
    Transform notation to board coordinates based on perspective.
    Args:
        row: Row notation.
        col: Column notation.
        colorontop: The color on top of the board.
    """
    letters = 'abcdefgh'
    if colorontop == "Green":
        col = letters.index(col)
        row = 8 - int(row)  # Convert row number to 0-based index
    else:
        col = 7 - letters.index(col)
        row = int(row) - 1  # Convert row number to 0-based index
    return (col, row)

def generate_legal_moves(currMove, boardgrid):
    """
    Generates all legal moves for the current player.
    Returns a list of legal move notations.
    Notation format: e3-d4 or e3-c5 (for captures)
    Args:
        currMove: The current player's turn.
        boardgrid: The grid representing the board state.
    """
    global colorontop
    legal_captures = []
    legal_moves = []

    for row_index, row in enumerate(boardgrid):
        for col_index, spot in enumerate(row):
            if spot.piece and spot.piece.team == currMove:
                captures, moves = generate_potential_moves((row_index, col_index), boardgrid)

                # Add captures to the legal captures list
                for capture in captures:
                    start_pos = position_to_notation(row_index, col_index, colorontop)
                    end_pos = position_to_notation(capture[0], capture[1], colorontop)
                    legal_captures.append(f"{start_pos}-{end_pos}")

                # Add regular moves to the legal moves list
                for move in moves:
                    start_pos = position_to_notation(row_index, col_index, colorontop)
                    end_pos = position_to_notation(move[0], move[1], colorontop)
                    legal_moves.append(f"{start_pos}-{end_pos}")

    # If captures are available, only return captures
    if legal_captures:
        return legal_captures

    # Otherwise, return regular moves
    return legal_moves

# Helper function to validate moves and captures
def is_valid_move(start, end, boardgrid):
    """
    Check if a move from start to end is valid.
    Args:
        start: Starting position (row, col).
        end: Ending position (row, col).
        boardgrid: The grid representing the board state.
    """
    start_row, start_col = start
    end_row, end_col = end

    # Ensure the start and end positions are within bounds
    if not (0 <= start_row < len(boardgrid) and 0 <= start_col < len(boardgrid[0])):
        return False
    if not (0 <= end_row < len(boardgrid) and 0 <= end_col < len(boardgrid[0])):
        return False

    # Ensure the start position has a piece
    if not boardgrid[start_row][start_col].piece:
        return False

    # Ensure the end position is empty
    if boardgrid[end_row][end_col].piece:
        return False

    return True

def check_win_by_capture(boardgrid):
    """
    Checks if a player has won by capturing all opponent pieces.
    Args:
        boardgrid: The grid representing the board state.
    """
    redpieces = 0
    greenpieces = 0
    for row in boardgrid:
        for spot in row:
            if spot.piece:
                if spot.piece.team == "Red":
                    redpieces +=1
                else:
                    greenpieces +=1
    if redpieces ==0:
        return "Green"
    elif greenpieces ==0:
        return "Red"
    else:
        return None
    
def check_win_by_stalemate(boardgrid, currMove):
    """
    Checks if a player has won by stalemate (no legal moves).
    Args:
        boardgrid: The grid representing the board state.
        currMove: The current player's turn.
    """
    for rowIndex, row in enumerate(boardgrid):
        for colIndex, spot in enumerate(row):
            if spot.piece and spot.piece.team == currMove:
                captures, moves = generate_potential_moves((rowIndex, colIndex), boardgrid)
                if captures or moves:
                    return None  # Found a piece with legal moves
    return opposite(currMove)  # No legal moves found, opponent wins

def end_check(grid, currMove):
    """
    Checks for gameending conditions and handles game termination.
    Args:
        grid: The grid representing the board state.
        currMove: The current player's turn.
    """
    checkwinbycaptureresult = check_win_by_capture(grid)
    checkwinbystalemateresult = check_win_by_stalemate(grid, currMove)
    if checkwinbycaptureresult or checkwinbystalemateresult:
        winner = checkwinbycaptureresult if checkwinbycaptureresult else checkwinbystalemateresult
        loser = opposite(winner)
        global playingagainstai, enemyai, score_list
        if playingagainstai and enemyai == "llama3.2":
            average_score = sum(score_list) / len(score_list)
            print(f"Average move score for the AI: {average_score}")
        resultboard_create(winner, loser)
        pygame.time.delay(10000)
        onexit()
        pygame.quit()
        sys.exit()

def player_color_selection_screen_create():
    """
    Creates the player color selection screen.
    """
    # create Checkers Header
    text = "Checkers"
    headerfont = pygame.font.SysFont("Times New Roman", 72)
    header = headerfont.render(text, True, (0,0,0))
    screen.blit(header, (display.current_w // 2 - header.get_width() // 2, 100))
    text = "Select your color:"
    subheaderfont = pygame.font.SysFont("Times New Roman", 48)
    subheader = subheaderfont.render(text, True, (0,0,0))
    screen.blit(subheader, (display.current_w // 2 - subheader.get_width() // 2, display.current_h // 2 -150))
    global playingas
    global playerredoption
    playerredoption = Button((200,200,0),display.current_w // 2 - 450, display.current_h // 2-50, 300, 100, "White Player", 36)
    playerredoption.draw(screen,"Times New Roman",(0,0,0))
    global playergreenoption
    playergreenoption = Button((200,200,0),display.current_w // 2 +150, display.current_h // 2-50, 300, 100, "Black Player", 36)
    playergreenoption.draw(screen,"Times New Roman",(0,0,0))
    pygame.display.flip()
        
def enemy_type_selection_screen_create():
    """
    Creates the enemy type selection screen.
    """
    # create Checkers Header
    text = "Checkers"
    headerfont = pygame.font.SysFont("Times New Roman", 72)
    header = headerfont.render(text, True, (0,0,0))
    screen.blit(header, (display.current_w // 2 - header.get_width() // 2, 100))
    text = "Select your enemy type:"
    subheaderfont = pygame.font.SysFont("Times New Roman", 48)
    subheader = subheaderfont.render(text, True, (0,0,0))
    screen.blit(subheader, (display.current_w // 2 - subheader.get_width() // 2, display.current_h // 2 -150))
    global playingagainstai
    global enemyaioption
    enemyaioption = Button((200,200,0),display.current_w // 2 - 450, display.current_h // 2-50, 300, 100, "AI Player", 36)
    enemyaioption.draw(screen,"Times New Roman",(0,0,0))
    global enemyhumanoption
    enemyhumanoption = Button((200,200,0),display.current_w // 2 +150, display.current_h // 2-50, 300, 100, "Human Player", 36)
    enemyhumanoption.draw(screen,"Times New Roman",(0,0,0))
    pygame.display.flip()

def ai_selection_screen_create():
    """
    Creates the enemy AI selection screen.
    """
    # create Checkers Header
    text = "Checkers"
    headerfont = pygame.font.SysFont("Times New Roman", 72)
    header = headerfont.render(text, True, (0,0,0))
    screen.blit(header, (display.current_w // 2 - header.get_width() // 2, 100))
    text = "Select your enemy AI:"
    subheaderfont = pygame.font.SysFont("Times New Roman", 48)
    subheader = subheaderfont.render(text, True, (0,0,0))
    screen.blit(subheader, (display.current_w // 2 - subheader.get_width() // 2, 200))
    # create buttons for enemy AI selection
    global enemyaioption1
    enemyaioption1 = Button((200,200,0),display.current_w // 2 - 150, 350, 300, 100, "Ollama Llama3.2", 36)
    enemyaioption1.draw(screen,"Times New Roman",(0,0,0))
    global enemyaioption3
    enemyaioption3 = Button((200,200,0),display.current_w // 2 - 150, 500, 300, 100, "Homemade AI", 36)
    enemyaioption3.draw(screen,"Times New Roman",(0,0,0))
    pygame.display.flip()

def selection_screen_remove():
    """
    Removes the selection screen.
    """
    pygame.draw.rect(screen, (255,255,255), (0,0, display.current_w, display.current_h))
    pygame.display.flip()

def resultboard_create(winner, loser):
    """
    Creates the result screen displaying the winner and loser.
    Args:
        winner: The winning player.
        loser: The losing player.
    """
    global playingas
    global playingagainstai
    global enemyai
    if not playingagainstai:
        winner = "You"
        loser = "yourself"
    else:
        if playingas == winner:    
            winner = "You"
            loser = f"the {enemyai} AI"
        else:
            winner = f"the {enemyai} AI"
            loser = "you"
    pygame.draw.rect(screen, (255,255,255), (0,0, display.current_w, display.current_h))
    text = f"{winner} won against {loser}!"
    headerfont = pygame.font.SysFont("Times New Roman", 72)
    header = headerfont.render(text, True, (0,0,0))
    screen.blit(header, (display.current_w // 2 - header.get_width() // 2, display.current_h // 2 - header.get_height() // 2))
    pygame.display.flip()

if __name__ == "__main__":
    grid = make_board_grid(rows, cols, gamewidth)
    highlightedPiece = None
    currMove = 'Green'
    enemy_type_selection_screen_create()
    while not enemyselected:
        screen.fill((255,255,255))
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                onexit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
                
                if enemyselected == False and playingagainstai == False:
                    if enemyhumanoption.isOver(mousepos):
                        enemyselected = True
                        selection_screen_remove()
                    if enemyaioption.isOver(mousepos):
                        playingagainstai = True
                        selection_screen_remove()
                        player_color_selection_screen_create()
                elif playingas == '' and playingagainstai == True:
                    if playerredoption.isOver(mousepos):
                        playingas = "Red"
                        grid = []
                        gap = gamewidth// rows
                        count = 0
                        for i in range(rows):
                            grid.append([])
                            for j in range(cols):
                                gridspot = Gridspot(j,i, gap)
                                if (i-j) % 2 == 1:
                                    gridspot.colour=(0,0,0)
                                if ((i+j)%2==1) and (i<3):
                                    gridspot.piece = Piece("Green")
                                elif((i+j)%2==1) and i>4:
                                    gridspot.piece=Piece("Red")
                                count+=1
                                grid[i].append(gridspot)
                        colorontop = "Green"
                        selection_screen_remove()
                        ai_selection_screen_create()
                    if playergreenoption.isOver(mousepos):
                        playingas = "Green"
                        selection_screen_remove()
                        ai_selection_screen_create()
                else:
                    if enemyaioption1.isOver(mousepos):
                        enemyai = "llama3.2"
                        enemyselected = True
                        playingagainstai = True
                        selection_screen_remove()
                    if enemyaioption3.isOver(mousepos):
                        enemyai = "homemade"
                        enemyselected = True
                        playingagainstai = True
                        selection_screen_remove()
                    
    if not playingagainstai:
        while True:
            screen.fill((255,255,255))
            for event in pygame.event.get():
                if event.type== pygame.QUIT:
                    onexit()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickedgridpos = get_board_grid_pos(rows, gamewidth)
                    if clickedgridpos is not None:
                        ClickedPositionColumn, ClickedPositionRow = clickedgridpos 
                        if turnAfterCapture:
                            # Enforce that only the capturing piece can move again
                            if capturingPiece == highlightedPiece:
                                captures, _ = generate_potential_moves(capturingPiece, grid)
                                if clickedgridpos in captures:  # Check if the clicked position is a valid capture
                                    # Allow the capturing piece to make another capture
                                    reset_colours(grid, capturingPiece)
                                    currMove = move(grid, capturingPiece, clickedgridpos)
                                    capturingPiece = clickedgridpos  # Update capturingPiece to the new position
                                    highlightedPiece = clickedgridpos  # Update highlightedPiece
                                    captures, _ = generate_potential_moves(capturingPiece, grid)
                                    if captures:
                                        highlight_potential_moves(capturingPiece, grid)  # Highlight next possible captures
                                    else:
                                        # No further captures are possible, reset capturingPiece and switch turn

                                        capturingPiece = None
                                        highlightedPiece = None  # Reset highlightedPiece
                                        end_check(grid, currMove)
                                        currMove = opposite(currMove)  # Switch turn
                                        turnAfterCapture = False  # End capture sequence
                                        reset_colours(grid, clickedgridpos)  # Reset the board colors
                                        draw_board(screen, grid, rows, gamewidth)  # Redraw the board
                        else:
                            # Normal turn logic
                            capturingPieces = get_all_capturing_pieces(currMove, grid)  # Get all pieces that can capture

                            if capturingPieces:
                                # Enforce capturing moves
                                if (ClickedPositionColumn, ClickedPositionRow) in capturingPieces:
                                    # Allow highlighting only for pieces that can capture
                                    if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                        highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)
                                elif grid[ClickedPositionColumn][ClickedPositionRow].colour == (75, 250, 240):
                                    # Allow moves only if they are capturing moves
                                    if highlightedPiece:
                                        pieceColumn, pieceRow = highlightedPiece
                                        if currMove == grid[pieceColumn][pieceRow].piece.team:
                                            captures, _ = generate_potential_moves((pieceColumn, pieceRow), grid)
                                            if clickedgridpos in captures:
                                                reset_colours(grid, highlightedPiece)
                                                currMove = move(grid, highlightedPiece, clickedgridpos)
                                                capturingPiece = clickedgridpos if (abs(pieceColumn - ClickedPositionColumn) == 2) else None
                                                highlightedPiece = clickedgridpos if capturingPiece else None  # Update highlightedPiece
                                                if capturingPiece:
                                                    turnAfterCapture = True  # Start capture sequence
                                                    captures, _ = generate_potential_moves(capturingPiece, grid)
                                                    if captures:
                                                        highlight_potential_moves(capturingPiece, grid)  # Highlight next possible captures
                                                    else:
                                                        # No further captures are possible, reset capturingPiece and switch turn
                                                        capturingPiece = None
                                                        highlightedPiece = None
                                                        end_check(grid, currMove)
                                                        currMove = opposite(currMove)
                                                        turnAfterCapture = False  # End capture sequence
                                                        reset_colours(grid, clickedgridpos)
                                                        draw_board(screen, grid, rows, gamewidth)
                            else:
                                # No capturing moves available, allow normal moves
                                if grid[ClickedPositionColumn][ClickedPositionRow].colour == (75, 250, 240):
                                    # Handle move
                                    if highlightedPiece:
                                        pieceColumn, pieceRow = highlightedPiece
                                        if currMove == grid[pieceColumn][pieceRow].piece.team:
                                            reset_colours(grid, highlightedPiece)
                                            currMove = move(grid, highlightedPiece, clickedgridpos)
                                            end_check(grid, currMove)
                                            capturingPiece = None  # Reset capturingPiece after a normal move
                                            highlightedPiece = None  # Reset the highlighted piece after the move
                                            draw_board(screen, grid, rows, gamewidth)  # Redraw the board
                                else:
                                    # Highlight normally if no captures are available
                                    if grid[ClickedPositionColumn][ClickedPositionRow].piece:
                                        if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                            highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)


            draw_board(screen, grid, rows, gamewidth)
    else:
        while True:
            screen.fill((255,255,255))
            if currMove == playingas:
                for event in pygame.event.get():
                    if event.type== pygame.QUIT:
                        onexit()
                        pygame.quit()
                        sys.exit()    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        clickedgridpos = get_board_grid_pos(rows, gamewidth)
                        if clickedgridpos is not None:
                            ClickedPositionColumn, ClickedPositionRow = clickedgridpos

                            if turnAfterCapture:
                                # Enforce that only the capturing piece can move again
                                if capturingPiece == highlightedPiece:
                                    captures, _ = generate_potential_moves(capturingPiece, grid)
                                    if clickedgridpos in captures:  # Check if the clicked position is a valid capture
                                        # Allow the capturing piece to make another capture
                                        reset_colours(grid, capturingPiece)
                                        currMove = move(grid, capturingPiece, clickedgridpos)
                                        capturingPiece = clickedgridpos  # Update capturingPiece to the new position
                                        highlightedPiece = clickedgridpos  # Update highlightedPiece
                                        captures, _ = generate_potential_moves(capturingPiece, grid)
                                        if captures:
                                            highlight_potential_moves(capturingPiece, grid)  # Highlight next possible captures
                                        else:
                                            # No further captures are possible, reset capturingPiece and switch turn
                                            capturingPiece = None
                                            highlightedPiece = None  # Reset highlightedPiece
                                            end_check(grid, currMove)
                                            currMove = opposite(currMove)  # Switch turn
                                            turnAfterCapture = False  # End capture sequence
                                            reset_colours(grid, clickedgridpos)  # Reset the board colors
                                            draw_board(screen, grid, rows, gamewidth)  # Redraw the board
                            else:
                                # Normal turn logic
                                capturingPieces = get_all_capturing_pieces(currMove, grid)  # Get all pieces that can capture

                                if capturingPieces:
                                    # Enforce capturing moves
                                    if (ClickedPositionColumn, ClickedPositionRow) in capturingPieces:
                                        # Allow highlighting only for pieces that can capture
                                        if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                            highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)
                                    elif grid[ClickedPositionColumn][ClickedPositionRow].colour == (75, 250, 240):
                                        # Allow moves only if they are capturing moves
                                        if highlightedPiece:
                                            pieceColumn, pieceRow = highlightedPiece
                                            if currMove == grid[pieceColumn][pieceRow].piece.team:
                                                captures, _ = generate_potential_moves((pieceColumn, pieceRow), grid)
                                                if clickedgridpos in captures:
                                                    reset_colours(grid, highlightedPiece)
                                                    currMove = move(grid, highlightedPiece, clickedgridpos)
                                                    capturingPiece = clickedgridpos if (abs(pieceColumn - ClickedPositionColumn) == 2) else None
                                                    highlightedPiece = clickedgridpos if capturingPiece else None  # Update highlightedPiece
                                                    if capturingPiece:
                                                        turnAfterCapture = True  # Start capture sequence
                                                        captures, _ = generate_potential_moves(capturingPiece, grid)
                                                        if captures:
                                                            highlight_potential_moves(capturingPiece, grid)  # Highlight next possible captures
                                                        else:
                                                            # No further captures are possible, reset capturingPiece and switch turn
                                                            capturingPiece = None
                                                            highlightedPiece = None
                                                            end_check(grid, currMove)
                                                            currMove = opposite(currMove)
                                                            turnAfterCapture = False  # End capture sequence
                                                            reset_colours(grid, clickedgridpos)
                                                            draw_board(screen, grid, rows, gamewidth)
                                else:
                                    # No capturing moves available, allow normal moves
                                    if grid[ClickedPositionColumn][ClickedPositionRow].colour == (75, 250, 240):
                                        # Handle move
                                        if highlightedPiece:
                                            pieceColumn, pieceRow = highlightedPiece
                                            if currMove == grid[pieceColumn][pieceRow].piece.team:
                                                reset_colours(grid, highlightedPiece)
                                                currMove = move(grid, highlightedPiece, clickedgridpos)
                                                end_check(grid, currMove)
                                                capturingPiece = None  # Reset capturingPiece after a normal move
                                                highlightedPiece = None  # Reset the highlighted piece after the move
                                                draw_board(screen, grid, rows, gamewidth)  # Redraw the board
                                    else:
                                        # Highlight normally if no captures are available
                                        if grid[ClickedPositionColumn][ClickedPositionRow].piece:
                                            if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                                highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)
            else:
                if enemyai == "llama3.2":
                    draw_board(screen, grid, rows, gamewidth)
                    for event in pygame.event.get():
                        if event.type== pygame.QUIT:
                            onexit()
                            pygame.quit()
                            sys.exit()
                    # AI's turn
                    
                    if not aimoverequested:
                        aimoverequested = True
                        board_state = analyze_board_state(grid)
                        
                        # Ensure the AI generates moves for the correct team
                        ai_team = opposite(playingas)  # AI plays as the opposite team
                        board_str = '\n'.join([' '.join(map(str, row)) for row in board_state])
                        legal_moves = generate_legal_moves(currMove, grid)  # Pass the correct team to generatelegalmoves
                        ai_move_origin, ai_move_destination = format_ai_move(board_str, ai_team, legal_moves)
                        
                    if ai_move_origin:
                        print(ai_move_origin, ai_move_destination)
                        formatedaimove = f"{ai_move_origin[0]}{ ai_move_origin[1]}-{ai_move_destination[0]}{ai_move_destination[1]}"
                        score = rate_move(generate_legal_moves(currMove, grid), grid, currMove, colorontop, formatedaimove )
                        score_list.append(score)
                        if not ai_move_destination:
                            # Handle multi-jump move
                            ai_move = ai_move_origin.split("-")
                            for i in range(len(ai_move) - 1):
                                origin = ai_move[i]
                                destination = ai_move[i + 1]
                                # NEW (color-dependent - replace the hardcoded section):
                                if playingas == "Red":  # Red (White in algebraic) - top→bottom, a-h left→right
                                    origin_col = ord(ai_move_origin[0]) - ord('a')
                                    origin_row = 8 - int(ai_move_origin[1])  # rank 1=top (row 7), rank 8=bottom (row 0)
                                    dest_col = ord(ai_move_destination[0]) - ord('a')
                                    dest_row = 8 - int(ai_move_destination[1])  
                                elif playingas == "Green":  # Green (Black in algebraic) - bottom→top, h-a right→left
                                    origin_col = 7 - (ord(ai_move_origin[0]) - ord('a'))  # h=0, g=1, ..., a=7
                                    origin_row = int(ai_move_origin[1]) - 1              # rank 1=bottom (row 0), rank 8=top (row 7)
                                    dest_col = 7 - (ord(ai_move_destination[0]) - ord('a'))
                                    dest_row = int(ai_move_destination[1]) - 1
                                move(grid, (origin_row, origin_col), (dest_row, dest_col))
                                draw_board(screen, grid, rows, gamewidth)
                                pygame.time.delay(500)  # Pause for half a second between jumps
                            aimoverequested = False  # Reset flag after multi-jump move
                        else:
                            # Handle single move
                            if playingas == "Red":  # Red (White in algebraic) - top→bottom, a-h left→right
                                origin_col = ord(ai_move_origin[0]) - ord('a')
                                origin_row = 8 - int(ai_move_origin[1])  # rank 1=top (row 7), rank 8=bottom (row 0)
                                dest_col = ord(ai_move_destination[0]) - ord('a')
                                dest_row = 8 - int(ai_move_destination[1])
                            elif playingas == "Green":  # Green (Black in algebraic) - bottom→top, h-a right→left
                                origin_col = 7 - (ord(ai_move_origin[0]) - ord('a'))  # h=0, g=1, ..., a=7
                                origin_row = int(ai_move_origin[1]) - 1              # rank 1=bottom (row 0), rank 8=top (row 7)
                                dest_col = 7 - (ord(ai_move_destination[0]) - ord('a'))
                                dest_row = int(ai_move_destination[1]) - 1
                            move(grid, (origin_row, origin_col), (dest_row, dest_col))
                            aimoverequested = False  # Reset flag after single move
                        draw_board(screen, grid, rows, gamewidth)
                        end_check(grid, currMove)
                        currMove = opposite(currMove)
                        aimoverequested = False  # Ensure flag is reset at the end of AI's turn
                else:  # Homemade AI
                    end_check(grid, currMove)
                    draw_board(screen, grid, rows, gamewidth)
                    bestmove = select_best_move(generate_legal_moves(currMove, grid), grid, currMove, colorontop)
                    start_col, start_row = bestmove[0], bestmove[1]
                    end_col, end_row = bestmove[3], bestmove[4]
                    start_row, start_col = notation_to_position(start_row, start_col, colorontop)
                    end_row, end_col = notation_to_position(end_row, end_col, colorontop)
                    move(grid, (int(start_col), int(start_row)), (int(end_col), int(end_row)))
                    end_check(grid, currMove)
                    currMove = opposite(currMove)
            draw_board(screen, grid, rows, gamewidth)
