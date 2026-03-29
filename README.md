# MEFAI CLI

[![CI](https://github.com/mefai-dev/mefai-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/mefai-dev/mefai-cli/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Built with Typer](https://img.shields.io/badge/built_with-Typer-009688.svg)](https://typer.tiangolo.com/)

Command line interface for the MEFAI Engine trading platform. Built with Typer and Rich for a beautiful terminal experience.

## Installation

Install from PyPI:

```bash
pip install mefai-cli
```

Or install from source:

```bash
git clone https://github.com/mefai-dev/mefai-cli.git
cd mefai-cli
pip install -e .
```

## Configuration

Before using the CLI you need to set your MEFAI Engine connection details:

```bash
mefai configure --base-url http://your-engine:8080 --api-key your_key_here
```

This saves a config file at `~/.mefai/config.yaml`.

## Commands

### Engine and Account

```
$ mefai status
+------------------------------------------+
|            Engine Status                  |
|   Status: running                         |
|   Uptime: 4d 12h 33m                     |
|   Version: 2.1.0                          |
+------------------------------------------+

$ mefai balance
+------------------------------------------+
|           Account Balance                 |
|   Total: 12450.00 USDT                   |
|   Available: 8200.00 USDT                |
|   In Positions: 4250.00 USDT             |
+------------------------------------------+

$ mefai positions
+----------+------+-------+-----------+---------+
| Symbol   | Side | Size  | Entry     | PnL     |
+----------+------+-------+-----------+---------+
| BTCUSDT  | long | 0.05  | 67,200.00 | +120.50 |
| ETHUSDT  | long | 1.20  | 3,450.00  | -15.30  |
+----------+------+-------+-----------+---------+
```

### Market Data

```
$ mefai ticker BTCUSDT
+------------------------------------------+
|          Ticker: BTCUSDT                  |
|   Price: 67,450.2300                      |
|   24h Change: +2.15%                      |
|   Volume: 1,234,567.89                    |
+------------------------------------------+

$ mefai orderbook BTCUSDT
+------------+----------+------------+----------+
| Bid Price  | Bid Size | Ask Price  | Ask Size |
+------------+----------+------------+----------+
| 67,449.50  | 1.230    | 67,450.10  | 0.890    |
| 67,448.00  | 2.100    | 67,451.00  | 1.500    |
+------------+----------+------------+----------+

$ mefai candles BTCUSDT --timeframe 4h --limit 5
+---------------------+-----------+-----------+-----------+-----------+----------+
| Time                | Open      | High      | Low       | Close     | Volume   |
+---------------------+-----------+-----------+-----------+-----------+----------+
| 2026-03-29 00:00    | 67,100.00 | 67,500.00 | 66,900.00 | 67,450.00 | 45123.5  |
+---------------------+-----------+-----------+-----------+-----------+----------+

$ mefai funding BTCUSDT
+------------------------------------------+
|       Funding Rate: BTCUSDT               |
|   Rate: 0.0100%                           |
|   Next Funding: 4h 12m                    |
+------------------------------------------+
```

### Intelligence and ML

```
$ mefai features BTCUSDT
+------------------------------------------+
|         Features: BTCUSDT                 |
|   RSI 14: 62.5                            |
|   MACD: 125.30                            |
|   Bollinger Upper: 68,100.00              |
|   VWAP: 67,200.00                         |
+------------------------------------------+

$ mefai signals
+----------+-----------+----------+--------+-------------------+
| Symbol   | Direction | Strength | Source | Time              |
+----------+-----------+----------+--------+-------------------+
| BTCUSDT  | long      | 0.85     | ML_v3  | 2026-03-29 14:30  |
+----------+-----------+----------+--------+-------------------+

$ mefai models
+----------+-----------+----------+--------+
| Name     | Type      | Accuracy | Status |
+----------+-----------+----------+--------+
| lstm_v3  | LSTM      | +82.30%  | active |
| xgb_v2   | XGBoost   | +79.10%  | active |
+----------+-----------+----------+--------+

$ mefai predict BTCUSDT --model lstm_v3
+------------------------------------------+
|        Prediction: BTCUSDT                |
|   Direction: long                         |
|   Confidence: 0.87                        |
|   Target: 68,200.00                       |
+------------------------------------------+
```

### Backtesting and Risk

```
$ mefai backtest BTCUSDT --start 2026-01-01 --end 2026-03-01
+------------------------------------------+
|         Backtest: BTCUSDT                 |
|   Total Trades: 142                       |
|   Win Rate: 64.8%                         |
|   Sharpe Ratio: 1.82                      |
|   Max Drawdown: -8.3%                     |
+------------------------------------------+

$ mefai metrics
+------------------------------------------+
|       Performance Metrics                 |
|   Daily PnL: +245.50 USDT                |
|   Weekly PnL: +1,230.00 USDT             |
|   Total PnL: +4,500.00 USDT              |
+------------------------------------------+

$ mefai risk
+------------------------------------------+
|           Risk Status                     |
|   Exposure: 34.1%                         |
|   Max Drawdown: -2.1%                     |
|   VaR 95: -350.00 USDT                   |
+------------------------------------------+
```

### Order Management

```
$ mefai order BTCUSDT long 0.01
[ok] Order placed: long 0.01 BTCUSDT

$ mefai close BTCUSDT
[ok] Position closed: BTCUSDT
```

### Streaming and Health

```
$ mefai stream
+------------------------------------------+
|            Live Stream                    |
|   Connecting to ws://localhost:8080/ws    |
+------------------------------------------+
[ok] Connected
BTCUSDT  67,450.2300  +0.15%
ETHUSDT  3,452.1000   -0.08%
...

$ mefai health
[ok] MEFAI Engine is healthy
```

## Development

```bash
git clone https://github.com/mefai-dev/mefai-cli.git
cd mefai-cli
pip install -e ".[dev]"
pytest
ruff check src/
mypy src/
```

## License

Apache 2.0. See [LICENSE](LICENSE) for details.
