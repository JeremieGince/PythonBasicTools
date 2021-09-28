from src.loggingtoolspy.file import logs_file_setup
from src.loggingtoolspy.discord import send_logs_file_to_discord
import json

if __name__ == '__main__':
    logs_file_setup(__file__)
    url = json.load(open("./user/credential.json"))["webhooks"]
    send_logs_file_to_discord(url)


