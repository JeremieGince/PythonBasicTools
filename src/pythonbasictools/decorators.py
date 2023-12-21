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


def try_func_n_times(_func=None, *, n: int = 32, delay: float = 0.1):
    def decorator_try_func_n_times(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            out = None
            for i in range(n):
                try:
                    out = func(*args, **kwargs)
                    break
                except Exception as e:
                    if i == n - 1:
                        raise e
                    else:
                        time.sleep(delay)
            return out

        wrapper.__name__ = func.__name__ + "@log_func"
        return wrapper

    if _func is None:
        return decorator_try_func_n_times
    else:
        return decorator_try_func_n_times(_func)


def save_on_exit(save_func_name="to_pickle", *save_args, **save_kwargs):
    """
    Decorator for a method that saves the object on exit.

    :param save_func_name: The name of the method that saves the object.
    :type save_func_name: str
    :param save_args: The arguments of the save method.
    :type save_args: tuple
    :param save_kwargs: The keyword arguments of the save method.
    :return: The decorated method.
    """
    
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            finally:
                if not hasattr(self, save_func_name):
                    raise AttributeError(
                        f"The object {self.__class__.__name__} does not have a save method named {save_func_name}."
                    )
                getattr(self, save_func_name)(*save_args, **save_kwargs)
        
        return wrapper
