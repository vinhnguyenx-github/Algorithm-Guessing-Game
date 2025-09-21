# Guessing Algorithm Game

An interactive game built with **Pygame** where players watch two sorting algorithm visualizations side by side and try to predict which one will finish first.

## Gameplay

- Two algorithms run simultaneously (currently **Bubble Sort**, **Insertion Sort**, **Quick Sort**, and **Merge Sort** (can be expendable if needed)).
- The player hovers over the left or right side to highlight, then clicks to make a prediction.
- After clicking, both algorithms speed up.
- When one finishes, the result is displayed on screen:
  - **Correct** if the chosen algorithm finished first.
  - **Incorrect** otherwise.
- Reaction time and results are logged.

## Data Logging

- Each session is saved under the `data/` folder.
- Files are named `attemptX.csv`, where `X` is the session index.
- Each row records:
  - **id**: try number within the attempt
  - **time**: reaction time in seconds
  - **result**: whether the prediction was correct or incorrect

> The `data/` folder is ignored via `.gitignore` so logs are not pushed to GitHub.

## Analysis

Jupyter notebooks under `notebooks/` provide analysis tools:

- Count number of attempts and tries.
- Compute average reaction time overall and per attempt.
- Calculate accuracy (percentage of correct guesses).
- Visualize per-attempt vs overall accuracy with graphs.

## Installation

1. Clone this repository.
2. Create a virtual environment (recommended).
3. Install dependencies:

```bash
   pip install -r requirements.txt
```

4. Run the game:

```bash
python visualization.py
```

## Project Structure

```
Algorithm-Guessing-Game/
├─ visualization.py      # Main game loop & algorithm race visualization
├─ button.py             # Button logic & hover interactions
├─ timer.py              # Timing utilities for reaction tracking
├─ config.py             # Configuration (colors, speeds, layout)
├─ notebooks/            # Jupyter notebooks for data analysis
├─ data/                 # Session logs (ignored in Git)
├─ requirements.txt      # Python dependencies
└─ README.md             # Project documentation
```

## Configuration

- Modify `config.py` to adjust colors, sizes, or sorting speeds.
- Add or remove algorithms by editing the visualization logic.

## Adding New Algorithms

1. Implement the sorting function as a generator or yield-based routine.
2. Add it to the visualization script alongside existing algorithms.
3. Ensure the generator yields intermediate steps so animations can update.
4. Register it in the algorithm selection list.

## Example Analysis Workflow

1. Play several rounds to generate logs in `data/`.
2. Open Jupyter Notebook:

   ```bash
   jupyter notebook notebooks/
   ```

3. Load the relevant CSV file(s).
4. Run cells to compute:

   - Average reaction time
   - Accuracy percentage
   - Graphs comparing attempts

## Roadmap

- [x] Sorting race visualization with logging
- [x] Jupyter notebook analysis
- [ ] Add more algorithms (Heap, Shell, Radix, etc.)
- [ ] Adjustable difficulty (array size, order randomness)
- [ ] Results screen & in-game stats summary
- [ ] Configurable UI for quick parameter changes

## Refereneces

- W3Schools. (n.d.). Data Structures and Algorithms (DSA). Retrieved September 13, 2025, from https://www.w3schools.com/dsa/
- Pygame documentation: https://www.pygame.org/docs/

---

**Note:** README content was generated with assistance from _ChatGPT_ for formatting, structure, and citations.
