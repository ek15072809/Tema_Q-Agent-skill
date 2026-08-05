"""stock_skill.py — Helpers for building stock-trading proposals.

Provides:
  * search_queries()   — ready-to-run websearch query templates (macro, sector,
                         ticker, valuation).
  * ticker_for()       — known tickers for major Japanese / US names.
  * Proposal dataclass — structured buy/sell proposal.
  * format_proposal()  — Markdown formatter for a Proposal.
  * format_report()    — Top-level Markdown report with N proposals.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal, Sequence


Action   = Literal["BUY", "SELL", "HOLD"]
RiskLvl  = Literal["conservative", "balanced", "aggressive"]


# ---- Known tickers --------------------------------------------------------

_JP_TICKERS = {
    "toyota": "7203.T", "sony": "6758.T", "softbank group": "9984.T",
    "keyence": "6861.T", "nintendo": "7974.T", "mufg": "8306.T",
    "takeda": "4502.T", "daiichi sankyo": "4568.T", "ntt": "9432.T",
    "softbank corp": "9434.T", "smfg": "8316.T", "tokyo electron": "8035.T",
}
_US_TICKERS = {
    "apple": "AAPL", "microsoft": "MSFT", "alphabet": "GOOGL",
    "amazon": "AMZN", "meta": "META", "tesla": "TSLA", "nvidia": "NVDA",
    "netflix": "NFLX", "jpmorgan": "JPM", "visa": "V",
    "j&j": "JNJ", "walmart": "WMT", "berkshire": "BRK.B",
    "unitedhealth": "UNH", "eli lilly": "LLY",
}


def ticker_for(name: str) -> str | None:
    """Lookup a ticker by lowercase company name."""
    n = name.strip().lower()
    return _JP_TICKERS.get(n) or _US_TICKERS.get(n)


# ---- Search query templates ----------------------------------------------

def search_queries(today: date | None = None,
                   theme: str | None = None,
                   ticker: str | None = None) -> dict[str, list[str]]:
    """Return categorized websearch query lists."""
    today = today or date.today()
    ymd = today.isoformat()
    month = today.strftime("%Y-%m")

    out: dict[str, list[str]] = {
        "macro": [
            f"{ymd} Nikkei 225 index",
            f"{ymd} Dow Jones S&P 500",
            f"{ymd} VIX volatility",
            f"FOMC schedule {month}",
            f"Earnings season {month} major companies",
        ],
        "sector": [
            f"Sector performance ranking {ymd}",
            f"Capital inflows by sector {month}",
            f"TOPIX 33 sectors advancers/decliners {ymd}",
        ],
    }
    if theme:
        out["theme"] = [
            f"{theme} stocks {ymd} outlook",
            f"{theme} sector leaders {month}",
        ]
    if ticker:
        out["ticker"] = [
            f"{ticker} earnings most recent quarter",
            f"{ticker} chart technical analysis",
            f"{ticker} IR disclosures recent",
            f"{ticker} analyst ratings upgrade downgrade",
            f"{ticker} insider buying",
            f"{ticker} PER PBR dividend yield",
            f"{ticker} EV/EBITDA ROE",
        ]
    return out


# ---- Proposal data model --------------------------------------------------

@dataclass
class Proposal:
    company: str
    ticker: str
    action: Action
    entry_start: date
    entry_end: date
    target_price: float
    position_pct: float
    entry_condition_price: float | None = None
    entry_condition_volume: float | None = None
    entry_trigger: str = ""
    take_profit: float | None = None
    stop_loss: float | None = None
    holding_days: int | None = None
    fundamentals: str = ""
    technicals: str = ""
    macro: str = ""
    risks: list[str] = field(default_factory=list)

    def take_profit_pct(self) -> str | None:
        if self.take_profit is None:
            return None
        pct = (self.take_profit - self.target_price) / self.target_price * 100
        return f"{pct:+.1f}%"

    def stop_loss_pct(self) -> str | None:
        if self.stop_loss is None:
            return None
        pct = (self.stop_loss - self.target_price) / self.target_price * 100
        return f"{pct:+.1f}%"


# ---- Markdown formatters --------------------------------------------------

_DISCLAIMER = (
    "> ⚠️ This proposal is for informational purposes only. "
    "It is not investment advice. Final decisions are the user's own responsibility."
)


def format_proposal(p: Proposal, idx: int) -> str:
    lines = [
        f"## Proposal {idx}: {p.company} ({p.ticker})",
        "",
        f"### Recommended Action: **{p.action}**",
        f"- Execution window: {p.entry_start.isoformat()} → {p.entry_end.isoformat()}",
        f"- Target price: {p.target_price}",
        f"- Position size: {p.position_pct}% of capital",
        "",
        "### Entry Conditions",
    ]
    if p.entry_condition_price is not None:
        lines.append(f"- Price: ≤ {p.entry_condition_price}")
    if p.entry_condition_volume is not None:
        lines.append(f"- Volume: ≥ {p.entry_condition_volume}")
    if p.entry_trigger:
        lines.append(f"- Trigger: {p.entry_trigger}")
    lines.append("")
    lines.append("### Exit Strategy")
    if p.take_profit is not None:
        lines.append(f"- Take profit: {p.take_profit} ({p.take_profit_pct()})")
    if p.stop_loss is not None:
        lines.append(f"- Stop loss: {p.stop_loss} ({p.stop_loss_pct()})")
    if p.holding_days is not None:
        lines.append(f"- Holding period: close within {p.holding_days} days")
    lines += [
        "",
        "### Rationale",
        f"1. Fundamentals: {p.fundamentals}",
        f"2. Technicals: {p.technicals}",
        f"3. Macro: {p.macro}",
        "",
        "### Risks",
    ]
    for r in p.risks:
        lines.append(f"- {r}")
    return "\n".join(lines)


def format_report(today: date | None,
                  macro: dict[str, str],
                  proposals: Sequence[Proposal],
                  portfolio: dict[str, str],
                  indicators: list[str],
                  risk_tolerance: RiskLvl = "balanced") -> str:
    today = today or date.today()
    lines = [
        f"# Stock Trading Proposal ({today.isoformat()})",
        "",
        _DISCLAIMER,
        "",
        "## Macro Environment Summary",
        f"- Nikkei 225: {macro.get('nikkei', 'n/a')}",
        f"- Dow Jones:  {macro.get('dow', 'n/a')}",
        f"- VIX:        {macro.get('vix', 'n/a')}",
        f"- Key events: {macro.get('events', 'n/a')}",
        "",
        "---",
        "",
    ]
    for i, p in enumerate(proposals, start=1):
        lines.append(format_proposal(p, i))
        lines.append("")
        lines.append("---")
        lines.append("")
    lines += [
        "## Portfolio Diversification",
        f"- Sector: {portfolio.get('sector', 'n/a')}",
        f"- Region: {portfolio.get('region', 'n/a')}",
        f"- Risk tolerance: {risk_tolerance}",
        "",
        "## Indicators to Watch (daily)",
    ]
    for ind in indicators:
        lines.append(f"- {ind}")
    return "\n".join(lines)


# ---- Self-test ------------------------------------------------------------

if __name__ == "__main__":
    today = date.today()
    p = Proposal(
        company="NVIDIA",
        ticker="NVDA",
        action="BUY",
        entry_start=today + timedelta(days=1),
        entry_end=today + timedelta(days=5),
        target_price=180.0,
        position_pct=10.0,
        entry_condition_price=175.0,
        entry_trigger="breakout above $180",
        take_profit=210.0,
        stop_loss=160.0,
        holding_days=30,
        fundamentals="Revenue +120% YoY, data-center demand",
        technicals="Above 200-day MA, RSI 55",
        macro="AI capex cycle, semis tailwind",
        risks=["Geopolitical China exposure", "Valuation stretched"],
    )
    md = format_report(
        today=today,
        macro={"nikkei": "38,000 (+0.5%)",
               "dow": "39,500 (-0.2%)",
               "vix": "14.2",
               "events": "FOMC minutes Wed"},
        proposals=[p],
        portfolio={"sector": "Tech 30%, Financials 20%, Cash 50%",
                   "region": "Japan 40%, US 60%"},
        indicators=["NVDA above 200-day MA", "VIX < 20"],
        risk_tolerance="balanced",
    )
    print(md)
