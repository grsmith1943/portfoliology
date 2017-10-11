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
        "positions": positions_summary.to_html(index=False)
    }

    return render(request, "portfolio/index.html", context)