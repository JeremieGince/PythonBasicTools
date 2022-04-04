import enum
import logging
from typing import Dict, List

import paramiko


class SlurmHostServer(enum.Enum):
	BELUGA = "beluga.computecanada.ca"
	GRAHAM = "graham.sharcnet.ca"
	HELIOS = "helios.calculquebec.ca"
	CEDAR = "cedar.computecanada.ca"


def send_slurm_cmd(hostnames, port, username, password, cmd_to_execute):
	"""
	Send a command to a host.
	:param hostnames: The hostname of the host to send the command to.
	:param port: The port to connect to.
	:param username: The username to connect with.
	:param password: The password to connect with.
	:param cmd_to_execute: The command to execute.
	:return: The output of the command.
	"""
	if not isinstance(hostnames, list):
		hostnames = [hostnames]
	opts = []
	for hostname in hostnames:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostname, port=port, username=username, password=password)
		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('\n'.join(cmd_to_execute))
		logging.info(str(ssh_stdin) + '\n' + str(ssh_stdout) + '\n' + str(ssh_stderr))
		logging.info("-" * 175)
		opt = ssh_stdout.readlines()
		opt = "".join(opt)
		logging.info(opt)
		opts.append(opt)
	return opts


def generate_slurm_cmd(
		repository_root: str,
		credential: Dict[str, str],
		bash_file_to_run: str = None,
		run_count: int = 1,
		job_to_cancel: str = None,
) -> List[str]:
	"""
	Generate a command to run on a host.
	:param repository_root: The root directory of the repository.
	:param credential: The credential to use.
		Must be in the format:
		{
			"username": "<username>",
			"password": "<password>"
		}
	:param bash_file_to_run: The bash file to run.
	:param run_count: The number of times to run the bash file.
	:param job_to_cancel: The job to cancel.
	:return: The command to run.
	"""
	cmd = [
		f"cd {repository_root}",
		"git pull",
		"ls",
	]
	if bash_file_to_run is not None:
		for _ in range(run_count):
			cmd.append(f"sbatch {bash_file_to_run}")
	if job_to_cancel is not None:
		cmd.append(f"scancel {job_to_cancel}")
	cmd.append(f"squeue -u {credential['username']}")
	return cmd
