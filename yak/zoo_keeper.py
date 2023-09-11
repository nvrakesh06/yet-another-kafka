#!/usr/bin/env python3

"""
Functions of zookeeper
- keep track of the leader - Make contacts regularly with the leader✅
- Elect leader from available brokers✅
- always running✅

"""
import sched
import subprocess
import sys
import time

import requests
from requests.exceptions import ConnectionError
from utils import tcolors, update_metadata

ONLINE_PORTS: list = sorted([6060, 7070, 8080])
LEADER_PORT: int = ONLINE_PORTS[0]
HEARTBEAT_FREQUENCY: int = 5  # in seconds


def new_leader() -> int:
    """
    Elect new leader from available broker PORT's
    """
    global ONLINE_PORTS, LEADER_PORT

    ONLINE_PORTS.remove(LEADER_PORT)
    if len(ONLINE_PORTS) == 0:
        print(tcolors.fail("All brokers are OFFLINE"))
        sys.exit(0)

    LEADER_PORT = ONLINE_PORTS[0]
    update_metadata(LEADER_PORT)

    return LEADER_PORT


def start_broker(port: int) -> None:
    """Start the broker server"""
    args: list = f"python yak/broker.py {port}".split(" ")

    subprocess.run(
        args,
        universal_newlines=True,
        shell=True,
        creationflags=subprocess.DETACHED_PROCESS,
    )


def check_status():
    """Check the status of the leader"""
    global LEADER_PORT, ONLINE_PORTS
    try:
        _ = requests.get(f"http://localhost:{LEADER_PORT}/status")

    except ConnectionError:
        print(f"Leader is down on PORT: {tcolors.fail(LEADER_PORT)}", end="\t")

        # Elect new leader
        LEADER_PORT = new_leader()
        print(f"Available Brokers - {tcolors.ok(ONLINE_PORTS)}")

        # start broker on this newly elected leader
        start_broker(LEADER_PORT)


def heartbeats(sc):
    """Periodically check the status of the leader"""

    check_status()
    sc.enter(HEARTBEAT_FREQUENCY, 1, heartbeats, (sc,))


def init() -> None:
    """Start the leader"""
    update_metadata(LEADER_PORT)
    args = f"python yak/broker.py {LEADER_PORT}".split(" ")
    subprocess.run(
        args,
        universal_newlines=True,
        shell=True,
        creationflags=subprocess.DETACHED_PROCESS,
    )


def main() -> None:

    print(tcolors.ok("Zookeeper has started"))
    init()

    # heartbeats
    s = sched.scheduler(time.time, time.sleep)

    s.enter(HEARTBEAT_FREQUENCY, 1, heartbeats, (s,))
    s.run()


if __name__ == "__main__":

    # Fixes the issue of color not rendering in Windows Powershell/CMD
    import ctypes

    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    try:
        main()
    except KeyboardInterrupt:
        print(tcolors.warning("Stopping zookeeper..."))
