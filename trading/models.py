from django.db import models
from django.contrib.auth.models import User

class Asset(models.Model):
    ticker = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, default='equity')

    def __str__(self):
        return self.ticker

class HistoricalData(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='data')
    timestamp = models.DateTimeField()
    open_price = models.DecimalField(max_digits=19, decimal_places=8)
    high_price = models.DecimalField(max_digits=19, decimal_places=8)
    low_price = models.DecimalField(max_digits=19, decimal_places=8)
    close_price = models.DecimalField(max_digits=19, decimal_places=8)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('asset', 'timestamp')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.asset.ticker} at {self.timestamp}"

class TradingStrategy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    script = models.TextField(help_text="Python code for the strategy. Must define a 'generate_signals(data)' function.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BacktestReport(models.Model):
    strategy = models.ForeignKey(TradingStrategy, on_delete=models.CASCADE, related_name='backtests')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    initial_capital = models.DecimalField(max_digits=19, decimal_places=4)
    final_balance = models.DecimalField(max_digits=19, decimal_places=4)
    total_return_pct = models.FloatField()
    sharpe_ratio = models.FloatField()
    max_drawdown_pct = models.FloatField()
    calmar_ratio = models.FloatField(default=0.0)
    win_rate_pct = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    # This can store JSON data for charts
    equity_curve = models.JSONField(default=dict)

    def __str__(self):
        return f"Backtest for {self.strategy.name} on {self.asset.ticker}"