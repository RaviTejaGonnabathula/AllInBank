# ♠️ AllInBank – Poker Bank & Settlement App

>  A modern Streamlit-based app to track poker game finances: buy-ins, rebuys, cash-outs, and compute minimal settlements. Save & load games, visualize results, and export snapshots — perfect for home games or poker nights with friends.

---

*Track your poker sessions with clean charts and settle up quickly.*

---

##  Features

-  **Track Buy‑ins, Rebuys, Cash‑outs**
-  **Settle balances fairly** — automatic minimal transfers
-  **Save/Load games** (JSON format)
-  **Charts** for Buy-ins & Net Balances
-  **Export** game summary to CSV or JSON
-  **Currency** symbol customization
-  **Simple, clean UI** — no setup or login needed

---

##  Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/RaviTejaGonnabathula/poker-bank-app.git
cd poker-bank-app

### 2. Create & activate virtual environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt


### 4. Run the Streamlit app
streamlit run poker_bank_app.py
