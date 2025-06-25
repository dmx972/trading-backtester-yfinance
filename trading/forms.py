from django import forms
from .models import TradingStrategy, Asset

class StrategyForm(forms.ModelForm):
    class Meta:
        model = TradingStrategy
        fields = ['name', 'description', 'script']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'script': forms.Textarea(attrs={'rows': 15, 'class': 'font-monospace'}),
        }

class BacktestForm(forms.Form):
    asset = forms.ModelChoiceField(queryset=Asset.objects.all(), label="Asset to trade")
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    initial_capital = forms.DecimalField(initial=10000.00)