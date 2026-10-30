# Rubik's Cube Solver

A browser-based Rubik's Cube solver built with Streamlit and the Kociemba two-phase solving algorithm.

## Features

- Browser camera capture for each of the six cube faces
- Approximate 3×3 sticker colour sampling from each captured image
- Manual correction of detected sticker colours
- Manual colour entry remains available
- Sticker count validation (nine of each colour)
- Cube validity checking through Kociemba
- Step-by-step, child-friendly move explanations
- Previous/Next move navigation
- PDF solution export

## Important note about camera scanning

The camera feature is an assisted scanner, not a fully automatic cube-recognition system. It samples nine positions from the central square of each photograph. For best results:

1. Capture one face at a time.
2. Hold the face straight toward the camera.
3. Centre the face in the camera preview and make it fill most of the square.
4. Use bright, even white lighting. Avoid shadows and glare.
5. Review and correct all nine colours after each capture.
6. Keep the cube orientation consistent with the colour scheme below.

The centre sticker is fixed to the expected face colour.

## Standard colour scheme and face order

The solver uses face order `U, R, F, D, L, B`.

| Face | Colour |
|---|---|
| Up (U) | White |
| Right (R) | Red |
| Front (F) | Green |
| Down (D) | Yellow |
| Left (L) | Orange |
| Back (B) | Blue |

Hold the cube with white on top and green facing you. If your physical cube uses a different colour arrangement, the mapping in `app.py` must be changed.

## Run locally on Windows

1. Install Python 3.10 or newer.
2. Extract this folder.
3. Open the folder in Visual Studio Code.
4. Open Terminal in VS Code.
5. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python -m streamlit run app.py
   ```

7. Open the local address shown in the terminal, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push these files to your GitHub repository.
2. Sign in at https://share.streamlit.io/ using GitHub.
3. Select **Create app**.
4. Choose your repository, branch, and `app.py` as the main file.
5. Select **Deploy**.

Streamlit reads `requirements.txt` and installs the listed packages.

## Updating the website

Edit `app.py` locally, test it, then commit and push your changes to GitHub. Streamlit Community Cloud detects the new commit and redeploys the app.
