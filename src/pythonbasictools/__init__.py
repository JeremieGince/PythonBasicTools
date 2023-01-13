__author__ = "Jérémie Gince"
__email__ = "gincejeremie@gmail.com"
__copyright__ = "Copyright 2021, Jérémie Gince"
__license__ = "Apache 2.0"
__url__ = "https://github.com/JeremieGince/PythonBasicTools"
__version__ = "0.0.1-alpha.3"

from .logging import logs_file_setup
from .device import DeepLib, log_device_setup
from .decorators import log_func
from .multiprocessing import worker_init, multiprocess_logger_init
from .slurm import SlurmHostServer, send_slurm_cmd, generate_slurm_cmd
from . import docstring
