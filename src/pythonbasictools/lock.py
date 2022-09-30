import os
import time


class FileLock:
	"""
	Class used to lock a process across multiple ones. This can be very useful when you want to use a file across
	multiple different processes or different applications.
	
	:Attributes:
		- :attr:`lock_path` (str): The path to the lock file.
		- :attr:`wait_time` (float): The time to wait between each check of the lock file in seconds.
		- :attr:`process_name` (str): The name of the process.
		
	:Methods:
		- :meth:`acquire`: Acquire the lock.
		- :meth:`release`: Release the lock.
		- :meth:`__enter__`: Acquire the lock.
		- :meth:`__exit__`: Release the lock.
		
	:Example:
		>>> with FileLock():
		>>> 	# Do something
		
		>>> lock = FileLock()
		>>> lock.acquire()
		>>> # Do something
		>>> lock.release()
		
		>>> data_path = "data.txt"
		>>> lock = FileLock()
		>>> with lock:
		>>> 	with open(data_path, "r") as f:
		>>> 		data = f.read()
		>>> 	# Do something with data
		>>> 	with open(data_path, "w") as f:
		>>> 		f.write(data)
	"""
	def __init__(
			self,
			lock_path: str = './lock.lck',
			wait_time: float = 0.1,
			process_name: str = "process"
	):
		"""
		Constructor of the class.
		
		:param lock_path: The path to the lock file.
		:type lock_path: str
		:param wait_time: The time to wait between each check of the lock file in seconds.
		:type wait_time: float
		:param process_name: The name of the process.
		:type process_name: str
		"""
		self.lock_path = lock_path
		self.wait_time = wait_time
		self.process_name = process_name
		self._acquired = False
	
	def acquire(self):
		"""
		Acquire the lock.
		
		:return: None
		"""
		self.__enter__()
	
	def release(self):
		"""
		Release the lock.
		
		:return: None
		"""
		self.__exit__(None, None, None)
	
	def __enter__(self):
		while os.path.exists(self.lock_path):
			time.sleep(self.wait_time)
		file_content = f"Process: {self.process_name}\nLock acquired at time {time.time()}"
		with open(self.lock_path, "w") as f:
			f.write(file_content)
		self._acquired = True
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if self._acquired and os.path.exists(self.lock_path):
			os.remove(self.lock_path)
		if self._acquired:
			self._acquired = False
		
	def __del__(self):
		if self._acquired:
			self.release()


