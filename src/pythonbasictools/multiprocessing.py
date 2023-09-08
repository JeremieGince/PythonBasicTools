import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from typing import List, Tuple, Optional, Dict, Callable


def worker_init(q):
    # all records from worker processes go to qh and then into q
    qh = QueueHandler(q)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(qh)


def multiprocess_logger_init():
    q = multiprocessing.Queue()
    # this is the handler for all log records
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(asctime)s - %(process)s - %(message)s"))

    # ql gets records from the queue and sends them to the handler
    ql = QueueListener(q, handler)
    ql.start()

    # add the handler to the logger so records from this process are handled
    logging.getLogger().addHandler(handler)

    return ql, q


def _make_callable_from_list(list_of_callable: List[Callable] = None):
    """
    Make a callable from a list of callable.

    :param list_of_callable: The list of callable.
    :type list_of_callable: List[Callable]

    :return: The callable.
    :rtype: Callable

    :raises ValueError: If the list_of_callable contains a non-callable.
    """
    if list_of_callable is None:
        list_of_callable = []

    for c in list_of_callable:
        if not callable(c):
            raise ValueError("The list_of_callable must contain only callable.")

    def _callable(*args, **kwargs):
        for callable_ in list_of_callable:
            callable_(*args, **kwargs)

    return _callable


def apply_func_main_process(
        func,
        iterable_of_args: List[Tuple],
        iterable_of_kwargs: Optional[List[Dict]] = None,
        **kwargs
):
    """
    Apply a function to a list of arguments in the main process.

    :param func: The function to apply.
    :type func: Callable
    :param iterable_of_args: The list of arguments to apply the function to.
    :type iterable_of_args: List[Tuple]
    :param iterable_of_kwargs: The list of keyword arguments to apply the function to.
    :type iterable_of_kwargs: Optional[List[Dict]]
    :param kwargs: The additional arguments.

    :keyword str desc: The description of the function to apply. See tqdm.tqdm for more details.
    :keyword str unit: The unit of the function to apply. See tqdm.tqdm for more details.
    :keyword bool verbose: Whether to print the progress bar or not. Default to True.
    :keyword List[Callable] callbacks: The list of callbacks to call after each iteration.

    :return: The list of results.

    :raises ValueError: If the length of iterable_of_args and iterable_of_kwargs are not the same.

    :Example:
    >>> from pythonbasictools.multiprocessing import apply_func_main_process
    >>> def func(x, y):
    ...     return x + y
    >>> apply_func_main_process(func, [(1, 2), (3, 4)])
    >>> [3, 7]
    """
    import tqdm

    if iterable_of_kwargs is None:
        iterable_of_kwargs = [{} for _ in range(len(iterable_of_args))]

    if len(iterable_of_args) != len(iterable_of_kwargs):
        raise ValueError("The length of iterable_of_args and iterable_of_kwargs must be the same.")

    list_of_callbacks = kwargs.get("callbacks", [])
    if not isinstance(list_of_callbacks, list):
        list_of_callbacks = [list_of_callbacks]

    with tqdm.tqdm(
            total=len(iterable_of_args),
            desc=kwargs.get("desc", None),
            unit=kwargs.get("unit", "it"),
            disable=not kwargs.get("verbose", True),
    ) as pbar:
        callback = _make_callable_from_list(list_of_callbacks)
        results = []
        for args, kwargs in zip(iterable_of_args, iterable_of_kwargs):
            results.append(func(*args, **kwargs))
            pbar.update()
            callback(*args, **kwargs)

    return results


def apply_func_multiprocess(
        func,
        iterable_of_args: List[Tuple],
        iterable_of_kwargs: Optional[List[Dict]] = None,
        nb_workers=-2,
        **kwargs
):
    """
    Apply a function to a list of arguments in parallel.

    :param func: The function to apply.
    :type func: Callable
    :param iterable_of_args: The list of arguments to apply the function to.
    :type iterable_of_args: List[Tuple]
    :param iterable_of_kwargs: The list of keyword arguments to apply the function to.
    :type iterable_of_kwargs: Optional[List[Dict]]
    :param nb_workers: The number of workers to use. If -1, use all the logical available CPUs. If -2, use all the
        available CPUs. If 0, use the main process. If greater than 0, use the specified number of workers.
        Default to -2.
    :type nb_workers: int
    :param kwargs: The additional arguments.

    :keyword str desc: The description of the function to apply. See tqdm.tqdm for more details.
    :keyword str unit: The unit of the function to apply. See tqdm.tqdm for more details.
    :keyword bool verbose: Whether to print the progress bar or not. Default to True.
    :keyword List[Callable] callbacks: The list of callbacks to call after each iteration.
        See multiprocessing.Pool.apply_async for more details.

    :return: The list of results.

    :raises ValueError: If the length of iterable_of_args and iterable_of_kwargs are not the same.
    :raises ValueError: If the number of workers is less than -2.

    :Example:
    >>> from pythonbasictools.multiprocessing import apply_func_multiprocess
    >>> def func(a, b):
    ...     return a + b
    >>> apply_func_multiprocess(func, [(1, 2), (3, 4), (5, 6)])
    >>> [3, 7, 11]
    """
    import tqdm
    from multiprocessing import Pool
    import psutil

    if nb_workers is None:
        nb_workers = -2

    if nb_workers == -1:
        nb_workers = psutil.cpu_count(logical=True)
    elif nb_workers == -2:
        nb_workers = psutil.cpu_count(logical=False)

    if nb_workers == 0:
        return apply_func_main_process(func, iterable_of_args, iterable_of_kwargs, **kwargs)

    if nb_workers < 0:
        raise ValueError("The number of workers must be greater or equal than 0.")

    if iterable_of_kwargs is None:
        iterable_of_kwargs = [{} for _ in range(len(iterable_of_args))]

    if len(iterable_of_args) != len(iterable_of_kwargs):
        raise ValueError("The length of iterable_of_args and iterable_of_kwargs must be the same.")

    q_listener, q = multiprocess_logger_init()

    with tqdm.tqdm(
            total=len(iterable_of_args),
            desc=kwargs.get("desc", None),
            unit=kwargs.get("unit", "it"),
            disable=not kwargs.get("verbose", True),
    ) as pbar:
        with Pool(nb_workers, worker_init, [q]) as pool:
            def p_bar_update_callback(*args, **kwds):
                pbar.update()
                return

            list_of_callbacks = kwargs.get("callbacks", [])
            if not isinstance(list_of_callbacks, list):
                list_of_callbacks = [list_of_callbacks]
            list_of_callbacks.append(p_bar_update_callback)

            results = [
                pool.apply_async(
                    func,
                    args=args,
                    kwds=kwds,
                    callback=_make_callable_from_list(list_of_callbacks)
                )
                for args, kwds in zip(iterable_of_args, iterable_of_kwargs)
            ]
            outputs = [r.get() for r in results]

    q_listener.stop()
    return outputs
