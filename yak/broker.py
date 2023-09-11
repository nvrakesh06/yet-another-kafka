#!/usr/bin/env python3

""" 
- Total 3 instances of brokers should be created✅
- One of the broker should be made as a leader✅
- Leader should maintain/create topics✅
- Leader should know which messages are not yet received by the consumer✅
- All brokers should maintain logs of all the operations✅

Topics
- topics should be stored as directories/folders, 
within those folders the message contents should be stored as partitions✅

POST localhost:LEADER_PORT/<str:topic> - by PRODUCER
    - store the message as partition
    - send to all consumer who are subscribed to particular topic

GET localhost:LEADER_PORT/<str:topic> - by CONSUMER
    - start consuming/streaming all the messages sent to particular topic
 
How to detect failure of leader?
- Use heartbeats to check the status of the leader✅

"""
import glob
import logging
import os
import pathlib
import sys

import pika
from flask import Flask, jsonify, request
from utils import topic_exists
from zoo_keeper import LEADER_PORT

if len(sys.argv) < 2:
    print("PORT not provided")
    sys.exit(1)

app = Flask(__name__)


LEADER_PORT = sys.argv[1]
STATUS = 200
MAX_LINES_PER_FILE = 5
here = pathlib.Path(__file__).parent.resolve()

# Fixes the issue of color not rendering in Windows Powershell/CMD
import ctypes

kernel32 = ctypes.windll.kernel32
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

logger = logging.getLogger("yak")
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f"{here}/logs/operations.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

for log_name, log_obj in logging.Logger.manager.loggerDict.items():
    if log_name != "yak":
        log_obj.disabled = True


@app.route("/status", methods=["GET"])
def status():

    if request.method == "GET":
        return {
            "MESSAGE": "Broker is running",
            "STATUS": STATUS,
            "LEADER_PORT": LEADER_PORT,
        }


@app.route("/topic/<topic>", methods=["GET", "POST"])
def broker_communication(topic):

    if request.method == "GET":
        try:
            if request.args.get("from_beginning") is not None:
                topic_path: str = f"{here}\\topics\\{topic}"

                all_data: str = ""

                list_of_files = glob.glob(f"{topic_path}/*.txt")

                if len(list_of_files) == 0:
                    return {"is_empty": 1}

                # list files in the order of creation
                sorted_files = sorted(list_of_files, key=os.path.getctime)

                for file in sorted_files:
                    with open(file) as f:
                        msgs = f.readlines()
                        all_data += ",".join((msg for msg in msgs))

                return jsonify({"info": all_data})
        except Exception as e:
            print(e)
            return {"error": e}

    if request.method == "POST":
        # PRODUCER & CONSUMER

        try:
            topic_path: str = f"{here}\\topics\\{topic}"

            if not topic_exists(topic):
                # create a new topic
                os.mkdir(topic_path)

            # print(request.get_data(as_text=True))
            DATA: dict = request.get_json()

            if DATA.get("is_consumer") is not None:
                channel.queue_declare(queue=topic)
                return {"ack": 1}

            channel.queue_declare(queue=topic)
            channel.basic_publish(exchange="", routing_key=topic, body=DATA.get("msg"))

            # * means all if need specific format then *.txt
            list_of_files = glob.glob(f"{topic_path}/*.txt")

            if len(list_of_files) > 0:
                # if file exists

                latest_file = max(list_of_files, key=os.path.getctime)
                file_name_count = int(latest_file.split(".")[0].split("\\")[-1])

                with open(latest_file, "r") as f:
                    data = f.readlines()
                    no_lines_present = len(data) + 1

                if no_lines_present > MAX_LINES_PER_FILE:
                    # create new file
                    with open(f"{topic_path}/{file_name_count+1}.txt", "a+") as new_f:
                        new_f.write(DATA.get("msg") + "\n")

                else:
                    with open(latest_file, "w") as f:
                        # write the msg and increment line count
                        data.append(DATA.get("msg") + "\n")
                        f.writelines(data)

            else:
                # create new file and write the msg
                print("first time write")
                with open(f"{topic_path}/1.txt", "a+") as new_f:
                    new_f.write(DATA.get("msg") + "\n")

            return {"ack": 1}

        except Exception as e:
            print(e)
            return {"ack": 0, "error": e}


if __name__ == "__main__":
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    app.run(debug=True, port=LEADER_PORT)
