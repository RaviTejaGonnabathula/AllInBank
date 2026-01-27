"""
Poker Bank App — Streamlit (with Save/Load, dropdown cash‑outs, and charts)
--------------------------------------------------------------------------
Track poker chips as money (buy‑ins, rebuys/top‑ups, cash‑outs) and compute minimal
settlement (who owes whom how much). Now includes:

- Save/Load games to resume later (JSON files on disk)
- Option to **start a new game** or **continue a previous game**
- Cash‑outs via **dropdown selector** (one player at a time)
- Simple, clear **charts** (buy‑ins & net results) + existing tables

Run
- Save this file as `poker_bank_app.py`
- `pip install streamlit pandas altair`
- `streamlit run poker_bank_app.py`

Notes
- Currency is configurable (defaults to $).
- Saves are stored under a `poker_bank_saves/` folder near this script.
"""

from __future__ import annotations
import json
from typing import Dict
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import altair as alt

from bank_core import Ledger, Player, min_cash_flow_settlement, normalize_player_name

# ----------------------------
# Save/Load helpers
# ----------------------------

SAVE_DIR = Path.cwd() / "poker_bank_saves"
SAVE_DIR.mkdir(exist_ok=True)

def _safe_filename(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name.strip())


def save_current_game():
    if "players" not in st.session_state or "ledger" not in st.session_state or "settings" not in st.session_state:
        st.error("Nothing to save yet.")
        return
    players: Dict[str, Player] = st.session_state.players
    ledger: Ledger = st.session_state.ledger
    settings: Dict[str, object] = st.session_state.settings

    payload = {
        "meta": {
            "saved_at": datetime.now().isoformat(),
            "app_version": 1
        },
        "settings": settings,
        "players": {name: {"name": p.name, "active": p.active} for name, p in players.items()},
        "ledger": {
            "buyins": ledger.buyins,
            "cashouts": ledger.cashouts,
        },
    }
    fname = _safe_filename(str(settings.get("game_name", "home_game"))) + ".json"
    fpath = SAVE_DIR / fname
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    st.toast(f"Saved game to {fpath.name}")


def load_game(filename: str):
    fpath = SAVE_DIR / filename
    if not fpath.exists():
        st.error("Save file not found.")
        return
    with open(fpath, "r", encoding="utf-8") as f:
        data = json.load(f)

    settings = data.get("settings", {})
    players_raw = data.get("players", {})
    ledger_raw = data.get("ledger", {})

    st.session_state.settings = settings
    st.session_state.players = {name: Player(**attrs) for name, attrs in players_raw.items()}
    led = Ledger()
    led.buyins = {k: float(v) for k, v in ledger_raw.get("buyins", {}).items()}
    led.cashouts = {k: float(v) for k, v in ledger_raw.get("cashouts", {}).items()}
    st.session_state.ledger = led

# ----------------------------
# Streamlit UI
# ----------------------------

st.set_page_config(page_title="AllInBank", page_icon="♠️", layout="wide")

# Init session state
if "players" not in st.session_state:
    st.session_state.players: Dict[str, Player] = {}
if "ledger" not in st.session_state:
    st.session_state.ledger = Ledger()
if "settings" not in st.session_state:
    st.session_state.settings = {
        "currency": "$",
        "default_buyin": 10.0,
        "game_name": f"Home Game {datetime.now().strftime('%Y-%m-%d')}"
    }

players: Dict[str, Player] = st.session_state.players
ledger: Ledger = st.session_state.ledger
settings: Dict[str, object] = st.session_state.settings

# Sidebar controls for Save/Load
st.sidebar.header("♠️ Menu")
mode = st.sidebar.radio("Mode", ["Start new game", "Continue from save"], horizontal=False)

if mode == "Start new game":
    new_name = st.sidebar.text_input("New game name", value=str(settings.get("game_name", "Home Game")), key="sb_game_name")
    default_buyin = st.sidebar.number_input("Default buy‑in", min_value=1.0, step=1.0, value=float(settings.get("default_buyin", 10.0)), key="sb_default_buyin")
    currency = st.sidebar.text_input("Currency symbol", value=str(settings.get("currency", "$")), key="sb_currency")
    if st.sidebar.button("Start New", use_container_width=True):
        st.session_state.players = {}
        st.session_state.ledger = Ledger()
        st.session_state.settings = {
            "currency": currency or "$",
            "default_buyin": float(default_buyin),
            "game_name": new_name or f"Home Game {datetime.now().strftime('%Y-%m-%d')}"
        }
        st.sidebar.success("Started new game")
else:
    saves = sorted([p.name for p in SAVE_DIR.glob("*.json")])
    if not saves:
        st.sidebar.info("No saves yet — start a new game first.")
    else:
        sel = st.sidebar.selectbox("Choose a save", options=saves)
        load_cols = st.sidebar.columns(2)
        if load_cols[0].button("Load", use_container_width=True, disabled=not sel):
            load_game(sel)
        if load_cols[1].button("Save current", use_container_width=True):
            save_current_game()

