import streamlit as st
from wordle_engine import WordleSession, load_word_list

# Map pattern letters to emoji (for messages / debugging)
COLOR_EMOJI = {
    "g": "🟩",
    "y": "🟨",
    "b": "⬛",
}


def inject_css():
    """Custom CSS to make the app look more like a polished Wordle helper."""
    st.markdown(
        """
        <style>
        /* Overall page tweaks */
        .main {
            background-color: #020617; /* slate-950 */
            color: #e5e7eb;            /* slate-200 */
        }
        .block-container {
            padding-top: 3rem;
            padding-bottom: 1.5rem;
        }

        /* Titles */
        h1, h2, h3, h4 {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
                         sans-serif;
        }

        /* Wordle-style board */
        .wordle-board {
            margin-top: 0.5rem;
            margin-bottom: 1rem;
        }
        .wordle-row {
            display: flex;
            gap: 0.35rem;
            margin-bottom: 0.3rem;
        }
        .wordle-tile {
            width: 3rem;
            height: 3rem;
            border-radius: 0.4rem;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.4rem;
            text-transform: uppercase;
            border: 1px solid #4b5563; /* slate-600 */
            box-shadow: 0 1px 2px rgba(0,0,0,0.6);
        }
        .tile-grey {
            background-color: #020617; /* slate-950 */
            color: #e5e7eb;
            border-color: #4b5563;
        }
        .tile-yellow {
            background-color: #facc15;
            color: #111827;
        }
        .tile-green {
            background-color: #22c55e;
            color: #052e16;
        }

        /* Candidate "pill" styling */
        .candidate-container {
            margin-top: 0.75rem;
            max-height: 420px;      /* scrollable area */
            overflow-y: auto;
            padding-right: 0.5rem;
        }
        .candidate-pill {
            display: inline-block;
            margin: 0.12rem 0.22rem;
            padding: 0.12rem 0.55rem;
            border-radius: 999px;
            background: #020617;
            border: 1px solid #1f2937;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
                         "Liberation Mono", "Courier New", monospace;
            font-size: 0.9rem;
            color: #e5e7eb;
            white-space: nowrap;
        }

        /* Streamlit form / widgets tweaks */
        .stTextInput > div > div > input {
            background-color: #020617 !important;
            color: #e5e7eb !important;
        }
        .stButton > button {
            border-radius: 999px;
            padding: 0.4rem 1.1rem;
            font-weight: 600;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    """Initialize all needed items in Streamlit's session_state."""
    if "word_list" not in st.session_state:
        st.session_state["word_list"] = load_word_list()

    if "session" not in st.session_state:
        st.session_state["session"] = WordleSession(st.session_state["word_list"])

    # 6 x 5 grid of colors, all starting as "b" (grey)
    if "color_grid" not in st.session_state:
        st.session_state["color_grid"] = [["b"] * 5 for _ in range(6)]

    # Which row of the grid we are currently filling (0–5)
    if "active_row" not in st.session_state:
        st.session_state["active_row"] = 0


def cycle_color(row: int, col: int):
    """Cycle a cell's color: b -> y -> g -> b."""
    colors = ["b", "y", "g"]
    current = st.session_state["color_grid"][row][col]
    idx = colors.index(current)
    next_color = colors[(idx + 1) % len(colors)]
    st.session_state["color_grid"][row][col] = next_color
    st.rerun()


def render_board(session: WordleSession):
    """Pretty, Wordle-style board using HTML/CSS tiles."""
    st.subheader("Guess Board")

    max_rows = 6
    html = ['<div class="wordle-board">']

    for i in range(max_rows):
        if i < len(session.history):
            gr = session.history[i]
            word = gr.word.upper()
            pattern = gr.pattern
        else:
            word = "     "  # 5 spaces for empty rows
            pattern = "bbbbb"

        html.append('<div class="wordle-row">')
        for j in range(5):
            letter = word[j] if j < len(word) and word[j] != " " else "&nbsp;"
            p = pattern[j]
            if p == "g":
                tile_class = "tile-green"
            elif p == "y":
                tile_class = "tile-yellow"
            else:
                tile_class = "tile-grey"

            html.append(
                f'<div class="wordle-tile {tile_class}">{letter}</div>'
            )
        html.append("</div>")  # end row

    html.append("</div>")  # end board
    st.markdown("\n".join(html), unsafe_allow_html=True)


def render_clickable_grid():
    """Clickable 6x5 grid for choosing colors (emoji buttons)."""
    st.subheader("Color Pattern Grid")

    active_row = st.session_state["active_row"]
    st.caption(f"Click squares on row {active_row + 1} to set Grey / Yellow / Green.")

    for r in range(6):
        cols = st.columns(5)
        for c in range(5):
            color = st.session_state["color_grid"][r][c]
            emoji = COLOR_EMOJI[color]

            # Only the active row is clickable; others are disabled
            disabled = (r != active_row)

            if cols[c].button(emoji, key=f"cell-{r}-{c}", disabled=disabled):
                cycle_color(r, c)


def render_candidates(candidates: list[str]):
    st.subheader("Remaining Candidates")
    st.write(f"Total candidates: **{len(candidates)}**")

    if not candidates:
        st.write("No candidates match the current guesses.")
        return

    # Pretty pill-style layout
    pills = ['<div class="candidate-container">']
    for w in candidates:
        pills.append(f'<span class="candidate-pill">{w}</span>')
    pills.append("</div>")

    st.markdown("\n".join(pills), unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Wordle Buster", page_icon="🧠", layout="wide")
    inject_css()
    init_state()

    session: WordleSession = st.session_state["session"]

st.markdown("### 🧠 Wordle Buster")
st.caption("A helper tool to narrow down Wordle candidates from your guesses.")

left_col, right_col = st.columns([2, 3])

with left_col:
    # TOP LEFT: Add Guess
    st.subheader("Add a Guess")

    with st.form("add_guess_form"):
        guess = st.text_input(
            "Guess word (5 letters):",
            max_chars=5,
            placeholder="e.g. crane",
        ).strip().lower()

        submitted = st.form_submit_button("Apply Guess")

    if submitted:
        if len(guess) != 5 or not guess.isalpha():
            st.error("Guess must be exactly 5 letters (A–Z).")
        else:
            row = st.session_state["active_row"]
            pattern = "".join(st.session_state["color_grid"][row])

            session.add_guess(guess, pattern)
            st.success(
                f"Added {guess.upper()} with pattern "
                f"{' '.join(COLOR_EMOJI[ch] for ch in pattern)} "
                f"({pattern})"
            )

            if row < 5:
                st.session_state["active_row"] = row + 1

            st.rerun()

    if st.button("Reset session"):
        st.session_state.clear()
        st.rerun()

    st.markdown("---")

    # BELOW: Color Pattern Grid
    render_clickable_grid()

with right_col:
    # TOP RIGHT: Guess Board
    render_board(session)

    # BELOW: Remaining Candidates
    candidates = session.get_candidates()
    render_candidates(candidates)

if __name__ == "__main__":
    main()
