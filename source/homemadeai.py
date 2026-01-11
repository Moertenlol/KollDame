import copy

def score_move(grid, start_pos, end_pos, currMove, colorontop):
    from main import notation_to_position, Piece
    score = 0
    start_col, start_row = start_pos[0], start_pos[1]
    start_col, start_row = notation_to_position(start_row, start_col, colorontop)
    end_col, end_row = end_pos[0], end_pos[1]
    end_col, end_row = notation_to_position(end_row, end_col, colorontop)

    # 1. Promotion
    if is_promotion(grid, start_pos, end_pos, currMove, colorontop):
        score += 800
        return score
    
    # 2. Positional
    piece_type = grid[start_row][start_col].piece.get_type()
    if piece_type == "MAN":
        row_advance = end_row - start_row
        score += 50 * row_advance  # Closer to promotion
    
    # 3. Edge control
    if end_col in [0,7]:
        score += 20
    
    # 4. Center
    if end_col in [2,3,4,5]:
        score += 30
    
    # 5. Safety
    threatened = threatened_check(grid, currMove)
    threatened_after_move = threatened_check_after_move(grid, (start_col,start_row),(end_col,end_row))
    print("Threatened before move:", threatened, "after move:", threatened_after_move)
    if threatened > threatened_after_move:
        score += 700  # Move to safer position
    if threatened < threatened_after_move:
        score -= 700  # Move to more threatened position
    return score

def is_promotion(board, start_pos, end_pos, currMove, colorontop):
    if currMove == colorontop:
        promotion_row = 0
    else:
        promotion_row = 7
    end_row = end_pos[1]
    if end_row == promotion_row:
        return True

def threatened_check(board, currMove):
    from main import generatelegalmoves
    threat_count = 0
    enemy_moves = generatelegalmoves(currMove, board)
    
    # Debugging output to trace generatelegalmoves and threat calculation
    print("Calculating threats for currMove:", currMove)
    print("Enemy moves:", enemy_moves)
    for move in enemy_moves:
        start_pos, end_pos = int(move[1]), int(move[4])
        if abs(end_pos - start_pos) == 2:
            print("Threat detected from", start_pos, "to", end_pos)
            threat_count += 1
    print("Total threats:", threat_count)
    
    # Updated logic to check if a piece is in front and can be taken
    for row in range(len(board)):
        for col in range(len(board[row])):
            spot = board[row][col]
            if spot.piece and spot.piece.team != currMove:  # Enemy piece
                # Check diagonals for threats
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < len(board) and 0 <= c < len(board[row]):
                        next_spot = board[r][c]
                        if next_spot.piece and next_spot.piece.team == currMove:  # Ally piece in position to take
                            # Check if there's no piece behind the enemy
                            br, bc = row - dr, col - dc
                            if 0 <= br < len(board) and 0 <= bc < len(board[row]):
                                behind_spot = board[br][bc]
                                if not behind_spot.piece:  # No piece behind
                                    threat_count += 1
    # Updated logic to check if a currMove piece can be taken by the enemy
    for row in range(len(board)):
        for col in range(len(board[row])):
            spot = board[row][col]
            if spot.piece and spot.piece.team == currMove:  # Ally piece
                # Check diagonals for threats
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < len(board) and 0 <= c < len(board[row]):
                        enemy_spot = board[r][c]
                        if enemy_spot.piece and enemy_spot.piece.team != currMove:  # Enemy piece in position to take
                            # Check if there's no ally piece behind the currMove piece
                            br, bc = row - dr, col - dc
                            if 0 <= br < len(board) and 0 <= bc < len(board[row]):
                                behind_spot = board[br][bc]
                                if not behind_spot.piece:  # No ally piece behind
                                    threat_count += 1
    return threat_count

def threatened_check_after_move(board, start_pos, end_pos):
    from main import generatelegalmoves, Gridspot

    # Create a custom deep copy of the board
    temp_board = [[Gridspot(spot.row, spot.col, spot.x) for spot in row] for row in board]

    # Copy the pieces manually
    for col in range(len(board)):
        for row in range(len(board[col])):
            if board[col][row].piece:
                temp_board[col][row].piece = board[col][row].piece

    # Simulate the move
    start_col, start_row = start_pos
    end_col, end_row = end_pos
    moving_piece = temp_board[start_row][start_col].piece
    temp_board[end_row][end_col].piece = moving_piece
    temp_board[start_row][start_col].piece = None

    # Calculate threats
    threat_count = 0
    currMove = moving_piece.team
    enemy_moves = generatelegalmoves(currMove, temp_board)
    
    # Debugging output to trace generatelegalmoves and threat calculation
    print("Simulating move from", start_pos, "to", end_pos)
    print("Enemy moves after move:", enemy_moves)
    for move in enemy_moves:
        start_pos, end_pos = int(move[1]), int(move[4])
        if abs(int(end_pos) - int(start_pos)) == 2:
            print("Threat detected from", start_pos, "to", end_pos)
            threat_count += 1
    print("Total threats after move:", threat_count)
    
    # Updated logic to check if a piece is in front and can be taken after a move
    for row in range(len(temp_board)):
        for col in range(len(temp_board[row])):
            spot = temp_board[row][col]
            if spot.piece and spot.piece.team != moving_piece.team:  # Enemy piece
                # Check diagonals for threats
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < len(temp_board) and 0 <= c < len(temp_board[row]):
                        next_spot = temp_board[r][c]
                        if next_spot.piece and next_spot.piece.team == moving_piece.team:  # Ally piece in position to take
                            # Check if there's no piece behind the enemy
                            br, bc = row - dr, col - dc
                            if 0 <= br < len(temp_board) and 0 <= bc < len(temp_board[row]):
                                behind_spot = temp_board[br][bc]
                                if not behind_spot.piece:  # No piece behind
                                    threat_count += 1
    # Updated logic to check if a currMove piece can be taken by the enemy after a move
    for row in range(len(temp_board)):
        for col in range(len(temp_board[row])):
            spot = temp_board[row][col]
            if spot.piece and spot.piece.team == moving_piece.team:  # Ally piece
                # Check diagonals for threats
                for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    r, c = row + dr, col + dc
                    if 0 <= r < len(temp_board) and 0 <= c < len(temp_board[row]):
                        enemy_spot = temp_board[r][c]
                        if enemy_spot.piece and enemy_spot.piece.team != moving_piece.team:  # Enemy piece in position to take
                            # Check if there's no ally piece behind the currMove piece
                            br, bc = row - dr, col - dc
                            if 0 <= br < len(temp_board) and 0 <= bc < len(temp_board[row]):
                                behind_spot = temp_board[br][bc]
                                if not behind_spot.piece:  # No ally piece behind
                                    threat_count += 1
    return threat_count

def select_best_move(legal_moves, grid, currMove, colorontop):
    from main import generatelegalmoves
    move_score =[]
    for legal_move in legal_moves:
        move_score.append(score_move(grid, (legal_move[0], legal_move[1]),(legal_move[3],legal_move[4]), currMove, colorontop))
        print(f"Move {legal_move} has score {move_score}")
    # if multiple moves have the same score, pick randomly among them
    if move_score.count(max(move_score)) > 1:
        best_moves = [i for i, score in enumerate(move_score) if score == max(move_score)]
        import random
        best_move_index = random.choice(best_moves)
        best_move = legal_moves[best_move_index]

    else:
        best_move_index = move_score.index(max(move_score))
        best_move = legal_moves[best_move_index]

    return best_move