# Always show a quick save option
st.sidebar.button("💾 Save now", use_container_width=True, on_click=save_current_game)

# Header
colA, colB = st.columns([0.7, 0.3])
with colA:
    st.title("♠️ AllInBank")
    st.caption("Track buy‑ins, rebuys, and cash‑outs. Save/Load and settle cleanly.")
with colB:
    settings["game_name"] = st.text_input("Game name", value=str(settings["game_name"]), key="hdr_game_name")
    settings["currency"] = st.text_input("Currency symbol", value=str(settings["currency"]), key="hdr_currency")

st.divider()

# Player management
st.subheader("1) Players")
add_col1, add_col2 = st.columns([0.6, 0.4])
with add_col1:
    new_name = st.text_input("Add player name", placeholder="e.g., Alex")
with add_col2:
    if st.button("Add Player", use_container_width=True):
        normalized_name = normalize_player_name(new_name)
        if not normalized_name:
            st.warning("Please enter a player name.")
        elif normalized_name in players:
            st.warning(f"Player '{normalized_name}' already exists.")
        else:
            players[normalized_name] = Player(name=normalized_name)
            st.success(f"Added player {normalized_name}.")

if players:
    names = list(players.keys())
    df_players = pd.DataFrame({
        "Player": names,
        "Active": [players[n].active for n in names],
        "Total Buy‑in": [ledger.buyins.get(n, 0.0) for n in names],
        "Cash‑out": [ledger.cashouts.get(n, 0.0) for n in names],
    })
    st.dataframe(df_players, use_container_width=True, hide_index=True)
else:
    st.info("Add a few players to get started.")

st.divider()

# Buy‑ins / Rebuys
st.subheader("2) Buy‑ins & Rebuys")
if not players:
    st.info("Add players first.")
else:
    bcol1, bcol2, bcol3 = st.columns([0.5, 0.25, 0.25])
    with bcol1:
        sel_player = st.selectbox("Player", options=list(players.keys()), key="buyin_player")
    with bcol2:
        amt = float(st.number_input("Amount", min_value=0.0, step=5.0, value=float(settings["default_buyin"])) )
    with bcol3:
        if st.button("Record Buy‑in / Rebuy", use_container_width=True):
            ledger.add_buyin(sel_player, amt)
            st.success(f"Recorded {settings['currency']}{amt:.2f} buy‑in for {sel_player}.")

    # running ledger view
    if ledger.buyins:
        df_b = pd.DataFrame(sorted(ledger.buyins.items()), columns=["Player", "Total Buy‑in"])
        st.dataframe(df_b, use_container_width=True, hide_index=True)

    # Chart: Buy‑ins per player
    if ledger.buyins:
        st.markdown("**Buy‑ins per player**")
        df_b_plot = pd.DataFrame({"Player": list(ledger.buyins.keys()), "Buyin": list(ledger.buyins.values())})
        chart_b = (
            alt.Chart(df_b_plot)
            .mark_bar()
            .encode(x=alt.X("Player:N", sort="-y"), y=alt.Y("Buyin:Q"), tooltip=["Player", "Buyin"])
            .properties(height=280, width=400)
        )
        st.altair_chart(chart_b, use_container_width=True)

st.divider()

# Cash‑outs (Dropdown entry per player)
st.subheader("3) End-of-Game Cash-outs")
if not players:
    st.info("Add players first.")
