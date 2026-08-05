---
name: stock
description: Propose concrete buy/sell strategies for Japanese and US equities — ticker, price, entry day, take-profit / stop-loss lines, and the macro / fundamental / technical rationale. Always include a disclaimer that this is not investment advice.
---

# Stock Trading Strategy Skill

## Overview
Propose concrete buy/sell strategies for Japanese and US equities. Explicitly state **ticker, price, entry day, take-profit / stop-loss lines**.

## ⚠️ Disclaimer (always include in output)
```
This proposal is for informational purposes only. It is not investment advice.
Final decisions are the user's own responsibility.
```

## Bundled Helper Module
**`skill/stock/scripts/stock_skill.py`** provides:
- `search_queries(today, theme, ticker)` — categorized websearch query lists (macro / sector / ticker / valuation)
- `ticker_for(name)` — lookup known tickers for major JP/US companies
- `Proposal` dataclass — structured buy/sell proposal with entry/exit/rationale
- `format_proposal(p, idx)` — Markdown formatter for one proposal
- `format_report(today, macro, proposals, portfolio, indicators, risk)` — full Markdown report

```python
import sys; sys.path.insert(0, "skill/stock/scripts")
from stock_skill import search_queries, ticker_for, Proposal, format_report
from datetime import date, timedelta

queries = search_queries(date.today(), ticker="NVDA")
p = Proposal(
    company="NVIDIA", ticker="NVDA", action="BUY",
    entry_start=date.today()+timedelta(days=1),
    entry_end=date.today()+timedelta(days=5),
    target_price=180.0, position_pct=10.0,
    take_profit=210.0, stop_loss=160.0, holding_days=30,
    fundamentals="Revenue +120% YoY",
    technicals="Above 200-day MA, RSI 55",
    macro="AI capex cycle",
    risks=["China exposure", "Valuation stretched"],
)
md = format_report(date.today(), {"nikkei": "38k", "dow": "39.5k", "vix": "14.2",
                                   "events": "FOMC Wed"}, [p],
                   {"sector": "Tech 30%", "region": "JP 40% / US 60%"},
                   ["NVDA above 200-day MA", "VIX < 20"])
```
Run `python skill/stock/scripts/stock_skill.py` to print a demo proposal.

## Information-Gathering Flow (real-time data mandatory)

### Phase 1: Macro Environment
```python
# websearch for current conditions
queries = [
    "{today's date} Nikkei 225 index",
    "{today's date} Dow Jones S&P 500",
    "{today's date} VIX volatility",
    "FOMC schedule {this month}",
    "Earnings season {this month} major companies",
]
```

### Phase 2: Sector Analysis
```python
# Sector relative strength
queries = [
    "Sector performance ranking {today}",
    "Capital inflows by sector {this month}",
    "TOPIX 33 sectors advancers/decliners {today}",
]
```

### Phase 3: Ticker Screening
```python
# Individual ticker details
queries = [
    "{ticker} earnings {most recent quarter}",
    "{ticker} chart technical analysis",
    "{ticker} IR disclosures recent",
    "{ticker} analyst ratings upgrade downgrade",
    "{ticker} insider buying",
]
```

### Phase 4: Valuation Check
```python
# Company valuation metrics
queries = [
    "{ticker} PER PBR dividend yield",
    "{ticker} EV/EBITDA ROE",
    "{ticker} forward PE valuation",
]
```

## Primary Data Sources

| Data | URL |
|---|---|
| Japan stocks (Yahoo) | https://finance.yahoo.co.jp/ |
| US stocks (Yahoo) | https://finance.yahoo.com/ |
| JPX timely disclosures | https://www2.jpx.co.jp/disc/ |
| EDGAR (US SEC) | https://www.sec.gov/edgar |
| TradingView | https://www.tradingview.com/ |
| StockAnalysis | https://stockanalysis.com/ |
| Macrotrends | https://www.macrotrends.net/ |
| Investing.com | https://www.investing.com/ |

## Ticker Notation

### Japan
- 4-digit code + `.T` (e.g., `7203.T` = Toyota)
- Major tickers:
  - 7203.T Toyota / 6758.T Sony Group / 9984.T SoftBank Group
  - 6861.T Keyence / 7974.T Nintendo / 8306.T MUFG
  - 4502.T Takeda / 4568.T Daiichi Sankyo / 9432.T NTT
  - 9434.T SoftBank Corp / 8316.T SMFG / 8035.T Tokyo Electron

### US
- Ticker only (e.g., `AAPL` = Apple)
- Major tickers:
  - AAPL Apple / MSFT Microsoft / GOOGL Alphabet / AMZN Amazon
  - META Meta / TSLA Tesla / NVDA NVIDIA / NFLX Netflix
  - JPM JPMorgan / V Visa / JNJ J&J / WMT Walmart
  - BRK.B Berkshire / UNH UnitedHealth / LLY Eli Lilly

## Buy/Sell Judgment Framework

### Buy Signals (≥3 elements recommended)
1. **Fundamentals**:
   - Recent quarter: revenue and profit growth
   - ROE > 10%, PER below industry average
   - Dividend yield ≥ 2% (when earnings are strong)
   - Insider buying detected

