import enum
import logging


class DeepLib(enum.Enum):
    """
    Enumerate the different deep learning libraries.
    """
    Null = -1
    Pytorch = 0
    Tensorflow = 1
    SkLearn = 2


def log_device_setup(deepLib: DeepLib = DeepLib.Null, level=logging.INFO):
    """
    Log the device setup.
    
    :param deepLib: The deep learning library to use.
    :type deepLib: DeepLib
    :param level: The logging level to use.
    :type level: int
    
    :return: None
    """
    import sys
    import psutil
    import multiprocessing

    logging.info(f'__Python VERSION: {sys.version}')
    logging.info(f"Number of available cores: {psutil.cpu_count(logical=False)}.")
    logging.info(f"Number of available logical processors: {multiprocessing.cpu_count()}.")

    setup_func = {
        DeepLib.Null: lambda *args: None,
        DeepLib.Pytorch: log_pytorch_device_setup,
        DeepLib.Tensorflow: log_tensorflow_device_setup,
        DeepLib.SkLearn: log_sklearn_device_setup,
    }
    setup_func[deepLib](level)


def log_pytorch_device_setup(level=logging.INFO):
    """
    Log the Pytorch device setup.
    
    :param level: The logging level to use.
    :type level: int
    
    :return: None
    """
    from subprocess import check_output
    import torch

    logging.info(f'__pyTorch VERSION:{torch.__version__}')
    try:
        logging.info(f'__CUDA VERSION:\n{check_output(["nvcc", "--version"]).decode("utf-8")}')
    except FileNotFoundError:
        logging.info('__CUDA VERSION:Not Found')

    try:
        logging.info(f'__nvidia-smi:\n{check_output(["nvidia - smi",]).decode("utf-8")}')
    except FileNotFoundError:
        logging.info('__nvidia-smi: Not Found')
    logging.info(f'__CUDNN VERSION:{torch.backends.cudnn.version()}')
    logging.info(f'__Number CUDA Devices:{torch.cuda.device_count()}')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"\n{'-' * 25}\nDEVICE: {device}\n{'-' * 25}\n")

    # Additional Info when using cuda
    if device.type == 'cuda':
        logging.info(torch.cuda.get_device_name(0))
        logging.info('Memory Usage:')
        logging.info(f'Allocated: {round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1)} GB')
        logging.info(f'Cached:   {round(torch.cuda.memory_reserved(0) / 1024 ** 3, 1)} GB')
        logging.info(f"Memory summary: \n{torch.cuda.memory_summary()}")


def log_tensorflow_device_setup(level=logging.INFO):
    """
    Log the Tensorflow device setup.
    
    :param level: The logging level to use.
    :type level: int
    
    :return: None
    """
    import tensorflow as tf
    from subprocess import check_output
    logging.info(f'__tensorflow VERSION:{tf.__version__}')
    try:
        logging.info(f'__CUDA VERSION:\n{check_output(["nvcc", "--version"]).decode("utf-8")}')
    except FileNotFoundError:
        logging.info('__CUDA VERSION:Not Found')
    try:
        logging.info(f'__nvidia-smi:\n{check_output(["nvidia - smi",]).decode("utf-8")}')
    except FileNotFoundError:
        logging.info('__nvidia-smi: Not Found')
    physical_devices = tf.config.list_physical_devices('GPU')
    logging.info(f"physical_devices: {physical_devices}")
    logical_devices = tf.config.list_logical_devices('GPU')
    logging.info(f"logical_devices: {logical_devices}")
    set_tf_loglevel(level)


def set_tf_loglevel(level=logging.INFO):
    """
    Set the Tensorflow log level.
    
    :param level: The logging level to use.
    :type level: int
    
    :return: None
    """
    import os
    if level >= logging.FATAL:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    if level >= logging.ERROR:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    if level >= logging.WARNING:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
    else:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
    logging.getLogger('tensorflow').setLevel(level)


def log_sklearn_device_setup(level=logging.INFO):
    """
    Log the SkLearn device setup.
    
    :param level: The logging level to use.
    :type level: int
    
    :return: None
    """
    import sklearn
    logging.info(f'__sklearn VERSION:{sklearn.__version__}')