else:
    cc0 = st.columns([1.0])[0]
    with cc0:
        co_mode = st.radio(
            "Cash-out mode",
            ["Add to existing (increment)", "Replace (set absolute)"],
            horizontal=True,
            key="cashout_mode",
        )

    cc1, cc2, cc3 = st.columns([0.5, 0.25, 0.25])
    with cc1:
        sel_player_co = st.selectbox("Select player", options=list(players.keys()), key="cashout_player")
    with cc2:
        current_total = float(ledger.cashouts.get(sel_player_co, 0.0))
        default_val = 0.0 if co_mode.startswith("Add") else current_total
        amt_co = float(
            st.number_input(
                "Cash-out amount",
                min_value=0.0,
                step=5.0,
                value=default_val,
                key="cashout_amount",
            )
        )
    with cc3:
        if co_mode.startswith("Add"):
            if st.button("Add Cash-out", use_container_width=True, key="btn_add_cashout"):
                ledger.add_cashout(sel_player_co, amt_co)
                new_total = ledger.cashouts.get(sel_player_co, 0.0)
                st.success(
                    f"Added {settings['currency']}{amt_co:.2f} for {sel_player_co}. Total cash-out is now {settings['currency']}{new_total:.2f}."
                )
        else:
            if st.button("Set Cash-out", use_container_width=True, key="btn_set_cashout"):
                ledger.set_cashout(sel_player_co, amt_co)
                st.success(
                    f"Set cash-out for {sel_player_co} to {settings['currency']}{amt_co:.2f}."
                )

    st.caption(
        f"Current recorded cash-out for {sel_player_co}: {settings['currency']}{current_total:.2f}. "
        + ("Adding will increment this total." if co_mode.startswith("Add") else "Setting will replace this total.")
    )

    # Table of all cash-outs
    df_cash = (
        pd.DataFrame(sorted(ledger.cashouts.items()), columns=["Player", "Cash-out"])
        if ledger.cashouts else
        pd.DataFrame(columns=["Player", "Cash-out"])
    )
    st.dataframe(df_cash, use_container_width=True, hide_index=True)

    # Totals sanity check
    total_in = ledger.total_buyin()
    total_out = ledger.total_cashout()
    delta = round(total_out - total_in, 2)
    if abs(delta) > 0.009:
        st.warning(
            f"⚠️ Totals don't match. "
            f"Buy-ins: {settings['currency']}{total_in:.2f} vs "
            f"Cash-outs: {settings['currency']}{total_out:.2f}. "
            f"Difference: {settings['currency']}{delta:.2f}"
        )
    else:
        st.success(
            f"Totals match ✔ Buy-ins = {settings['currency']}{total_in:.2f}, "
            f"Cash-outs = {settings['currency']}{total_out:.2f}"
        )

st.divider()


# Settlement
st.subheader("4) Settlement — Who owes whom?")
if players:
    all_names = list(players.keys())
    bals = ledger.balances(all_names)
    df_bal = pd.DataFrame([{ "Player": k, "Net": v } for k, v in bals.items()])
    df_bal.sort_values("Net", ascending=False, inplace=True)

    cols1, cols2 = st.columns([0.5, 0.5])
    with cols1:
        st.markdown("**Net per player** (\+ means should receive, − means should pay)")
        st.dataframe(df_bal, use_container_width=True, hide_index=True)

        # Chart: Net per player
        if not df_bal.empty:
            chart_net = (
                alt.Chart(df_bal)
                .mark_bar()
                .encode(x=alt.X("Player:N", sort=None), y=alt.Y("Net:Q"), color=alt.condition("datum.Net >= 0", alt.value("#4caf50"), alt.value("#f44336")), tooltip=["Player", "Net"])
                .properties(height=300)
            )
            st.altair_chart(chart_net, use_container_width=True)

    transfers = min_cash_flow_settlement(bals)
    with cols2:
        st.markdown("**Minimal transfers** to settle:")
        if not transfers:
            st.info("No transfers needed. Everyone is square.")
        else:
            df_t = pd.DataFrame(transfers, columns=["From (debtor)", "To (creditor)", "Amount"])
            st.dataframe(df_t, use_container_width=True, hide_index=True)

    # Export buttons
    st.subheader("Export")
    export_payload = {
        "game_name": settings["game_name"],
        "currency": settings["currency"],
        "created_at": datetime.now().isoformat(),
        "players": list(players.keys()),
        "buyins": ledger.buyins,
        "cashouts": ledger.cashouts,
        "balances": bals,
        "transfers": transfers,
        "total_buyin": ledger.total_buyin(),
        "total_cashout": ledger.total_cashout(),
    }

    json_bytes = json.dumps(export_payload, indent=2).encode("utf-8")
    st.download_button(
        label="Download JSON snapshot",
        data=json_bytes,
        file_name=f"{str(settings['game_name']).replace(' ', '_').lower()}_snapshot.json",
        mime="application/json",
        use_container_width=True,
    )

    # CSV exports
    df_buyins = pd.DataFrame(sorted(ledger.buyins.items()), columns=["Player", "Total_Buyin"]) if ledger.buyins else pd.DataFrame(columns=["Player","Total_Buyin"]) 
    df_cashouts = pd.DataFrame(sorted(ledger.cashouts.items()), columns=["Player", "Cashout"]) if ledger.cashouts else pd.DataFrame(columns=["Player","Cashout"]) 
    df_transfers = pd.DataFrame(transfers, columns=["From","To","Amount"]) if transfers else pd.DataFrame(columns=["From","To","Amount"]) 

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button("Buy‑ins CSV", df_buyins.to_csv(index=False).encode("utf-8"), "buyins.csv", "text/csv", use_container_width=True)
    with c2:
        st.download_button("Cash‑outs CSV", df_cashouts.to_csv(index=False).encode("utf-8"), "cashouts.csv", "text/csv", use_container_width=True)
    with c3:
        st.download_button("Transfers CSV", df_transfers.to_csv(index=False).encode("utf-8"), "transfers.csv", "text/csv", use_container_width=True)

# Footer
st.divider()
st.caption("Pro tip: Save early and often. You can resume any saved game from the sidebar.")
