# CheckersAI

A simple Checkers (Draughts) game implementation with an AI using Minimax and alpha-beta pruning.

This repository includes a playable board representation and an AI that evaluates positions to choose moves. It is intended as a learning project and a foundation for experimenting with search depth, evaluation heuristics, and move analysis.

## Features

- Board, pieces and move logic for standard 8x8 checkers
- AI based on Minimax with alpha-beta pruning
- Position evaluator for scoring board states
- Utilities for move analysis and PDF export (basic)

## Requirements

- Python 3.8+
- No external packages required for core functionality (checkers logic and AI)

Optional (for any extra utilities you add):
- reportlab or similar library to enable advanced PDF export

## Installation

1. Clone the repository or copy the files to your local machine.
2. (Optional) Create and activate a virtual environment:

   python -m venv .venv
   source .venv/bin/activate

3. Install any optional packages if you intend to use them (for example, PDF generation):

   pip install -r requirements.txt

## Running the game / AI

There are simple entry points in this repository:

- `main.py` — Basic runner for the game (CLI or simple loop). Open this file to see how the Board and AI are wired together.
- `ai.py` — Contains the `AI` class implementing Minimax with alpha-beta pruning. You can instantiate it and call `get_best_move(board, player)`.

Example usage inside a Python REPL or script:

```python
from ai import AI
from board import Board

board = Board()  # create starting position or custom position
ai = AI(depth=4)
move = ai.get_best_move(board, 'red')
print(move)
```

Adjust `depth` to increase or decrease search strength and runtime.

## Files overview

- `board.py` — Board representation, rules, move generation, and game state checks.
- `piece.py` — Piece class and related utilities (king state, movement helpers).
- `ai.py` — Minimax AI with alpha-beta pruning, move evaluation helpers, and search statistics.
- `evaluator.py` — Position evaluator used by the AI to score positions from Red's perspective.
- `move_analyzer.py` — Helpers to break down and analyze moves (if present).
- `pdf_generator.py` — Basic PDF export utilities (if used to export game states or reports).
- `main.py` — Example or CLI entry point for running the game.

There's also an `Archive/` directory that contains older versions of many of these files.

## Tuning and experimentation

- Evaluation: Modify `evaluator.py` to change heuristics (material, positional weights, center control, king value).
- Depth: Increase `AI(depth=...)` for stronger play; performance scales exponentially.
- Move ordering: Implement heuristics (captures first, killer moves) to improve alpha-beta pruning efficiency.

## Tests

No formal test suite is included yet. For development, consider adding unit tests for:

- Move generation correctness (including jumps and multiple captures)
- Game-over detection and kinging behavior
- Evaluator consistency
- AI choosing captures when appropriate

## Contributing

Contributions are welcome. Suggested small improvements:

- Add unit tests
- Improve the evaluator heuristic and share benchmark results
- Add a simple GUI or web front-end for visualization
- Add optional transposition table (Zobrist hashing) to speed up searches

## License

This project is provided as-is for learning and experimentation. Add a license file if you plan to publish or distribute it.

---

If you want, I can also:
- Add a basic `requirements.txt` or `setup.py`
- Create example scripts that play AI vs AI or AI vs human
- Generate unit tests for core modules

Tell me which you'd like next.
