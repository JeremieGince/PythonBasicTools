import logging
import multiprocessing
from logging.handlers import QueueHandler, QueueListener
from typing import List, Tuple, Optional, Dict


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
		available CPUs.
	:type nb_workers: int
	:param kwargs: The additional arguments.
	
	:keyword str desc: The description of the function to apply. See tqdm.tqdm for more details.
	:keyword str unit: The unit of the function to apply. See tqdm.tqdm for more details.
	:keyword bool verbose: Whether to print the progress bar or not. Default to True.
	
	:return: The list of results.
	
	:raises ValueError: If the length of iterable_of_args and iterable_of_kwargs are not the same.
	
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

	if nb_workers == -1:
		nb_workers = psutil.cpu_count(logical=True)
	elif nb_workers == -2:
		nb_workers = psutil.cpu_count(logical=False)
	assert nb_workers > 0
	
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
