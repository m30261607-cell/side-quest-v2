import json
import random
import time
from pathlib import Path
from datetime import date

import streamlit as st
from cards import CARDS

# --- config ---
st.set_page_config(page_title="Side Quest", page_icon="🕹️", layout="centered")

STATE_FILE = Path("state.json")

# --- persistent state (recent cards, streak) ---
def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"recent": [], "done_dates": []}

def save_state(s):
    STATE_FILE.write_text(json.dumps(s))

state = load_state()

# --- pick a card, avoiding last 8 ---
def pick_card():
    pool = [c for c in CARDS if c["id"] not in state["recent"]]
    if not pool:
        pool = CARDS
    card = random.choice(pool)
    state["recent"].append(card["id"])
    state["recent"] = state["recent"][-8:]
    save_state(state)
    return card

# --- session state ---
if "card" not in st.session_state:
    st.session_state.card = pick_card()
if "started_at" not in st.session_state:
    st.session_state.started_at = None

# --- UI ---
st.markdown("<h1 style='text-align:center;'>Side Quest</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:gray;'>A tiny reset for a busy brain.</p>", unsafe_allow_html=True)
st.write("")

card = st.session_state.card

# Category badge
st.markdown(
    f"<p style='text-align:center; font-size:14px; color:#7a8c7a; font-weight:bold; letter-spacing:1px;'>"
    f"{card['category'].upper()}</p>",
    unsafe_allow_html=True,
)

# The card text
st.markdown(
    f"<div style='padding:32px; border-radius:16px; background:#f4f1ea; color:#2c2c2c; "
    f"font-size:22px; text-align:center; line-height:1.4; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>{card['text']}</div>",
    unsafe_allow_html=True,
)

# NEW: The description text
st.markdown(
    f"<p style='text-align:center; color:gray; font-size:15px; padding:0 20px;'>{card.get('description', '')}</p>",
    unsafe_allow_html=True,
)

st.write("")

# --- TIMER LOGIC ---
# We use st.empty() so the timer can tick without erasing the buttons below it
timer_placeholder = st.empty()
controls_placeholder = st.empty()

if st.session_state.started_at is None:
    with controls_placeholder.container():
        if st.button("▶ Start timer", use_container_width=True):
            st.session_state.started_at = time.time()
            st.rerun()
else:
    # While timer is running, show the ticking clock
    elapsed = time.time() - st.session_state.started_at
    remaining = max(0, card["seconds"] - int(elapsed))
    
    with timer_placeholder.container():
        st.markdown(
            f"<h2 style='text-align:center; color:#8fbc8f;'>{remaining}s</h2>",
            unsafe_allow_html=True,
        )
        
    with controls_placeholder.container():
        # Added a pause button so users don't have to use Streamlit's top-right stop button
        if st.button("⏸ Pause Timer", use_container_width=True):
            st.session_state.started_at = None
            st.rerun()
            
    if remaining == 0:
        with timer_placeholder.container():
            st.success("Quest complete. Notice how that felt.")
    else:
        # This creates a smooth countdown without destroying the buttons
        time.sleep(1)
        st.rerun()

st.write("")

# --- ACTIONS (Done / Swap) ---
# Because the timer is isolated, these buttons will never disappear while the timer runs!
col1, col2 = st.columns(2)
with col1:
    if st.button("✓ Done", use_container_width=True):
        today = date.today().isoformat()
        if today not in state["done_dates"]:
            state["done_dates"].append(today)
        save_state(state)
        st.session_state.card = pick_card()
        st.session_state.started_at = None
        st.balloons()
        st.rerun()

with col2:
    if st.button("↻ Swap", use_container_width=True):
        st.session_state.card = pick_card()
        st.session_state.started_at = None
        st.rerun()

# Streak
st.write("---")
streak = len(state["done_dates"])
st.markdown(
    f"<p style='text-align:center; color:gray; font-size:14px;'>"
    f"{streak} Side Quests completed so far.</p>",
    unsafe_allow_html=True,
)