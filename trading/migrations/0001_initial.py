# Generated by Django 5.2.3 on 2025-06-22 03:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('asset_type', models.CharField(default='equity', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TradingStrategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('script', models.TextField(help_text="Python code for the strategy. Must define a 'generate_signals(data)' function.")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BacktestReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('initial_capital', models.DecimalField(decimal_places=4, max_digits=19)),
                ('final_balance', models.DecimalField(decimal_places=4, max_digits=19)),
                ('total_return_pct', models.FloatField()),
                ('sharpe_ratio', models.FloatField()),
                ('max_drawdown_pct', models.FloatField()),
                ('win_rate_pct', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('equity_curve', models.JSONField(default=dict)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trading.asset')),
                ('strategy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='backtests', to='trading.tradingstrategy')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('open_price', models.DecimalField(decimal_places=8, max_digits=19)),
                ('high_price', models.DecimalField(decimal_places=8, max_digits=19)),
                ('low_price', models.DecimalField(decimal_places=8, max_digits=19)),
                ('close_price', models.DecimalField(decimal_places=8, max_digits=19)),
                ('volume', models.BigIntegerField()),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data', to='trading.asset')),
            ],
            options={
                'ordering': ['timestamp'],
                'unique_together': {('asset', 'timestamp')},
            },
        ),
    ]
