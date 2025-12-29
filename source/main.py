import pygame
from PIL import Image
import random
import sys
import os
import ollama
from ollamainteract import get_ai_move
from Button import Button
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
playingas = 'Black' #MERKEN DAS SCHWARZ WARUM AUCH IMMER ALS ERSTES DRAN IST NICHT VERGESSEN IDK WIE LANGE NOCH 
playingagainstai = False
enemyai = "llama3.2"
enemyselected = False

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
        pygame.draw.rect(screen, self.colour, (self.x, self.y, gamewidth / rows, gamewidth / cols))
        if self.piece:
            screen.blit(self.piece.image, (self.x, self.y))

def drawboard(screen, boardgrid, rows, width):
    for row in boardgrid:
        for spot in row:
            spot.draw(screen)
    drawboardgrid(screen, rows, width)
    drawlettersandnumbers(screen, rows, width)
    pygame.display.update()

def make_boardgrid(rows, cols, width):
    boardgrid = []
    gap = width// rows
    count = 0
    for i in range(rows):
        boardgrid.append([])
        for j in range(cols):
            gridspot = Gridspot(j,i, gap)
            if (i-j) % 2 == 1:
                gridspot.colour=(0,0,0)
            if ((i+j)%2==1) and (i<3):
                gridspot.piece = Piece("Red")
            elif((i+j)%2==1) and i>4:
                gridspot.piece=Piece("Green")
            count+=1
            boardgrid[i].append(gridspot)
    return boardgrid

def drawboardgrid(screen, rows, width):
    gap = width // rows
    for i in range(rows+1):
        pygame.draw.line(screen, (0,0,0), (boardedgefromleft, i * gap + boardedgefromtop), (width + boardedgefromleft -5, i * gap +boardedgefromtop ))
        for j in range(cols+1):
            pygame.draw.line(screen, (0,0,0), (j * gap + boardedgefromleft, boardedgefromtop), (j * gap + boardedgefromleft , width + boardedgefromtop -5))

def drawlettersandnumbers(screen, rows, width):
    global playingas 
    gap = width // rows
    font = pygame.font.SysFont("Times New Roman" , 36)
    if playingas == "White":
        letters = ['a','b','c','d','e','f','g','h']
        numbers = ['1','2','3','4','5','6','7','8']
    else:
        letters = ['h','g','f','e','d','c','b','a']
        numbers = ['8','7','6','5','4','3','2','1']
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
        self.type = None

    def project(self, x, y):
        screen.blit(self.image, (x + boardedgefromleft,y + boardedgefromtop))


def getboardgridpos(rows, width):
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

def resetColours(boardgrid, node):
    if node:
        captures, moves = generatePotentialMoves(node, boardgrid)  # Unpack captures and moves
        positions = captures + moves  # Combine captures and moves into a single list
        positions.append(node)  # Add the current node to the list

        for colouredNodes in positions:
            posX, posY = colouredNodes
            boardgrid[posX][posY].colour = (0, 0, 0) if (posX - posY) % 2 == 1 else (255, 255, 255)

def HighlightpotentialMoves(piecePosition, boardgrid):
    global turnAfterCapture
    captures, moves = generatePotentialMoves(piecePosition, boardgrid)
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
    return "Red" if team=="Green" else "Green"

def generatePotentialMoves(nodePosition, boardgrid):
    checker = lambda x, y: 0 <= x + y < 8  # Ensure the position is within bounds
    captures = []
    moves = []
    column, row = nodePosition
    if boardgrid[column][row].piece:
        piece = boardgrid[column][row].piece
        if piece.type == 'Dame':
            # Dame (king) can move in all directions
            vectors = [[1, -1], [1, 1], [-1, -1], [-1, 1]]
        else:
            # Regular pieces can only move forward
            vectors = [[1, -1], [1, 1]] if piece.team == "Red" else [[-1, -1], [-1, 1]]
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

def analyzeboardstate(boardgrid):
    board_state = []
    for row in boardgrid:
        board_row = []
        for spot in row:
            if spot.piece:
                if spot.piece.team == "Red":
                    board_row.append(1)
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
    Column, Row = ClickedNode
    if boardgrid[Column][Row].piece and boardgrid[Column][Row].piece.team == currMove:
        if OldHighlight:
            resetColours(boardgrid, OldHighlight)  # Reset the old highlight
        HighlightpotentialMoves(ClickedNode, boardgrid)  # Highlight potential moves
        return (Column, Row)  # Update the highlighted piece
    return OldHighlight  # Return the old highlight if the piece doesn't belong to the current player

