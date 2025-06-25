from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Data Management
    path('data/', views.data_management, name='data_management'),

    # Strategies
    path('strategies/', views.strategy_list, name='strategy_list'),
    path('strategies/create/', views.strategy_create, name='strategy_create'),
    path('strategies/<int:pk>/', views.strategy_detail, name='strategy_detail'),
    path('strategies/<int:pk>/edit/', views.strategy_edit, name='strategy_edit'),
    path('strategies/<int:pk>/delete/', views.strategy_delete, name='strategy_delete'),

    # Backtesting
    path('strategies/<int:pk>/run_backtest/', views.run_backtest_view, name='run_backtest'),
    path('backtests/<int:pk>/', views.view_backtest_report, name='view_backtest_report'),

    # Task status check for AJAX polling
    path('task_status/<str:task_id>/', views.task_status, name='task_status'),
]