import functools
import logging
import time


def log_func(_func=None, *, box_length=50, box_char='-', logging_func=logging.info):
    def decorator_log_func(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            head = (box_char*box_length) + ' ' + func.__name__ + ' ' + (box_char*box_length)
            logging_func(head)
            out = func(*args, **kwargs)
            elapsed_time_msg = f"<---> Elapsed time {time.time() - start_time:.2}s <--->"
            logging_func(elapsed_time_msg)
            logging_func(box_char*len(head))
            return out
    
        wrapper.__name__ = func.__name__ + "@log_func"
        return wrapper
    
    if _func is None:
        return decorator_log_func
    else:
        return decorator_log_func(_func)

