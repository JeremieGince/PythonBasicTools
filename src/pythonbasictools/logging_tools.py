import logging


def logs_file_setup(file: str, level=logging.INFO, root_logs_dir: str = "./", add_stdout: bool = True):
	"""
	Set up the logs file.
	
	:param file: The logs file name.
	:type file: str
	:param level: The level of the logs.
	:type level: int
	:param root_logs_dir: The root directory of the logs.
	:type root_logs_dir: str
	:param add_stdout: Whether to add the stdout handler.
	:type add_stdout: bool
	
	:return: The logs file path.
	:rtype: str
	"""
	import os
	import sys
	import time
	from datetime import date

	today = date.today()
	timestamp = str(time.time()).replace('.', '')
	logs_dir = f"{root_logs_dir}/logs/logs-{today.strftime('%d-%m-%Y')}"
	logs_file = f'{logs_dir}/{os.path.splitext(os.path.basename(file))[0]}-{timestamp}.log'
	os.makedirs(logs_dir, exist_ok=True)
	logging.basicConfig(level=level)
	logging.getLogger().addHandler(logging.FileHandler(logs_file))
	if add_stdout:
		sh = logging.StreamHandler(sys.stdout)
		logging.getLogger().addHandler(sh)
	logging.info(f"Logs file at: {logs_file}\n")
	return logs_file
