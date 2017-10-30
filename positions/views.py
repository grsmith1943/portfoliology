from django.shortcuts import render

from .models import Account, Position
from . import portfolio_utils as pu


def index(request):
    """Primary view of positions held"""

    positions_summary = pu.get_position_summary(Position.objects.all())
    accounts = Account.objects.all()
    total_cash = sum((acct.cash_balance for acct in accounts))

    context = {
        "positions": positions_summary.to_html(index=False),
        "accounts": [acct.name for acct in accounts],
        "cash_balances": {acct: acct.cash_balance for acct in accounts},
        "total_cash": "{:,.2f}".format(total_cash)
    }

    return render(request, "positions/index.html", context)
