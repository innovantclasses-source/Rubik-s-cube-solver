import io
from datetime import datetime

import numpy as np
import streamlit as st
from PIL import Image
import kociemba

FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
FACE_NAMES = {"U": "Up", "R": "Right", "F": "Front", "D": "Down", "L": "Left", "B": "Back"}
FACE_COLOURS = {"U": "White", "R": "Red", "F": "Green", "D": "Yellow", "L": "Orange", "B": "Blue"}
COLOUR_EMOJI = {
    "White": "⬜", "Red": "🟥", "Green": "🟩",
    "Yellow": "🟨", "Orange": "🟧", "Blue": "🟦",
}
COLOURS = list(COLOUR_EMOJI.keys())

# Approximate RGB reference colours. Camera detection is a starting estimate,
# not a substitute for reviewing the detected stickers.
REFERENCE_RGB = {
    "White": np.array([238, 238, 225], dtype=float),
    "Red": np.array([190, 35, 35], dtype=float),
    "Green": np.array([20, 135, 65], dtype=float),
    "Yellow": np.array([235, 210, 35], dtype=float),
    "Orange": np.array([235, 115, 20], dtype=float),
    "Blue": np.array([30, 75, 175], dtype=float),
}


def move_explanation(move: str) -> str:
    face = move[0]
    suffix = move[1:]
    name = FACE_NAMES[face]
    if suffix == "'":
        return f"{name} face: turn counterclockwise (↺)"
    if suffix == "2":
        return f"{name} face: turn 180° (↻ twice)"
    return f"{name} face: turn clockwise (↻)"


def detect_face_colours(uploaded_image):
    """Sample the centre of a 3x3 grid inside the central square of the photo."""
    image = Image.open(uploaded_image).convert("RGB")
    width, height = image.size
    side = min(width, height)
    left = (width - side) // 2
    top = (height - side) // 2
    image = image.crop((left, top, left + side, top + side)).resize((300, 300))
    pixels = np.asarray(image, dtype=np.float32)

    detected = []
    # Sample a small patch around each sticker centre, avoiding grid lines.
    for row in range(3):
        for col in range(3):
            cx = int((col + 0.5) * 100)
            cy = int((row + 0.5) * 100)
            patch = pixels[cy - 8:cy + 8, cx - 8:cx + 8]
            sample = np.median(patch.reshape(-1, 3), axis=0)
            distances = {
                colour: np.linalg.norm(sample - reference)
                for colour, reference in REFERENCE_RGB.items()
            }
            detected.append(min(distances, key=distances.get))
    return detected, image


