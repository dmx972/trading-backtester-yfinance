from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.contrib import messages
from celery.result import AsyncResult
from django.http import JsonResponse
from .models import TradingStrategy, BacktestReport, Asset
from .forms import StrategyForm, BacktestForm
from .tasks import fetch_market_data_task, run_backtest_task


@login_required
def dashboard(request):
    strategies = TradingStrategy.objects.filter(user=request.user)
    backtests = BacktestReport.objects.filter(strategy__user=request.user).order_by('-created_at')[:5]
    context = {'strategies': strategies, 'backtests': backtests}
    return render(request, 'trading/dashboard.html', context)


@login_required
def strategy_list(request):
    strategies = TradingStrategy.objects.filter(user=request.user)
    return render(request, 'trading/strategy_list.html', {'strategies': strategies})


@login_required
def strategy_create(request):
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            messages.success(request, 'Strategy created successfully!')
            return redirect('strategy_list')
    else:
        form = StrategyForm()
    return render(request, 'trading/strategy_form.html', {'form': form})


@login_required
def strategy_detail(request, pk):
    strategy = get_object_or_404(TradingStrategy, pk=pk, user=request.user)
    backtests = strategy.backtests.all().order_by('-created_at')
    return render(request, 'trading/strategy_detail.html', {'strategy': strategy, 'backtests': backtests})


@login_required
def strategy_edit(request, pk):
    strategy = get_object_or_404(TradingStrategy, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StrategyForm(request.POST, instance=strategy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Strategy updated successfully!')
            return redirect('strategy_detail', pk=strategy.pk)
    else:
        form = StrategyForm(instance=strategy)
    return render(request, 'trading/strategy_form.html', {'form': form})


@login_required
@require_POST
def strategy_delete(request, pk):
    strategy = get_object_or_404(TradingStrategy, pk=pk, user=request.user)
    strategy.delete()
    messages.success(request, 'Strategy deleted successfully!')
    return redirect('strategy_list')


@login_required
def data_management(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        task = fetch_market_data_task.delay(ticker, start_date, end_date)
        messages.info(request, f'Data fetch task for {ticker} started. Task ID: {task.id}')
        return redirect('data_management')

    assets = Asset.objects.all()
    return render(request, 'trading/data_management.html', {'assets': assets})


@login_required
def run_backtest_view(request, pk):
    strategy = get_object_or_404(TradingStrategy, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BacktestForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            task = run_backtest_task.delay(
                strategy_id=strategy.id,
                asset_id=data['asset'].id,
                start_date_str=data['start_date'].strftime('%Y-%m-%d'),
                end_date_str=data['end_date'].strftime('%Y-%m-%d'),
                initial_capital_str=str(data['initial_capital'])
            )
            # Redirect to a waiting page or the strategy detail page
            # We'll pass the task_id to the template to poll for status
            return render(request, 'trading/backtest_running.html', {'task_id': task.id})
    else:
        form = BacktestForm()
    return render(request, 'trading/run_backtest_form.html', {'strategy': strategy, 'form': form})


@login_required
def view_backtest_report(request, pk):
    report = get_object_or_404(BacktestReport, pk=pk, strategy__user=request.user)
    return render(request, 'trading/backtest_report.html', {'report': report})


def task_status(request, task_id):
    """
    Checks the status of a Celery task and returns it as JSON.
    Handles failures gracefully by converting exception objects to strings.
    """
    task = AsyncResult(task_id)

    if task.state == 'FAILURE':
        # If the task failed, the result is an Exception object.
        # Convert it to a string to make it JSON serializable.
        response_data = {
            'state': task.state,
            'result': str(task.result)  # Convert exception to string
        }
    elif task.state == 'SUCCESS':
        response_data = {
            'state': task.state,
            'result': task.result  # The result is the report_id, which is fine
        }
    else:
        # For states like PENDING or STARTED, the result is None
        response_data = {
            'state': task.state,
            'result': None
        }

    return JsonResponse(response_data)