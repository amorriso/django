from celery import Celery
import json
import urllib2
import time
import urlparse
import os
import datetime
import logging
import logging.config


from pyvirtualdisplay import Display

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise EnvironmentError(
        'DJANGO_SETTINGS_MODULE must point to trader.trader.settings'
        )

try:
    from trader.marketdata import models as md_models
except:
    from marketdata import models as md_models

import scraper

app = Celery(
        'barchart_tasks',
        broker='amqp://127.0.0.1',
        backend='amqp',
    )

app.conf['CELERY_DEFAULT_QUEUE'] = 'fetcher'

# ----------------------------------

DISPLAY = None
def STARTDISPLAY():
    global DISPLAY
    if DISPLAY is None:
        DISPLAY = Display(visible = 0, size=(2560,1440))
        DISPLAY.start()
        logging.info("set Display(visible = 0, size=(2560,1440))")


def KILLDISPLAY():
    global DISPLAY
    DISPLAY.stop()


def restart_all_workers():
    app.control.broadcast('pool_restart')

@app.task
def fetch(barchart_id):

    STARTDISPLAY()
    '''Here we check previous bets again to make sure we don't go over limit.
    '''
    scraper.fetch(barchart_id, "chrome-nodisplay")
