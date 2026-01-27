from bank_core import Ledger, min_cash_flow_settlement, normalize_player_name


def test_normalize_player_name_trims_whitespace():
    assert normalize_player_name("  Alex  ") == "Alex"


def test_ledger_totals_and_balances():
    ledger = Ledger()
    ledger.add_buyin("Alex", 20)
    ledger.add_buyin("Bri", 10)
    ledger.add_cashout("Alex", 5)
    ledger.add_cashout("Bri", 25)

    assert ledger.total_buyin() == 30.0
    assert ledger.total_cashout() == 30.0

    balances = ledger.balances(["Alex", "Bri", "Casey"])
    assert balances["Alex"] == -15.0
    assert balances["Bri"] == 15.0
    assert balances["Casey"] == 0.0


def test_min_cash_flow_settlement_balances_to_zero():
    balances = {"Alex": -15.0, "Bri": 15.0, "Casey": 0.0}
    transfers = min_cash_flow_settlement(balances)

    assert transfers == [("Alex", "Bri", 15.0)]
