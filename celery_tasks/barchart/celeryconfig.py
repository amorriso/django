# config file for Celery Daemon
BROKER_URL = 'amqp://127.0.0.1'
CELERY_HIJACK_ROOT_LOGGER = False
CELERY_DEFAULT_QUEUE = 'fetcher'
CELERYD_LOG_FORMAT = "[%(levelname)s/%(processName)s, %(asctime)s, %(funcName)s, %(filename)s]: %(message)s"
CELERYD_MAX_TASKS_PER_CHILD = 36000 # at 10 sec a task - run for 10 hours
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_TASK_TIME_LIMIT = 30
CELERYD_POOL_RESTARTS = True
