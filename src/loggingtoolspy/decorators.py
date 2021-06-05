import logging
import time


def log_func(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logging.info(f"\n--- {func.__name__} -> begin --- \n")
        out = func(*args, **kwargs)
        logging.info(f"\n--- {func.__name__} -> end in {time.time() - start_time:.2}s ---\n")
        return out

    wrapper.__name__ = func.__name__ + "@log_func"
    return wrapper




