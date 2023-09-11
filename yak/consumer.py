#!/usr/bin/env python3

""" 
- Consumer consumes the messages from the topic✅
- if --from-beginning is given before starting the consumer process then 
  all the messages which have been sent to the topic previously should be consumed✅

"""
import pika
import requests
from requests.exceptions import ConnectionError

from .utils import read_metadata


class Consumer:
    """YAK class to consume messages published to a topic"""

    count = 0

    def __init__(self) -> None:
        Consumer.count += 1
        self.LEADER_PORT = read_metadata()
        self.leader_url = f"http://localhost:{self.LEADER_PORT}"

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        self.channel = self.connection.channel()

    def __del__(self):
        """
        Destructor for YAK class Consumer.
        E.g:
        c = Consumer()

        del c # this will call destructor
        """
        Consumer.count -= 1

    @classmethod
    def get_producer_count(cls):
        return Consumer.count

    @staticmethod
    def callback(ch, method, properties, body):
        print('[x] Received - "%s"' % (body.decode("utf-8")))

    def recv(self, topic: str, from_beginning: bool = False) -> str:
        """
        Consume message(s) from the topic.
        if from_beginning=True then all the messages which were published to the topic will be returned
        """
        try:
            headers = {}
            headers["Content-Type"] = "application/json"

            if from_beginning:
                response = requests.get(
                    f"{self.leader_url}/topic/{topic}?from_beginning=1"
                )
                all_msgs = dict(response.json())

                if all_msgs.get("info") is not None:
                    for msg in all_msgs.get("info").split(","):
                        print(msg, end="")
                elif all_msgs.get("is_empty") is not None:
                    pass

            data = {"is_consumer": 1}
            _ = requests.post(
                f"{self.leader_url}/topic/{topic}", json=data, headers=headers
            )

            self.channel.queue_declare(queue=topic)
            self.channel.basic_consume(
                queue=topic, on_message_callback=self.callback, auto_ack=True
            )
            self.channel.start_consuming()

        except ConnectionError:
            print("Leader is not online")
            self.LEADER_PORT = read_metadata()
            self.recv(topic, from_beginning=from_beginning)

        except KeyboardInterrupt:
            print("Closing...")
            # Gracefully close the connection
            self.connection.close()
        except Exception as e:
            print(e)
