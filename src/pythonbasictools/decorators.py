import functools
import logging
import time


def log_func(_func=None, *, box_length=50, box_char='-', logging_func=logging.info):
    """
    Log the function call and the time it took to execute.
    
    :param _func: The function to decorate.
    :type _func: Callable
    :param box_length: The length of the box to use to log the function call.
    :type box_length: int
    :param box_char: The character to use to log the function call.
    :type box_char: str
    :param logging_func: The logging function to use to log the function call.
    :type logging_func: Callable
    
    :return: The decorated function.
    """
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

