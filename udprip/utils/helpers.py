import time


def current_time():
    return time.time()


def has_expired(last_time, period, factor=4):
    return (time.time() - last_time) > (factor * period)
