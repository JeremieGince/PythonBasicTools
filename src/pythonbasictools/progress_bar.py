import logging


def printProgressBar(
        iteration,
        total,
        prefix='',
        suffix='',
        decimals=0,
        length=100,
        fill='█',
        printEnd='',
        current_elapse_seconds=None,
        log_func=print,
):
    """
    Call in a loop to create terminal progress bar
    
    :param iteration: Current iteration
    :type iteration: int
    :param total: Total iterations
    :type total: int
    :param prefix: Prefix string
    :type prefix: str
    :param suffix: Suffix string
    :type suffix: str
    :param decimals: Positive number of decimals in percent complete
    :type decimals: int
    :param length: Character length of bar
    :type length: int
    :param fill: Bar fill character
    :type fill: str
    :param printEnd: end parameter of the print function
    :type printEnd: str
    :param current_elapse_seconds: The current elapsed time in seconds.
    :type current_elapse_seconds: float
    :param log_func: The logging function to use to log the function call.
    :type log_func: Callable
    
    :return: None
    """
    import warnings
    import os

    os.getpid()

    if iteration > total:
        warnings.warn("progress bar not use properly: iteration > total")
        return
    import time
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if current_elapse_seconds is None:
        progress_bar = f'{prefix} |{bar}| {iteration}/{total}, {percent}%, {suffix}'
    else:
        sec_per_itr = max(1e-12, current_elapse_seconds / max(1, iteration))
        remaining_time = int((total - iteration) * sec_per_itr)
        remaining_time = time.strftime('%H:%M:%S', time.gmtime(remaining_time))
        current_elapse_seconds = time.strftime('%H:%M:%S', time.gmtime(current_elapse_seconds))
        progress_bar = f'{prefix} |{bar}| {iteration}/{total}, ' \
                       f'[{current_elapse_seconds}<{remaining_time}, {int(1/sec_per_itr)}itr/s] ' \
                       f'{percent}% {suffix}'
    # Print New Line on Complete
    if iteration == total:
        log_func('\r'+progress_bar.replace(fill, '#'))
    else:
        log_func('\r' + progress_bar, end=printEnd)





