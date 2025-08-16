import pygame
from PIL import Image
import random
import sys
import os
pygame.init()

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
    pygame.display.update()

def make_boardgrid(rows, cols, width):
    boardgrid = []
    gap = width// rows
    count = 0
    for i in range(rows):
        boardgrid.append([])
        for j in range(cols):
            gridspot = Gridspot(j,i, gap)
            if (i-j) % 2 == 0:
                gridspot.colour=(0,0,0)
            if ((i+j)%2==0) and (i<3):
                gridspot.piece = Piece("Red")
            elif((i+j)%2==0) and i>4:
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
            boardgrid[posX][posY].colour = (0, 0, 0) if (posX - posY) % 2 == 0 else (255, 255, 255)

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
        

if __name__ == "__main__":
    grid = make_boardgrid(rows, cols, gamewidth)
    highlightedPiece = None
    currMove = 'Green'

    while True:
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