def make_pdf(solution, cube_string):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Rubik's Cube Solver", styles["Title"]),
        Paragraph("Solution guide", styles["Heading2"]),
        Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Cube input (URFDLB)", styles["Heading2"]),
        Paragraph(cube_string, styles["Code"]),
        Spacer(1, 12),
        Paragraph("Move sequence", styles["Heading2"]),
        Paragraph(" ".join(solution), styles["BodyText"]),
        Spacer(1, 12),
        Paragraph("Move-by-move instructions", styles["Heading2"]),
    ]
    rows = [["Step", "Move", "What to do"]]
    for index, move in enumerate(solution, 1):
        rows.append([str(index), move, move_explanation(move)])
    table = Table(rows, colWidths=[45, 55, 390], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#26364A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F4F8")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


st.set_page_config(page_title="Rubik's Cube Solver", page_icon="🧩", layout="wide")
st.title("🧩 Rubik's Cube Solver")
st.write("Scan or enter the colours on your cube, solve it, and follow the moves one step at a time.")

with st.expander("Before you start: cube orientation", expanded=True):
    st.markdown(
        """
        - Hold the cube with **white on top** and **green facing you**.
        - The standard colour scheme is **Up = White, Right = Red, Front = Green,
          Down = Yellow, Left = Orange, Back = Blue**.
        - When scanning, point one face directly at the camera. Keep the whole 3×3 face
          centred and close enough to fill most of the square preview.
        - Use bright, even lighting. Avoid shadows, glare, and coloured lights.
        - The camera's colour guesses are approximate. **Review and correct every face before solving.**
        """
    )

if "cube_values" not in st.session_state:
    st.session_state.cube_values = {
        face: [FACE_COLOURS[face] for _ in range(9)] for face in FACE_ORDER
    }
if "solution_moves" not in st.session_state:
    st.session_state.solution_moves = None

st.header("1. Scan your cube")
st.caption("Capture each face separately. The app samples the nine sticker positions and then lets you correct the results.")
scan_tabs = st.tabs([f"{face} · {FACE_NAMES[face]}" for face in FACE_ORDER])

for face, tab in zip(FACE_ORDER, scan_tabs):
    with tab:
        st.write(f"Show the **{FACE_NAMES[face]} face** to the camera.")
        st.caption(f"Expected centre sticker: {FACE_COLOURS[face]}. The centre is fixed in the app.")
        photo = st.camera_input(f"Capture {FACE_NAMES[face]} face", key=f"camera_{face}")
        if photo is not None:
            try:
                detected, preview = detect_face_colours(photo)
                detected[4] = FACE_COLOURS[face]
                st.image(preview, caption="Central square used for colour sampling", width=300)
                if st.button(f"Use detected colours for {face}", key=f"use_scan_{face}"):
                    st.session_state.cube_values[face] = detected
                    for index, colour in enumerate(detected):
                        widget_key = f"{face}_{index}"
                        if widget_key in st.session_state:
                            del st.session_state[widget_key]
                    st.session_state.solution_moves = None
                    st.success(f"{FACE_NAMES[face]} face colours added. Review them in section 2.")
                    st.rerun()
            except Exception as exc:
                st.error(f"Could not read this photo: {exc}")

st.divider()
st.header("2. Review and correct all six faces")
st.warning("The camera uses a simple centre-grid colour sampler. It does not locate sticker boundaries automatically. Make sure the cube face is centred and check every detected colour below.")

edit_tabs = st.tabs([f"{face} · {FACE_NAMES[face]}" for face in FACE_ORDER])
for face, tab in zip(FACE_ORDER, edit_tabs):
    with tab:
        st.subheader(f"{FACE_NAMES[face]} face")
        st.caption(f"Centre sticker is fixed as {FACE_COLOURS[face]}.")
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                index = row * 3 + col
                key = f"{face}_{index}"
                current = st.session_state.cube_values[face][index]
                if index == 4:
                    cols[col].text_input(
                        f"Sticker {index + 1}",
                        value=f"{COLOUR_EMOJI[FACE_COLOURS[face]]} {FACE_COLOURS[face]} (centre)",
                        disabled=True,
                        key=f"{key}_centre",
                    )
                    st.session_state.cube_values[face][index] = FACE_COLOURS[face]
                else:
                    if key not in st.session_state:
                        st.session_state[key] = current
                    selected = cols[col].selectbox(
                        f"Sticker {index + 1}",
                        COLOURS,
                        index=COLOURS.index(st.session_state[key]),
                        format_func=lambda colour: f"{COLOUR_EMOJI[colour]} {colour}",
                        key=key,
                    )
                    st.session_state.cube_values[face][index] = selected

all_stickers = [colour for face in FACE_ORDER for colour in st.session_state.cube_values[face]]
counts = {colour: all_stickers.count(colour) for colour in COLOURS}
valid_counts = all(counts[colour] == 9 for colour in COLOURS)

with st.expander("Sticker count check", expanded=True):
    count_cols = st.columns(6)
    for col, colour in zip(count_cols, COLOURS):
        col.metric(f"{COLOUR_EMOJI[colour]} {colour}", counts[colour], "Need 9" if counts[colour] != 9 else "Correct")

def build_facelet_string():
    colour_to_face = {FACE_COLOURS[face]: face for face in FACE_ORDER}
    return "".join(colour_to_face[colour] for face in FACE_ORDER for colour in st.session_state.cube_values[face])


st.header("3. Solve the cube")
if st.button("Solve my cube", type="primary", use_container_width=True):
    if not valid_counts:
        st.error("The cube cannot be solved yet. Check that every colour appears exactly 9 times.")
    else:
        facelets = build_facelet_string()
        try:
            solution_text = kociemba.solve(facelets)
            st.session_state.solution_moves = solution_text.split()
            st.session_state.cube_input = facelets
            st.session_state.current_step = 0
            st.session_state.solve_error = None
        except Exception as exc:
            st.session_state.solution_moves = None
            st.session_state.solve_error = str(exc)

if st.session_state.get("solve_error"):
    st.error("The entered stickers do not describe a valid, solvable cube. Recheck the face orientation and sticker colours.")
    with st.expander("Technical detail"):
        st.code(st.session_state.solve_error)

if st.session_state.get("solution_moves") is not None:
    moves = st.session_state.solution_moves
    st.success(f"Solution found: {len(moves)} moves")
    st.subheader("Your solution")
    st.code(" ".join(moves) if moves else "Already solved", language="text")
    if moves:
        current = st.session_state.get("current_step", 0)
        left, middle, right = st.columns([1, 2, 1])
        with left:
            if st.button("← Previous", disabled=current <= 0, use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
        with right:
            if st.button("Next →", disabled=current >= len(moves) - 1, use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()
        with middle:
            st.metric("Move", f"{current + 1} of {len(moves)}")
        st.progress((current + 1) / len(moves))
        st.markdown(f"## {moves[current]}")
        st.subheader(move_explanation(moves[current]))
        with st.expander("All move instructions"):
            for index, move in enumerate(moves, 1):
                st.write(f"**{index}. {move}**: {move_explanation(move)}")
    else:
        st.success("Your cube is already solved.")
    pdf_bytes = make_pdf(moves, st.session_state.cube_input)
    st.download_button(
        "📄 Download solution as PDF",
        data=pdf_bytes,
        file_name="rubiks_cube_solution.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()
st.caption("Rubik's Cube Solver · Streamlit · Kociemba two-phase solver")
