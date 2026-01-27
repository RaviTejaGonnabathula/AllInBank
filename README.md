# ♠️ AllInBank – Poker Bank & Settlement App

>  A modern Streamlit-based app to track poker game finances: buy-ins, rebuys, cash-outs, and compute minimal settlements. Save & load games, visualize results, and export snapshots — perfect for home games or poker nights with friends.

---
Access the app : [AllInBank](https://allinbank-jcbud6hkcut7jpyzp2spzn.streamlit.app/)
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
git clone https://github.com/RaviTejaGonnabathula/AllInBank.git
cd AllInBank
```
### 2. Create & activate virtual environment

```
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run the Streamlit app
```
streamlit run AllInBank.py
```

### 5. Run the unit tests
```
pytest -q
```

## 🛠 Tech Stack

| Component   | Description              |
|-------------|--------------------------|
| Streamlit   | Interactive Web UI       |
| Pandas      | Data manipulation        |
| Altair      | Charts & visualizations  |
| JSON        | Save/Load game states    |
| Pytest      | Unit testing             |

---

##  How It Works

1. **Start a New Game** or **Load Previous Save**  
2. Add players → Record buy-ins and cash-outs  
3. Automatically compute net balances per player  
4. Use **Greedy Min-Cash-Flow** algorithm to settle debts  
5. **Download** game summary as `.json` or `.csv`  

The core money flow logic (ledger, settlement, name normalization) lives in
`bank_core.py` and is imported by the Streamlit UI so it can be tested independently.


---

##  Save & Load

- Auto-saves stored in: `poker_bank_saves/` folder  
- Game name → becomes filename (e.g., `home_game.json`)  
- Easily reload previous games from the sidebar  

---

##  Visualizations

- Bar chart of **Total Buy-ins**  
- Bar chart of **Net Position** (+ve means others owe)  
- Table of **Minimal Transfers** to settle the game  

---

##  Export Options

At the end of any game, export your data:

-  `snapshot.json` – All data including players, ledger, transfers  
-  `buyins.csv`, `cashouts.csv`, `transfers.csv` – Clean exports for sharing  

---

##  Example Use Case

You're hosting a poker night:

- Everyone buys in with chips  
- Some players rebuy  
- At the end, they cash out  

Use **AllInBank** to:  
- Record all entries  
- See who is up/down  
- View total in/out  
- Automatically calculate who owes how much  
- Export the result  

---


##  Contributing

Pull requests and ideas are welcome!  
To contribute:  
1. Fork the repo  
2. Create a feature branch  
3. Submit a pull request  

---

##  Author

Made with ♠️ by **Ravi Teja Gonnabathula**  
GitHub: [github.com/RaviTejaGonnabathula](https://github.com/RaviTejaGonnabathula)  
LinkedIn: [linkedin.com/in/ravitejagonnabathula](https://www.linkedin.com/in/ravitejagonnabathula)  


