import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from ..models import TradingStrategy, Asset, HistoricalData, BacktestReport
import importlib.util
from datetime import datetime
import sys

def run_backtest_logic(strategy_id, asset_id, start_date, end_date, initial_capital):
    """
    The core logic for running a backtest.
    This is called by the Celery task.
    """
    strategy = TradingStrategy.objects.get(id=strategy_id)
    asset = Asset.objects.get(id=asset_id)

    # 1. Get Data
    qs = HistoricalData.objects.filter(
        asset=asset,
        timestamp__date__range=(start_date, end_date)
    ).order_by('timestamp')

    if not qs.exists():
        raise ValueError("No historical data for the selected asset and date range.")

    data = pd.DataFrame.from_records(qs.values())
    data.set_index('timestamp', inplace=True)

    # 2. Generate Signals
    # Use exec to run the user-provided strategy script.
    # This is a security risk in a public-facing app. Use with caution.
    local_scope = {}
    try:
        # Create a unique name for our virtual module
        module_name = f"strategy_script_{strategy.id}"

        # Create a module specification from the script content
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        strategy_module = importlib.util.module_from_spec(spec)

        # Execute the script's code within the new module's namespace
        # This is a robust way to handle imports inside the script
        exec(strategy.script, strategy_module.__dict__)

        # The 'generate_signals' function is now an attribute of our virtual module
        signals = strategy_module.generate_signals(data)

    except Exception as e:
        # Handle potential errors in user script
        raise type(e)(f"Error in strategy script: {e}")

    # 3. Simulate Portfolio
    cash = initial_capital
    position = 0
    portfolio_values = []

    for i in range(len(data)):
        current_date = data.index[i]
        current_price = Decimal(data['close_price'].iloc[i])
        signal = signals.iloc[i]

        # Simple execution logic
        if signal == 1 and cash > current_price:  # Buy Signal
            position += 1
            cash -= current_price
        elif signal == -1 and position > 0:  # Sell Signal
            position -= 1
            cash += current_price

        portfolio_value = cash + (position * current_price)
        portfolio_values.append({'date': current_date, 'value': portfolio_value})

    equity_curve_df = pd.DataFrame(portfolio_values).set_index('date')

    # 4. Calculate Metrics
    # Do all direct monetary calculations first using the precise Decimal type
    final_balance = equity_curve_df['value'].iloc[-1]
    total_return = (final_balance / initial_capital) - 1

    # Calculate CAGR (Compound Annual Growth Rate)
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    num_years = (end_dt - start_dt).days / 365.25

    if num_years > 0:
        cagr = (float(final_balance) / float(initial_capital)) ** (1 / num_years) - 1
    else:
        cagr = 0.0  # Avoid division by zero if backtest is less than a day

    # Now, convert the equity curve to float for the statistical calculations
    equity_curve_df['value'] = equity_curve_df['value'].astype(float)

    returns = equity_curve_df['value'].pct_change().dropna()
    sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) != 0 else 0.0

    cumulative_max = equity_curve_df['value'].cummax()
    drawdown = (equity_curve_df['value'] - cumulative_max) / cumulative_max
    max_drawdown = drawdown.min()

    # Calculate Calmar Ratio
    # Use the absolute value of max_drawdown
    if max_drawdown != 0:
        calmar_ratio = cagr / abs(max_drawdown)
    else:
        calmar_ratio = 0.0  # Avoid division by zero

    wins = len(returns[returns > 0])
    losses = len(returns[returns < 0])
    win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0

    # 5. Save Report
    report = BacktestReport.objects.create(
        strategy=strategy,
        asset=asset,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        final_balance=final_balance.quantize(Decimal('0.01')),
        total_return_pct=float(total_return) * 100,
        sharpe_ratio=float(sharpe_ratio),
        max_drawdown_pct=float(max_drawdown) * 100,
        calmar_ratio=float(calmar_ratio),  # <-- Add the new ratio here
        win_rate_pct=float(win_rate) * 100,
        equity_curve={
            'dates': [d.strftime('%Y-%m-%d') for d in equity_curve_df.index],
            'values': [v for v in equity_curve_df['value']]
        }
    )
    return report.id