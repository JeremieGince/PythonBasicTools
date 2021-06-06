from discord_webhook import DiscordWebhook
import logging


def send_logs_file_to_discord(webhook_urls: str):
    webhook = DiscordWebhook(url=webhook_urls)
    filenames = [
        getattr(h, "baseFilename")
        for h in logging.root.handlers
        if hasattr(h, "baseFilename")
    ]

    for filename in filenames:
        with open(filename, "r") as f:
            webhook.add_file(file=f.read(), filename=filename)

    return webhook.execute()


