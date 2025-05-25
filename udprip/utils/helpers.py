import time


def current_time():
    return time.time()


def has_expired(last_time, period, factor=4):
    print(f'--> Rota expirada: {(time.time() - last_time) > (factor * period)}')
    return (time.time() - last_time) > (factor * period)
