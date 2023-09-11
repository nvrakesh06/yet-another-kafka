#!/usr/bin/env python3

""" 
- Producer produces/publishes the messages to the topics
- Number of producers should be dynamic

"""
import requests
from requests.exceptions import ConnectionError

from .utils import read_metadata


class Producer:
    """YAK class to publish messages to particular topic"""

    count = 0

    def __init__(self) -> None:
        Producer.count += 1
        self.LEADER_PORT = read_metadata()
        self.leader_url = f"http://localhost:{self.LEADER_PORT}"

    def __del__(self):
        """
        Destructor for YAK class Producer.

        E.g:
        p = Producer()

        del p # this will call destructor
        """
        Producer.count -= 1

    @classmethod
    def get_producer_count(cls):
        return Producer.count

    def send(self, topic: str, msg: str) -> int:
        """
        Publish message(s) to the topic. Returns acknowledgement. If 1 is returned then published message is
        received by the leader, else 0 is returned.
        """
        ack: int = 0

        try:
            topic_url = f"{self.leader_url}/topic/{topic}"

            headers = {}
            headers["Content-Type"] = "application/json"

            payload = {"msg": msg}

            response = requests.post(topic_url, json=payload, headers=headers)
            ack = response.json().get("ack")  # ack = 1

        except ConnectionError:
            print("Leader is not online, trying to reconnect.")
            self.LEADER_PORT = read_metadata()

        return ack