def move(boardgrid, piecePosition, newPosition):
    global capturingPiece  # Use the global capturingPiece variable
    resetColours(boardgrid, piecePosition)
    newColumn, newRow = newPosition
    oldColumn, oldRow = piecePosition

    piece = boardgrid[oldColumn][oldRow].piece
    boardgrid[newColumn][newRow].piece = piece
    boardgrid[oldColumn][oldRow].piece = None

    if newColumn == 7 and boardgrid[newColumn][newRow].piece.team == "Red":
        boardgrid[newColumn][newRow].piece.type = 'Dame'
        boardgrid[newColumn][newRow].piece.image = reddame
    if newColumn == 0 and boardgrid[newColumn][newRow].piece.team == "Green":
        boardgrid[newColumn][newRow].piece.type = 'Dame'
        boardgrid[newColumn][newRow].piece.image = greendame

    if abs(newColumn - oldColumn) == 2 or abs(newRow - oldRow) == 2:
        # A capture occurred
        boardgrid[int((newColumn + oldColumn) / 2)][int((newRow + oldRow) / 2)].piece = None
        capturingPiece = (newColumn, newRow)  # Update capturingPiece to the new position
        return boardgrid[newColumn][newRow].piece.team

    capturingPiece = None  # Reset capturingPiece if no capture occurred
    return opposite(boardgrid[newColumn][newRow].piece.team)

def getAllCapturingPieces(currMove, boardgrid):
    capturingPieces = []
    for rowIndex, row in enumerate(boardgrid):
        for colIndex, spot in enumerate(row):
            if spot.piece and spot.piece.team == currMove:
                captures, _ = generatePotentialMoves((rowIndex, colIndex), boardgrid)
                if captures:
                    capturingPieces.append((rowIndex, colIndex))
    return capturingPieces
        
def selectionscreencreate():
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

