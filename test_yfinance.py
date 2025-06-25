# test_yfinance.py
import yfinance as yf

TICKER = '^GSPC'
START_DATE = '2015-01-01'
END_DATE = '2024-12-31'

print(f"Attempting to download data for {TICKER} from {START_DATE} to {END_DATE}...")

try:
    data = yf.download(TICKER, start=START_DATE, end=END_DATE)

    if data.empty:
        print("\n---> RESULT: FAILED. yfinance returned an empty DataFrame.")
        print("This could be due to network issues, an API block, or an outdated library.")
    else:
        print(f"\n---> RESULT: SUCCESS! Downloaded {len(data)} rows of data.")
        print("The first row downloaded is:")
        print(data.head(1))

except Exception as e:
    print(f"\n---> RESULT: FAILED. An error occurred during download: {e}")