2. **Technicals**:
   - Trading above 200-day moving average
   - Volume surge (≥ 1.5× average)
   - Breakout above recent high
   - RSI 40–60 (not overbought)

3. **Macro / Sentiment**:
   - Industry tailwind
   - Analyst upgrade(s)
   - Institutional inflows increasing

### Sell Signals
1. **Fundamental deterioration**:
   - Revenue / profit decline, guidance cut
   - ROE drop, debt increase
   - Scandal / litigation risk

2. **Technical deterioration**:
   - Broke below 200-day moving average
   - Double top / head-and-shoulders
   - Decline on rising volume

3. **Macro headwinds**:
   - Rising rates (hurts growth stocks)
   - Tighter industry regulation
   - Consecutive analyst downgrades

## Output Format (strict)

```markdown
# Stock Trading Proposal ({YYYY-MM-DD})

## ⚠️ Disclaimer
This proposal is for informational purposes only. It is not investment advice.
Final decisions are the user's own responsibility.

## Macro Environment Summary
- Nikkei 225: {value} ({change})
- Dow Jones: {value} ({change})
- VIX: {value}
- Key events: {FOMC / earnings / etc.}

---

## Proposal 1: {Company Name} ({ticker})

### Recommended Action
**{BUY/SELL/HOLD}**
- Execution window: {YYYY-MM-DD} to {YYYY-MM-DD} ({N} days)
- Target price: {JPY/USD}
- Position size: {X}% of capital

### Entry Conditions
- Price: ≤ {value}
- Volume: ≥ {value}
- Trigger: {breakout / reversal / etc.}

### Exit Strategy
- **Take profit**: {value} (+{X}%)
- **Stop loss**: {value} (−{X}%)
- **Holding period**: close within {N} days

### Rationale (3 elements)
1. Fundamentals: {concrete data}
2. Technicals: {concrete data}
3. Macro: {concrete data}

### Risks
- {risk 1}
- {risk 2}

---

## Proposal 2: ...

## Portfolio Diversification
- Sector: {sector 1} X%, {sector 2} Y%
- Region: Japan X%, US Y%
- Risk tolerance: {conservative / balanced / aggressive}

## Indicators to Watch (daily)
- {indicator 1}: {threshold}
- {indicator 2}: {threshold}
```

## Strategy-Type Approaches

### 1. Swing Trade (days to weeks)
- Focus: Technicals (MA, MACD, RSI)
- Universe: large-cap, high-liquidity
- Risk: medium

### 2. Value Investing (months to years)
- Focus: Fundamentals (PER, PBR, ROE, dividend)
- Universe: undervalued, high-dividend
- Risk: low

### 3. Growth Investing (months to years)
- Focus: revenue growth, market share, innovation
- Universe: tech, biotech, EV
- Risk: high

### 4. Event-Driven (days to weeks)
- Focus: earnings, M&A, splits, dividend hikes
- Universe: companies with imminent catalysts
- Risk: medium–high

## Timing Guidelines

### Entry Execution Day
- Recommend within next 1–5 business days from proposal date
- In fast-moving markets, same day or next day

### Holding Period
- Swing: 5–30 days
- Value: 90 days–1 year
- Event-driven: 1–14 days after the event
- Stop loss: immediate on trigger

### Take-Profit Timing
- Staged profit-taking recommended (50% / 30% / 20%)
- Stage 1: +10%, sell half
- Stage 2: +20%, sell half of remaining
- Stage 3: trailing stop on the rest

## Risk Management

### Max Position per Ticker
- ≤ 20% of capital
- Sector concentration: ≤ 40%

### Stop-Loss Rules (mandatory)
- Cut at −7% to −10% from entry
- Cut if 200-day MA is broken
- Cut if original thesis is invalidated

### Portfolio-Level
- Keep ≥ 20% cash
- Diversify across low-correlation tickers

## Pre-Output Checklist

- [ ] Proposal date, execution window, holding period stated
- [ ] Ticker accurate (Japan: 4-digit + `.T`; US: ticker)
- [ ] Entry, take-profit, and stop-loss all stated
- [ ] Fundamental / technical / macro all addressed
- [ ] Risks listed
- [ ] Disclaimer included
- [ ] Macro summary attached
- [ ] Latest data fetched via websearch

## Common Pitfalls

| Pitfall | Fix |
|---|---|
| Stale data | Always websearch the latest figures |
| No stop-loss | Set at −7% to −10% |
| Concentrated position | Max 20% per ticker rule |
| Ignoring macro | Always check Nikkei, VIX, rates |
| Skipping fundamentals | Always check earnings and IR |
| Sounding like financial advice | Always include disclaimer |
| Vague timing | State exact execution window in days |

## Notes

- Proposals reflect **current information only**. Re-evaluate when market conditions shift.
- Always **do your own research** alongside these proposals.
- Leverage / margin carries elevated risk.
- Account for taxes (Japan capital-gains tax: 20.315%).
- Use NISA (Japan tax-advantaged account) when eligible.
