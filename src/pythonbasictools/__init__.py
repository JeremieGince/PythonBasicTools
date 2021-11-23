__author__ = "Jérémie Gince"
# repository: https://github.com/JeremieGince/PythonBasicTools

from .logging import logs_file_setup
from .device import DeepLib, log_device_setup
from .decorators import log_func
from .multiprocessing import worker_init, multiprocess_logger_init