def aiselectionscreencreate():
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
    global enemyaioption2
    enemyaioption2 = Button((200,200,0),display.current_w // 2 - 150, 500, 300, 100, "OpenAI GPT-4o", 36)
    enemyaioption2.draw(screen,"Times New Roman",(0,0,0))
    global enemyaioption3
    enemyaioption3 = Button((200,200,0),display.current_w // 2 - 150, 650, 300, 100, "Homemade AI", 36)
    enemyaioption3.draw(screen,"Times New Roman",(0,0,0))
    pygame.display.flip()

def selectionscreenremove():
    pygame.draw.rect(screen, (255,255,255), (0,0, display.current_w, display.current_h))
    pygame.display.flip()


if __name__ == "__main__":
    grid = make_boardgrid(rows, cols, gamewidth)
    highlightedPiece = None
    currMove = 'Green'
    selectionscreencreate()
    while not enemyselected:
        screen.fill((255,255,255))
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                onexit()
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mousepos = pygame.mouse.get_pos()
                if not playingagainstai:
                    if enemyhumanoption.isOver(mousepos):
                        enemyselected = True
                        selectionscreenremove()
                    if enemyaioption.isOver(mousepos):
                        playingagainstai = True
                        selectionscreenremove()
                        aiselectionscreencreate()

                else:
                    if enemyaioption1.isOver(mousepos):
                        enemyai = "llama3.2"
                        enemyselected = True
                        playingagainstai = True
                        selectionscreenremove()
                    if enemyaioption2.isOver(mousepos):
                        enemyai = "gpt-4o"
                        enemyselected = True
                        selectionscreenremove()
                        playingagainstai = True
                    if enemyaioption3.isOver(mousepos):
                        enemyai = "homemade"
                        enemyselected = True
                        selectionscreenremove()
                        playingagainstai = True
                    
    if not playingagainstai:
        while True:
            screen.fill((255,255,255))
            for event in pygame.event.get():
                if event.type== pygame.QUIT:
                    onexit()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clickedgridpos = getboardgridpos(rows, gamewidth)
                    if clickedgridpos is not None:
                        ClickedPositionColumn, ClickedPositionRow = clickedgridpos

                        if turnAfterCapture:
                            # Enforce that only the capturing piece can move again
                            if capturingPiece == highlightedPiece:
                                captures, _ = generatePotentialMoves(capturingPiece, grid)
                                if clickedgridpos in captures:  # Check if the clicked position is a valid capture
                                    # Allow the capturing piece to make another capture
                                    resetColours(grid, capturingPiece)
                                    currMove = move(grid, capturingPiece, clickedgridpos)
                                    capturingPiece = clickedgridpos  # Update capturingPiece to the new position
                                    highlightedPiece = clickedgridpos  # Update highlightedPiece
                                    captures, _ = generatePotentialMoves(capturingPiece, grid)
                                    if captures:
                                        HighlightpotentialMoves(capturingPiece, grid)  # Highlight next possible captures
                                    else:
                                        # No further captures are possible, reset capturingPiece and switch turn
                                        print("No further captures are possible.")
                                        capturingPiece = None
                                        highlightedPiece = None  # Reset highlightedPiece
                                        currMove = opposite(currMove)  # Switch turn
                                        turnAfterCapture = False  # End capture sequence
                                        resetColours(grid, clickedgridpos)  # Reset the board colors
                                        drawboard(screen, grid, rows, gamewidth)  # Redraw the board
                                else:
                                    print("Invalid move. You must capture one of the highlighted positions.")
                            else:
                                print("Only the capturing piece can move again.")
                        else:
                            # Normal turn logic
                            capturingPieces = getAllCapturingPieces(currMove, grid)  # Get all pieces that can capture

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
                                            captures, _ = generatePotentialMoves((pieceColumn, pieceRow), grid)
                                            if clickedgridpos in captures:
                                                resetColours(grid, highlightedPiece)
                                                currMove = move(grid, highlightedPiece, clickedgridpos)
                                                capturingPiece = clickedgridpos if (abs(pieceColumn - ClickedPositionColumn) == 2) else None
                                                highlightedPiece = clickedgridpos if capturingPiece else None  # Update highlightedPiece
                                                if capturingPiece:
                                                    turnAfterCapture = True  # Start capture sequence
                                                    captures, _ = generatePotentialMoves(capturingPiece, grid)
                                                    if captures:
                                                        HighlightpotentialMoves(capturingPiece, grid)  # Highlight next possible captures
                                                    else:
                                                        # No further captures are possible, reset capturingPiece and switch turn
                                                        capturingPiece = None
                                                        highlightedPiece = None
                                                        currMove = opposite(currMove)
                                                        turnAfterCapture = False  # End capture sequence
                                                        resetColours(grid, clickedgridpos)
                                                        drawboard(screen, grid, rows, gamewidth)
                                            else:
                                                print("Invalid move. You must capture one of the highlighted positions.")
                            else:
                                # No capturing moves available, allow normal moves
                                if grid[ClickedPositionColumn][ClickedPositionRow].colour == (75, 250, 240):
                                    # Handle move
                                    if highlightedPiece:
                                        pieceColumn, pieceRow = highlightedPiece
                                        if currMove == grid[pieceColumn][pieceRow].piece.team:
                                            resetColours(grid, highlightedPiece)
                                            currMove = move(grid, highlightedPiece, clickedgridpos)
                                            capturingPiece = None  # Reset capturingPiece after a normal move
                                            highlightedPiece = None  # Reset the highlighted piece after the move
                                            drawboard(screen, grid, rows, gamewidth)  # Redraw the board
                                else:
                                    # Highlight normally if no captures are available
                                    if grid[ClickedPositionColumn][ClickedPositionRow].piece:
                                        if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                            highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)


            drawboard(screen, grid, rows, gamewidth)
    else:
        while True:
            screen.fill((255,255,255))
            for event in pygame.event.get():
                if event.type== pygame.QUIT:
                    onexit()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if currMove == playingas:
                        clickedgridpos = getboardgridpos(rows, gamewidth)
                        if clickedgridpos is not None:
                            ClickedPositionColumn, ClickedPositionRow = clickedgridpos

                            if turnAfterCapture:
                                # Enforce that only the capturing piece can move again
                                if capturingPiece == highlightedPiece:
                                    captures, _ = generatePotentialMoves(capturingPiece, grid)
                                    if clickedgridpos in captures:  # Check if the clicked position is a valid capture
                                        # Allow the capturing piece to make another capture
                                        resetColours(grid, capturingPiece)
                                        currMove = move(grid, capturingPiece, clickedgridpos)
                                        capturingPiece = clickedgridpos  # Update capturingPiece to the new position
                                        highlightedPiece = clickedgridpos  # Update highlightedPiece
                                        captures, _ = generatePotentialMoves(capturingPiece, grid)
                                        if captures:
                                            HighlightpotentialMoves(capturingPiece, grid)  # Highlight next possible captures
                                        else:
                                            # No further captures are possible, reset capturingPiece and switch turn
                                            print("No further captures are possible.")
                                            capturingPiece = None
                                            highlightedPiece = None  # Reset highlightedPiece
                                            currMove = opposite(currMove)  # Switch turn
                                            turnAfterCapture = False  # End capture sequence
                                            resetColours(grid, clickedgridpos)  # Reset the board colors
                                            drawboard(screen, grid, rows, gamewidth)  # Redraw the board
                                    else:
                                        print("Invalid move. You must capture one of the highlighted positions.")
                                else:
                                    print("Only the capturing piece can move again.")
                            else:
                                # Normal turn logic
                                capturingPieces = getAllCapturingPieces(currMove, grid)  # Get all pieces that can capture

                                if capturingPieces:
                                    # Enforce capturing moves
                                    if (ClickedPositionColumn, ClickedPositionRow) in capturingPieces:
                                        # Allow highlighting only for pieces that can capture
                                        if grid[ClickedPositionColumn][ClickedPositionRow].piece.team == currMove:
                                            highlightedPiece = highlight(clickedgridpos, grid, highlightedPiece, currMove)
            drawboard(screen, grid, rows, gamewidth)



