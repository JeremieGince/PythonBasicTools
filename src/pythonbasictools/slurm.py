import enum
import logging
from typing import Dict, List, Optional


class SlurmHostServer(enum.Enum):
	"""
	Enum of the different Slurm host server.
	"""
	BELUGA = "beluga.computecanada.ca"
	GRAHAM = "graham.sharcnet.ca"
	HELIOS = "helios.calculquebec.ca"
	CEDAR = "cedar.computecanada.ca"


def send_slurm_cmd(hostnames, port, username, password, cmd_to_execute):
	"""
	Send a command to a host.
	
	:param hostnames: The hostname of the host to send the command to.
	:type hostnames: str
	:param port: The port to connect to.
	:type port: int
	:param username: The username to connect with.
	:type username: str
	:param password: The password to connect with.
	:type password: str
	:param cmd_to_execute: The command to execute.
	:type cmd_to_execute: str
	
	:return: The output of the command.
	:rtype: str
	"""
	import paramiko
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
		credential: Optional[Dict[str, str]] = None,
		bash_file_to_run: str = None,
		run_count: int = 1,
		job_to_cancel: str = None,
) -> List[str]:
	"""
	Generate a command to run on a host.
	
	:param repository_root: The root directory of the repository.
	:type repository_root: str
	:param credential: The credential to use. If provided, must contain the following key: "username".
	:type credential: Optional[Dict[str, str]]
	:param bash_file_to_run: The bash file to run.
	:type bash_file_to_run: str
	:param run_count: The number of times to run the bash file.
	:type run_count: int
	:param job_to_cancel: The job to cancel.
	:type job_to_cancel: str
	
	:return: The command to run.
	:rtype: List[str]
	
	:Exemple:
		
		>>> generate_slurm_cmd(
		...     repository_root="./GitHub/pythonbasictools",
		...     credential={
		...         "username": "user",
		...         "password": "password"
		...     },
		...     bash_file_to_run="./GitHub/pythonbasictools/jobs/test.sh",
		...     run_count=1,
		...     job_to_cancel="123456"
		... )
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
	if credential is not None:
		cmd.append(f"squeue -u {credential['username']}")
	return cmd
