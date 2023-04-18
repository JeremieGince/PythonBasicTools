import logging
from typing import Union, List
import pathlib


def send_files_to_discord(webhook_urls: str, file_paths: Union[str, List[str]]):
    """
    Send the logs file to Discord.

    :param webhook_urls: The webhook urls to use to send the files.
    :type webhook_urls: str
    :param file_paths: The file paths to send.
    :type file_paths: Union[str, List[str]]

    :return: The result of the request.
    """
    try:
        from discord_webhook import DiscordWebhook
    except ImportError:
        logging.error("The package discord_webhook must be installed.")
        return -1
    webhook = DiscordWebhook(url=webhook_urls)
    
    if isinstance(file_paths, str):
        file_paths = [file_paths]
    
    for file_path in file_paths:
        try:
            file = pathlib.Path(file_path)
            webhook.add_file(file=file.read_text(), filename=file.name)
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
    
    return webhook.execute()


def send_logs_file_to_discord(webhook_urls: str):
    """
    Send the logs file to Discord.
    
    :param webhook_urls: The webhook urls to use to send the logs file.
    :type webhook_urls: str
    
    :return: The result of the request.
    """
    filenames = [
        getattr(h, "baseFilename")
        for h in logging.root.handlers
        if hasattr(h, "baseFilename")
    ]
    return send_files_to_discord(webhook_urls, filenames)


