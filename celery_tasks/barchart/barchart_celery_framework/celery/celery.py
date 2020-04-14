from __future__ import absolute_import

from celery import Celery

# instantiate Celery object and hand it a list containing the relative
# (to where you start the Celery daemon!) path to all modules containing 
# Celery tasks.
celery = Celery(include = [
        'barchart_celery_framework.barchart.barchart_tasks'
    ])

# import celery config file
celery.config_from_object('celeryconfig')

if __name__ == '__main__':
    celery.start()
