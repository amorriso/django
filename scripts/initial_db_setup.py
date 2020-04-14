import base_scraper
import urlparse
import os
import time
import re
import datetime
import pandas

from fetcher_statics import ScrapeStatics

import logging
import logging.config

from trader.marketdata import models as md_models


if __name__ == '__main__':

    """Remember to: export DJANGO_SETTINGS_MODULE=trader.trader.settings
    """

    future = md_models.Future(
            name = "Crude Oil Brent Jun '20 (CBM20)",
            barchart_id = 'CBM20',
            easyscreen_id = 'CBM20',
            expiry_date = datetime.datetime(2020, 6, 21),
    )
    try:
        future.save()
    except:
        future = md_models.Future.objects.get(name="Crude Oil Brent Jun '20 (CBM20)")

    option_def = md_models.OptionDefinition(
            future = future,
            name = 'Brent_Jun_20_Options',
            expiry_date = datetime.datetime(2020, 4, 27),
            strike_interval = 5.0,
            number_of_OTM_options = 20,
    )
    option_def.save()
