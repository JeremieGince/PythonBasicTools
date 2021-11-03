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
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
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
        # log_func('\r' + progress_bar, end=printEnd)
        # log_func('\r\t*')
        # log_func()
        logging.info('\r'+progress_bar.replace(fill, '#'))
    else:
        log_func('\r' + progress_bar, end=printEnd)





