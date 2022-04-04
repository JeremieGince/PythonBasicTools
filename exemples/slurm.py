import json
import os
import sys
import logging
from src.pythonbasictools.slurm import SlurmHostServer, generate_slurm_cmd, send_slurm_cmd
from src.pythonbasictools import logs_file_setup

if __name__ == "__main__":
	if len(sys.argv) == 3:
		run_count: int = int(sys.argv[1])
		bash_file_to_run: str = sys.argv[2]
	else:
		run_count: int = 1
		bash_file_to_run: str = None

	job_to_cancel = None

	logs_file_setup(__file__)

	servers = [
		SlurmHostServer.BELUGA,
		SlurmHostServer.GRAHAM,
		SlurmHostServer.CEDAR,
	]

	logging.info(f"Host servers --> " + ', '.join([f"{server.name}: {server.value}" for server in servers]))
	logging.info(f"file to run in sbatch: {bash_file_to_run}")

	# credential file must be named as ~/user/credential.json and must have the following form:
	"""
	{
		"username": "[username]",
		"password": "[password]"
	}
	"""
	credential = json.load(open(os.path.join(os.getcwd(), "credential.json")))

	cmd = generate_slurm_cmd(
		repository_root="<Repository name>",
		credential=credential,
		bash_file_to_run=bash_file_to_run,
		run_count=run_count,
		job_to_cancel=job_to_cancel,
	)

	send_slurm_cmd(
		hostnames=[server.value for server in servers],
		port=22,
		username=credential['username'],
		password=credential['password'],
		cmd_to_execute=cmd,
	)