from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class Player:
    name: str
    active: bool = True


@dataclass
class Ledger:
    """Tracks money flows per player."""

    buyins: Dict[str, float] = field(default_factory=dict)
    cashouts: Dict[str, float] = field(default_factory=dict)

    def add_buyin(self, player: str, amount: float) -> None:
        self.buyins[player] = self.buyins.get(player, 0.0) + float(amount)

    def set_cashout(self, player: str, amount: float) -> None:
        """Replace the player's cash-out with an absolute amount."""
        self.cashouts[player] = float(amount)

    def add_cashout(self, player: str, amount: float) -> None:
        """Add (increment) to the player's existing cash-out total."""
        self.cashouts[player] = self.cashouts.get(player, 0.0) + float(amount)

    def total_buyin(self) -> float:
        return float(sum(self.buyins.values()))

    def total_cashout(self) -> float:
        return float(sum(self.cashouts.values()))

    def balances(self, all_players: List[str]) -> Dict[str, float]:
        """
        Net balance for each player: cash_out - total_buy_in.
        Positive => others owe them; Negative => they owe others.
        Players with no entries are treated as 0 buyin & 0 cashout.
        """
        bal: Dict[str, float] = {}
        for player in all_players:
            buyin = self.buyins.get(player, 0.0)
            cashout = self.cashouts.get(player, 0.0)
            bal[player] = round(cashout - buyin, 2)
        return bal


def min_cash_flow_settlement(balances: Dict[str, float]) -> List[Tuple[str, str, float]]:
    """
    Given dict: name -> net (positive: is owed money; negative: owes money),
    return list of transfers (debtor -> creditor, amount) that settle all balances.

    Greedy approach:
    - Repeatedly match the most negative with the most positive balance.
    - Transfer min(abs(neg), pos). Update and continue until all within epsilon.
    """
    eps = 1e-9
    debtors: List[Tuple[str, float]] = []
    creditors: List[Tuple[str, float]] = []

    for name, net in balances.items():
        if net < -eps:
            debtors.append((name, net))
        elif net > eps:
            creditors.append((name, net))

    # Sort: debtors ascending (most negative first), creditors descending (most positive first)
    debtors.sort(key=lambda x: x[1])  # more negative first
    creditors.sort(key=lambda x: x[1], reverse=True)  # more positive first

    i = 0
    j = 0
    transfers: List[Tuple[str, str, float]] = []

    while i < len(debtors) and j < len(creditors):
        debtor_name, debtor_amt = debtors[i]
        creditor_name, creditor_amt = creditors[j]

        pay = round(min(-debtor_amt, creditor_amt), 2)
        if pay > 0:
            transfers.append((debtor_name, creditor_name, pay))
            debtor_amt += pay  # debtor_amt is negative
            creditor_amt -= pay

        # Move pointers
        if debtor_amt >= -eps:
            i += 1
        else:
            debtors[i] = (debtor_name, debtor_amt)

        if creditor_amt <= eps:
            j += 1
        else:
            creditors[j] = (creditor_name, creditor_amt)

    return transfers


def normalize_player_name(name: str) -> str:
    return name.strip()
