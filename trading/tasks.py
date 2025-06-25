import yfinance as yf
from celery import shared_task
from decimal import Decimal
from .models import Asset, HistoricalData
from .services.backtester import run_backtest_logic
import pandas as pd
import traceback


@shared_task
def fetch_market_data_task(ticker, start_date, end_date):
    """
    Fetches historical market data from Yahoo Finance and stores it,
    with enhanced logging for debugging.
    """
    print(f"--- CELERY WORKER: Task started for ticker: {ticker} ---")
    asset, created = Asset.objects.get_or_create(ticker=ticker)
    if created:
        # This part requires a network call, let's wrap it too
        try:
            print(f"CELERY WORKER: Fetching info for new asset {ticker}...")
            stock_info = yf.Ticker(ticker).info
            asset.name = stock_info.get('longName', ticker)
            asset.save()
            print(f"CELERY WORKER: Asset info saved for {ticker}.")
        except Exception as e:
            print(f"CELERY WORKER: FAILED to get Ticker info for {ticker}.")
            print(traceback.format_exc())
            # We can continue without the name, it's not critical

    data = pd.DataFrame()  # Initialize an empty dataframe
    try:
        print(f"CELERY WORKER: Attempting yf.download for {ticker}...")
        data = yf.download(ticker, start=start_date, end=end_date)
        print(f"CELERY WORKER: yf.download call completed. DataFrame is empty: {data.empty}")
    except Exception as e:
        print("!!!!!! CELERY WORKER: yf.download FAILED with an exception !!!!!!")
        print(traceback.format_exc())
        return f"Task failed for {ticker}. yfinance download error: {e}"

    if data.empty:
        print(f"CELERY WORKER: No data returned for {ticker}. Task will stop.")
        return f"No data found for {ticker} between {start_date} and {end_date}"

    # Flatten the columns for easier access in case of MultiIndex
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    instances = []
    for index, row in data.iterrows():
        if not HistoricalData.objects.filter(asset=asset, timestamp=index).exists():
            instances.append(
                HistoricalData(
                    asset=asset, timestamp=index,
                    open_price=Decimal(row['Open']), high_price=Decimal(row['High']),
                    low_price=Decimal(row['Low']), close_price=Decimal(row['Close']),
                    volume=int(row['Volume'])
                )
            )

    HistoricalData.objects.bulk_create(instances)
    print(f"--- CELERY WORKER: Task finished for {ticker}. Stored {len(instances)} new records. ---")
    return f"Successfully downloaded and stored {len(instances)} data points for {ticker}."


@shared_task
def run_backtest_task(strategy_id, asset_id, start_date_str, end_date_str, initial_capital_str):
    """
    Celery task to run the backtest asynchronously.
    """
    initial_capital = Decimal(initial_capital_str)
    # The actual backtesting logic is in the service layer
    report_id = run_backtest_logic(strategy_id, asset_id, start_date_str, end_date_str, initial_capital)
    return report_id