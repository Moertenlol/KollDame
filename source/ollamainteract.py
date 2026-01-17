import ollama

MODEL = 'llama3.2'

def ai_select_move(board_state, color, legal_moves):

    if color == 'Red':
        notation = "Files a-h left→right (col 0=a, col 7=h), Ranks 1-8 top→bottom (row 0=rank 1, row 7=rank 8)"
    else:
        notation = "Files h-a right→left (col 0=h, col 7=a), Ranks 1-8 bottom→top (row 7=rank 1, row 0=rank 8)"
    move_amount = len(legal_moves)
    moves_list = "\n".join(f"{i}: {move}" for i, move in enumerate(legal_moves[:10]))  # Top 10


    prompt = f"""
    You are playing STANDARD CHECKERS on an 8x8 board.

    BOARD FORMAT (rows from your side to opponent):
    {board_state}

    PIECE CODES:
    1=your man, 10=your king, 2=opponent man, 20=opponent king, 0=empty

    ALGEBRAIC NOTATION:
    {notation}

    LEGAL MOVES ONLY (numbered 1-{move_amount}, pick ONE by number):
    {legal_moves}

    Respond with ONLY the NUMBER (e.g. "3") of your chosen best move.
    NO explanations, NO move notation, JUST the number.
    """
    if move_amount > 1:
        response = ollama.chat(model=MODEL, messages=[
            {'role': 'system', 'content': 'You are a checkers AI. Be fast and legal.'},
            {'role': 'user', 'content': prompt}
        ])
        index = response['message']['content'].strip()
        if not index.isdigit() or not (1 <= int(index) <= move_amount):
            print("Invalid AI response. Rerunning")
            return ai_select_move(board_state, color, legal_moves)
    else:
        index = 1
    return legal_moves[int(index)-1]


def format_ai_move(board_str, color, legal_moves):    
    ai_move = ai_select_move(board_str, color, legal_moves)
    print(f"AI move: {ai_move}")
    ai_move_array = ai_move.split('-')
    if len(ai_move_array) > 2:
        return ai_move_array  # Multi-jump move, UNTERSCHEIDUNG EINZELMOVE UND MEHRFACHMOVE IMPLEMENTIEREN IN MAIN
    else: 
        ai_move_origin = ai_move_array[0]
        ai_move_origin = ai_move_origin[0], ai_move_origin[1]
        ai_move_destination = ai_move_array[1]
        ai_move_destination = ai_move_destination[0], ai_move_destination[1]
        return ai_move_origin, ai_move_destination

def test_ai():
    board_state = """0 1 0 1 0 1 0 1
1 0 1 0 1 0 1 0
0 1 0 1 0 1 0 1
0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0
2 0 2 0 2 0 2 0
0 2 0 2 0 2 0 2
2 0 2 0 2 0 2 0"""
    color = 'Red'
    legal_moves = ['1.: h6-g5', '2.: f6-g5', '3.: f6-e5', '4.: d6-e5', '5.: d6-c5', '6.: b6-c5', '7.: b6-a5']
