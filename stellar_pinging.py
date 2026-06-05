# go through list of discovered nodes and send a HTTPs get HEAD request as a ping

import os
from datetime import datetime
import requests
import json
import concurrent.futures
import urllib3
import threading
import time
import requests
import socket


# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
file_lock = threading.Lock()

default_ports = ['11625']

datadir = '../../data_new/'
dirpath = datadir+'stellar/'

current_datetime = datetime.now()
formatted_datetime = current_datetime.strftime("%Y%m%d %H")
formatted_date = formatted_datetime.split(' ')[0]

# if the main data directories do not exist, create them
if not os.path.exists(dirpath):
    # Create the directory
    os.makedirs(dirpath)
    print(f"Directory '{dirpath}' created.")

save_folder = dirpath+'pinged_peerList/'
if not os.path.exists(save_folder):
    # Create the directory
    os.makedirs(save_folder)
    print(f"Directory '{save_folder}' created.")

def tcp_ping(host, port, timeout=8):
    """
    Attempt to establish a TCP connection to the specified host and port.

    Args:
        host (str): The target hostname or IP address.
        port (int): The target port.
        timeout (int): Timeout in seconds for the connection attempt.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (host,port, True)
    except (socket.timeout, ConnectionRefusedError, socket.error):
        return (host,port,False)


# in-protocol ping for all nodes in parallel
def ping_all(addresses, timeout = 8, max_workers= 200):
    """
    Ping a list of addresses in parallel using TCP
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(tcp_ping, host, port, timeout) for host, port in addresses]
        for future in futures:
            result = future.result()
            if(result[2]):
                results.append(result)
    # create directory and save to file
    f_ping = 'stellar_ping_'+ formatted_datetime+'.json'
    dir = dirpath+'pinged_peerList/'+formatted_date+'/'
    if not os.path.exists(dir):
        # Create the directory
        os.makedirs(dir)
        print(f"Directory '{dir}' created.")
    with open(dir+f_ping, "w") as f:
        for ip,port,bool in sorted(results):
            f.write(f'{ip}:{port}\n')


if __name__ == "__main__":

    # read in the latest crawl data and make list of ip,port with also the default ports
    dir = 'discovered/'
    files = sorted(os.listdir(dirpath+dir))
    nodes = []
    with open(dirpath+dir+files[-1], "r") as f:
        for line in f.readlines():
            nodes.append(tuple(line[:-1].split(':')))

    all_nodes = set(nodes)
    for ip,port in nodes:
        for p in default_ports:
            all_nodes.add((ip,p))
    all_nodes = list(set(all_nodes))
    ping_all(list(all_nodes)) #ping all
