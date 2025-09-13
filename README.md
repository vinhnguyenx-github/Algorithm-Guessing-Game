# Guessing Algorithm Game

An interactive game built with **Pygame** where players watch two sorting algorithm visualizations side by side and try to predict which one will finish first.

## 🎮 Gameplay
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

## ⚙️ Installation
1. Clone this repository.
2. Create a virtual environment (recommended).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
