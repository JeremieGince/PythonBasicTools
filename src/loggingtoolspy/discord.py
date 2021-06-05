import requests
from discord import Webhook, RequestsWebhookAdapter

webhook = Webhook.from_url("url-here", adapter=RequestsWebhookAdapter())
webhook.send("Hello World")
