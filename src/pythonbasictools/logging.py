import logging


def logs_file_setup(file: str, level=logging.INFO, root_logs_dir: str = "./", add_stdout: bool = True):
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
