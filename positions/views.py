import os
import pandas as pd

from django.shortcuts import render
from django.conf import settings

from . import portfolio_utils as pu


def index(request):
    """Primary view of positions held"""
    positions_raw = pd.read_csv(os.path.join(settings.STATIC_ROOT, 'portfolio/positions.csv'))
    positions_summary = pu.get_position_metrics(positions_raw)

    context = {
        "positions": positions_summary.to_html(index=False, justify="right"),
        "accounts": [acct for acct in positions_summary["Account"].unique() if acct]
    }

    return render(request, "positions/index.html", context)
