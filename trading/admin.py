from django.contrib import admin
from .models import Asset, HistoricalData, TradingStrategy, BacktestReport

admin.site.register(Asset)
admin.site.register(TradingStrategy)

@admin.register(HistoricalData)
class HistoricalDataAdmin(admin.ModelAdmin):
    list_display = ('asset', 'timestamp', 'close_price')
    list_filter = ('asset',)
    date_hierarchy = 'timestamp'

@admin.register(BacktestReport)
class BacktestReportAdmin(admin.ModelAdmin):
    list_display = ('strategy', 'asset', 'total_return_pct', 'sharpe_ratio', 'created_at')
    list_filter = ('strategy', 'asset')