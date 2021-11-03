import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from typing import List, Tuple


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


def apply_func_multiprocess(func, iterable_of_args: List[Tuple], nb_workers=-2, **kwargs):
	import tqdm
	from multiprocessing import Pool
	import psutil

	if nb_workers == -1:
		nb_workers = psutil.cpu_count(logical=True)
	elif nb_workers == -2:
		nb_workers = psutil.cpu_count(logical=False)
	assert nb_workers > 0

	q_listener, q = multiprocess_logger_init()

	with tqdm.tqdm(total=len(iterable_of_args), desc=kwargs.get("desc"), unit=kwargs.get("unit")) as pbar:
		with Pool(nb_workers, worker_init, [q]) as pool:
			def callback(*args):
				pbar.update()
				return

			results = [
				pool.apply_async(
					func,
					args=args,
					callback=callback
				)
				for args in iterable_of_args
			]
			outputs = [r.get() for r in results]

	q_listener.stop()
	return outputs