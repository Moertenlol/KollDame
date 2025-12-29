import ollama

MODEL = 'llama3.2'

def get_ai_move(board_state):
    prompt = f"""
    You are playing checkers (8x8 board). Current board (1=your piece, 2=opponent, 0=empty):
    {board_state}
    
    Respond ONLY with your move in algebraic notation like 'c3-b4' or multi-jump 'c3-d4-e5'.
    """
    
    response = ollama.chat(model=MODEL, messages=[
        {'role': 'system', 'content': 'You are a checkers AI. Be fast and legal.'},
        {'role': 'user', 'content': prompt}
    ])
    
    return response['message']['content'].strip()

# Example usage for checkers loop
if __name__ == "__main__":
    # Dummy 8x8 board as list of lists (flatten for prompt)
    example_board = [[0]*8 for _ in range(8)]  # Replace with real board logic
    board_str = '\n'.join([' '.join(map(str, row)) for row in example_board])
    
    ai_move = get_ai_move(board_str)
    print(f"AI move: {ai_move}")
