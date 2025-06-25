Quantitative Trading Strategy Framework

A full-stack, open-source framework for researching, backtesting, and analyzing quantitative trading strategies. Built with Python, Django, and Celery for robust, asynchronous back-end processing and a clean web-based user interface.

About The Project

This project was built to provide a personal, self-hosted platform for quantitative finance research. It moves beyond simple scripts into a full-featured application, allowing users to define complex strategies in Python, test them against historical data, and analyze their performance through a clean web dashboard.

The entire stack is built on powerful, open-source technologies, giving you complete control and unlimited flexibility without licensing fees.
Key Features

    Web-Based UI: Manage data, strategies, and backtest reports through a secure Django interface.
    Modular Strategy Definition: Write strategies as self-contained Python scripts. The framework is flexible enough to handle simple indicator crossovers, complex statistical arbitrage pairs, or advanced filters like the Unscented Kalman Filter.
    Asynchronous Backtesting: Leverages Celery and Redis to run complex backtests in the background without tying up the user interface.
    Detailed Performance Reporting: Automatically generates key metrics for every backtest, including:
        Total Return
        Sharpe Ratio
        Maximum Drawdown
        Calmar Ratio
        Interactive Equity Curve Charts
    Flexible Data Management: Ingests historical daily or intraday data from yfinance.
    Built-in Custom Filter Engine: Includes a from-scratch Unscented Kalman Filter implementation to demonstrate how to integrate advanced, non-library models.

Built With

    Python
    Django
    PostgreSQL
    Celery
    Redis
    Pandas & NumPy
    SciPy
    yfinance
    pykalman

Getting Started

Follow these steps to get a local copy up and running.
Prerequisites

You must have the following installed on your system:

    Python 3.10+
    PostgreSQL
    Redis

Installation

    Clone the repo
    Bash

git clone <your-github-repo-url.git>
cd quant_framework

Create and activate a Python virtual environment
Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Create a requirements.txt file. This is a best practice for sharing your project. Run this command once to generate the file:
Bash

pip freeze > requirements.txt

Install dependencies
Bash

pip install -r requirements.txt

Configure your database in settings.py

    Open quant_framework/settings.py.
    Find the DATABASES section and enter your PostgreSQL credentials (database name, user, password).

Set up the PostgreSQL Database

    Open the psql terminal (e.g., sudo -u postgres psql).
    Run the following SQL commands:
    SQL

    CREATE USER your_db_user WITH PASSWORD 'your_db_password';
    CREATE DATABASE your_db_name WITH OWNER = your_db_user;
    GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
    \q

Run Django Migrations to create the application tables in your database.
Bash

python manage.py makemigrations trading
python manage.py migrate

Create a Superuser to be able to log into the web application.
Bash

    python manage.py createsuperuser

Usage

To run the application, you need to start its three main components in separate terminals.

    Terminal 1: Start Redis
    Bash

redis-server

Terminal 2: Start the Celery Worker (from the project root directory)
Bash

celery -A quant_framework worker --loglevel=info

Terminal 3: Start the Django Development Server
Bash

    python manage.py runserver

You can now access the web interface at http://127.0.0.1:8000.

The typical workflow is:

    Navigate to the Market Data page to download data for the assets you want to analyze (e.g., SPY, ^VIX).
    Go to the Strategies page and create a new strategy, pasting your Python code into the script box.
    From the strategy's detail page, run a Backtest by selecting the asset and date range.
    View the Report to analyze the performance.

Roadmap

This framework is a powerful base with many potential enhancements. Here are some ideas for future development branches:

    [ ] Advanced Transaction Cost Modeling: Add more sophisticated models for slippage and commissions.
    [ ] Walk-Forward Analysis: Implement a dedicated UI and back-end logic for running robust walk-forward optimizations.
    [ ] State Continuation ("Warm Starts"): Implement the feature to initialize a backtest from the saved state of a previous run.
    [ ] Live Paper Trading: Integrate with a broker API like Alpaca to run strategies on live market data with a paper account.
    [ ] Portfolio-Level Backtesting: Upgrade the engine to simulate a strategy across a portfolio of assets, not just one at a time.
