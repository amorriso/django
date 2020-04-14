#!/usr/bin/python
from apscheduler.schedulers.background import BackgroundScheduler
import os
import urlparse
import datetime
import pytz
import django.utils
import sys
import time
import pdb
import logging
import logging.config

import barchart_celery_framework.barchart.barchart_tasks

if "DJANGO_SETTINGS_MODULE" not in os.environ:
    raise EnvironmentError(
        'DJANGO_SETTINGS_MODULE must point to webapp.webapp.settings'
        )

settings = utils.load_settings(
        'settings.barchart', 
        'settings.logger',
        'settings.webserver',
    )

from webapp.rawfeed import models as rawfeed_models
from webapp.feed import models as feed_models

logging.config.fileConfig(
        settings['GLOBAL_LOGGING_PROCESS_CONF'],
        {"logging_server" : settings['GLOBAL_LOGGING_SERVER'],},
    )

logging.info('starting bfuk_win_get_odds')

if __name__ == '__main__':

    '''
    Here we initiate a Celery task.
    '''
    local_timezone = pytz.timezone(settings['BFUK_TIMEZONE'])

    utc_timezone = pytz.timezone('UTC')
    utc_day_tuple = utc_timezone.localize(utils.time_now()).timetuple()[0:3]

    utc_restart_timeonly_tuple = settings['BFUK_WIN_FETCH_ODDS_SCHEDULER_RESET']
    utc_restart_time = utc_timezone.localize(
            datetime.datetime(
                *(datetime.datetime.utcnow().timetuple()[0:3] +
                    utc_restart_timeonly_tuple)
            )
        )

    local_restart_time = utc_restart_time.astimezone(local_timezone)
    local_now = utils.tzaware_time_now(local_timezone)

    if local_restart_time < local_now:
        local_restart_time += datetime.timedelta(days = 1)

    logging.info('local machine time: ' + str(local_now))
    logging.info('next restart time: ' + str(local_restart_time))

    obarchart = barchart_utils.Oddsbarchart(settings['BFUK_WIN_FEEDNAME'])

    # Start the scheduler
    sched = BackgroundScheduler(timezone = local_timezone)
    sched.start()

    LOOP_MINUTES = 10
    fetch_info_times = settings['BFUK_WIN_FETCH_ODDS_AT']
#    delayed_race_guid_fetchtime_tuple_set = set([])

    while True:

        logging.info('looking for new races: ' + str(
                utils.tzaware_time_now(utc_timezone))
            )
        race_obj_list = obarchart.get_new_rawrace_objs(
                utils.tzaware_time_now(utc_timezone), LOOP_MINUTES + (LOOP_MINUTES/2)
            )
    
        for race in race_obj_list:

            for t, resub, failc, delay in fetch_info_times:
                fetch_time = race.scheduled_jump + datetime.timedelta(
                        seconds = t
                    )
                logging.info('adding bfuk_fetch_win_odds.delay at: ' + \
                        str(fetch_time) + ', for venue: ' + race.venue_tag + \
                        ', scheduled_jump: ' + str(race.scheduled_jump)
                    )
                sched.add_job(
                        barchart_celery_framework.barchart.barchart_tasks.bfuk_fetch_win_odds.delay,
                        args = [
                                resub,
                                failc,
                                delay,
                                race.guid, 
                                settings['BFUK_TIMEZONE'],
                                race.country.code3,
                                race.venue_tag,
                                str(race.scheduled_jump),
                                race.url,
                                urlparse.urljoin(
                                        settings['HANDLER_ODDS_ROOT_URL'],
                                        race.feed.archive_url
                                    )
                            ],
                        next_run_time = fetch_time,
                        misfire_grace_time = 60,
                        max_instances = 10
                    )

#        # -- get delayed races
#        delayed_race_ejt_tuple_list = obarchart.get_upcoming_delayed_races(
#                utils.tzaware_time_now(utc_timezone), LOOP_MINUTES + (LOOP_MINUTES/2)
#            )
#
#        for race, ejt in delayed_race_ejt_tuple_list:
#
#            for t in fetch_times:
#                fetch_time = ejt + datetime.timedelta( seconds = t )
#                guid_fetchtime_tuple = (race.guid, fetch_time)
#
#                if not guid_fetchtime_tuple in delayed_race_guid_fetchtime_tuple_set:
#
#                    logging.info('adding DELAYED bfuk_fetch_win_odds.delay at: ' + \
#                            str(fetch_time) + ', for venue: ' + race.venue_tag + \
#                            ', DELAYED_jump: ' + str(ejt)
#                        )
#
#                    sched.add_job(
#                            barchart_celery_framework.barchart.barchart_tasks.bfuk_fetch_win_odds.delay,
#                            args = [
#                                    race.guid, 
#                                    settings['BFUK_TIMEZONE'],
#                                    race.country.code3,
#                                    race.venue_tag,
#                                    str(race.scheduled_jump),# scheduled_jump is correct here!
#                                    race.url,
#                                    urlparse.urljoin(
#                                            settings['HANDLER_ODDS_ROOT_URL'],
#                                            race.feed.archive_url
#                                        )
#                                ],
#                            next_run_time = fetch_time,
#                            misfire_grace_time = 60,
#                            max_instances = 10
#                        )
#
#                    delayed_race_guid_fetchtime_tuple_set.add(
#                            guid_fetchtime_tuple 
#                        )
#                


                        


        # The scheduler will now sit in the below loop until local_restart_time
        # Note that here every LOOP_MINUTES we'll break out of the loop below in the 
        # the While loop above, here we'll see if any new races have been added
        # if they have we'll add schedule events to extract the odds associated
        # with these.
        counter = 0
        while True:
            counter += 1
            if counter >= LOOP_MINUTES:
                break
            if utils.tzaware_time_now(local_timezone) <= local_restart_time:
                #print utils.tzaware_time_now(local_timezone)
                time.sleep(60)
            else:
                message = "Resetting scheduler: " + __file__.split('/')[-1]
                try:
                    barchart_celery_framework.barchart.barchart_tasks.KILLDISPLAY()
                except Exception as e:
                    m = "KILLDISPLAY() failed! ???"
                    #logging.error(m)
                raise SystemExit(message)
           

