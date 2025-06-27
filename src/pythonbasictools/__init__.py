import importlib_metadata

__author__ = "Jérémie Gince"
__email__ = "gincejeremie@gmail.com"
__copyright__ = "Copyright 2021, Jérémie Gince"
__license__ = "Apache 2.0"
__url__ = "https://github.com/JeremieGince/PythonBasicTools"
__package__ = "pythonbasictools"
__version__ = importlib_metadata.version(__package__)

from . import cmds, docstring, google_drive, lock
from .collections_tools import list_insert_replace_at, ravel_dict, sequence_get
from .decorators import log_func
from .device import DeepLib, log_device_setup
from .hash_tools import hash_dict
from .logging_tools import logs_file_setup
from .multiprocessing_tools import (
    apply_func_multiprocess,
    multiprocess_logger_init,
    worker_init,
)
from .run_output_file import RunOutputFile
from .slurm import SlurmHostServer, generate_slurm_cmd, send_slurm_cmd
