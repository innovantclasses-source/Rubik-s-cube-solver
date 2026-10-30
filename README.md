# Rubik's Cube Solver

A browser-based Rubik's Cube solver built with Streamlit and the Kociemba two-phase solving algorithm.

## Features

- Manual entry of all six cube faces
- Fixed standard colour scheme and centre stickers
- Sticker count validation (nine of each colour)
- Cube validity checking through Kociemba
- Step-by-step, child-friendly move explanations
- Previous/Next move navigation
- PDF solution export

> Webcam scanning is not included in this starter version. It can be added as a later enhancement after the manual-entry solver is deployed and tested.

## Run locally on Windows

1. Install Python 3.10 or newer.
2. Extract this folder.
3. Open the folder in Visual Studio Code.
4. Open Terminal in VS Code.
5. Install the libraries:

   ```bash
   python -m pip install -r requirements.txt
   ```

6. Start the app:

   ```bash
   python -m streamlit run app.py
   ```

7. Streamlit will open the app in your browser. If it does not, open the local URL shown in the terminal, usually `http://localhost:8501`.

## Upload to GitHub

1. Create a new, empty GitHub repository named `rubiks-cube-solver`.
2. Extract this ZIP file.
3. Upload the four files and the `.gitignore` file from this folder to the repository's root.
4. Commit the upload.

## Deploy on Streamlit Community Cloud

1. Sign in at https://share.streamlit.io/ using your GitHub account.
2. Select **Create app**.
3. Choose the `rubiks-cube-solver` repository and the branch you uploaded to.
4. Set the main file path to `app.py`.
5. Select **Deploy**.

Streamlit reads `requirements.txt` and installs the listed packages during deployment.

## Updating the website

Edit `app.py` locally, test it, then commit and push the changes to GitHub. Streamlit Community Cloud will detect the new commit and redeploy the app.

## Cube entry orientation

Enter each face while looking directly at that face. The face order used internally is `U, R, F, D, L, B`.

The fixed colour scheme is:

| Face | Colour |
|---|---|
| Up (U) | White |
| Right (R) | Red |
| Front (F) | Green |
| Down (D) | Yellow |
| Left (L) | Orange |
| Back (B) | Blue |

The centre sticker of each face is fixed. Make sure the physical cube uses this standard colour arrangement. If the cube has a different colour scheme, this starter app needs its colour mapping adjusted before use.
