import io
from datetime import datetime

import streamlit as st
import kociemba

# Fixed standard colour scheme. The solver input is always URFDLB.
FACE_ORDER = ["U", "R", "F", "D", "L", "B"]
FACE_NAMES = {
    "U": "Up",
    "R": "Right",
    "F": "Front",
    "D": "Down",
    "L": "Left",
    "B": "Back",
}
FACE_COLOURS = {
    "U": "White",
    "R": "Red",
    "F": "Green",
    "D": "Yellow",
    "L": "Orange",
    "B": "Blue",
}
COLOUR_EMOJI = {
    "White": "⬜",
    "Red": "🟥",
    "Green": "🟩",
    "Yellow": "🟨",
    "Orange": "🟧",
    "Blue": "🟦",
}
COLOURS = list(COLOUR_EMOJI.keys())


def move_explanation(move: str) -> str:
    face = move[0]
    suffix = move[1:]
    face_name = FACE_NAMES[face]
    if suffix == "'":
        return f"{face_name} face: turn counterclockwise (↺)"
    if suffix == "2":
        return f"{face_name} face: turn 180° (↻ twice)"
    return f"{face_name} face: turn clockwise (↻)"


def make_pdf(solution, cube_string):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError as exc:
        raise RuntimeError("PDF support is unavailable. Install reportlab using pip.") from exc

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
st.write("Enter the colours on your cube, solve it, and follow the moves one step at a time.")

with st.expander("How to enter your cube", expanded=True):
    st.markdown(
        """
        1. Hold the cube with the **white centre on top** and the **green centre facing you**.
        2. Enter the nine sticker colours for each face below. The centre sticker is fixed.
        3. Enter every face as you look directly at that face.
        4. Each colour must appear exactly nine times across the whole cube.

        Standard colour layout used here: **Up = White, Right = Red, Front = Green,
        Down = Yellow, Left = Orange, Back = Blue.**
        """
    )

st.info("This first web version uses manual colour entry. Webcam scanning can be added after the online solver is working.")

if "cube_values" not in st.session_state:
    st.session_state.cube_values = {
        face: [FACE_COLOURS[face] if i == 4 else FACE_COLOURS[face] for i in range(9)]
        for face in FACE_ORDER
    }

tabs = st.tabs([f"{face} · {FACE_NAMES[face]}" for face in FACE_ORDER])
for face, tab in zip(FACE_ORDER, tabs):
    with tab:
        st.subheader(f"{FACE_NAMES[face]} face")
        st.caption(f"Centre colour: {FACE_COLOURS[face]}. The centre cannot be changed.")
        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                index = row * 3 + col
                key = f"{face}_{index}"
                if key not in st.session_state:
                    st.session_state[key] = st.session_state.cube_values[face][index]
                if index == 4:
                    cols[col].text_input(
                        f"Sticker {index + 1}",
                        value=f"{COLOUR_EMOJI[FACE_COLOURS[face]]} {FACE_COLOURS[face]} (centre)",
                        disabled=True,
                        key=f"{key}_centre",
                    )
                    st.session_state.cube_values[face][index] = FACE_COLOURS[face]
                else:
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

with st.expander("Sticker count check", expanded=False):
    count_cols = st.columns(6)
    for col, colour in zip(count_cols, COLOURS):
        col.metric(f"{COLOUR_EMOJI[colour]} {colour}", counts[colour], "Need 9" if counts[colour] != 9 else "Correct")

def build_facelet_string():
    # kociemba requires facelets in URFDLB order. Each fixed centre colour
    # maps to its corresponding face letter.
    colour_to_face = {FACE_COLOURS[face]: face for face in FACE_ORDER}
    return "".join(colour_to_face[colour] for face in FACE_ORDER for colour in st.session_state.cube_values[face])


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
    st.error(
        "The entered stickers do not describe a valid, solvable cube. "
        "Recheck the face orientation and sticker colours, then try again."
    )
    with st.expander("Technical detail"):
        st.code(st.session_state.solve_error)

if st.session_state.get("solution_moves"):
    moves = st.session_state.solution_moves
    st.success(f"Solution found: {len(moves)} moves")
    st.subheader("Your solution")
    st.code(" ".join(moves), language="text")

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    st.markdown("### Follow the moves")
    if not moves:
        st.success("Your cube is already solved.")
    else:
        current = st.session_state.current_step
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
        st.caption("Clockwise and counterclockwise are judged while looking directly at the face being turned.")

    with st.expander("All move instructions"):
        for index, move in enumerate(moves, 1):
            st.write(f"**{index}. {move}**: {move_explanation(move)}")

    try:
        pdf_bytes = make_pdf(moves, st.session_state.cube_input)
        st.download_button(
            "📄 Download solution as PDF",
            data=pdf_bytes,
            file_name="rubiks_cube_solution.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except RuntimeError as exc:
        st.warning(str(exc))

st.divider()
st.caption("Rubik's Cube Solver · Built with Streamlit and the Kociemba two-phase solver.")
