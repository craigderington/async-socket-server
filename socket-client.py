#!.env/bin/python
# -*- coding: utf-8 -*-

import socket
import sys
import time
import binascii
import random

# client vars
# host = "demo.owlsite.net"
host = "54.201.193.104"
port = 7180

IMEI_LIST = ["3961389","3961897", "3969986", "3965580", "3965585", "3966754", "3966800", "3967500", "3967487"]
VOLTAGE_LIST = ["321", "365", "375", "385", "390", "395", "400", "405"]
RSSI_LIST = ["-67", "-70", "-58", "-68", "-69", "-71", "-80"]
SENSOR_VALUES_LIST = ["125,10", "100,21.7,3.25", "105,22.8", "101,12,3.35,200.7", "103.2,16.7,3.3"]


def main():
    # create socket
    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket Created: {}'.format(s))

        try:
            remote_ip = socket.gethostbyname(host)

            # Connect to remote server
            s.connect((remote_ip, port))
            print('Socket Connected to {} on IP: {}:{}'.format(host, remote_ip, port))
            
            # Send some data to remote server
            imei = random.choice(IMEI_LIST)
            voltage = random.choice(VOLTAGE_LIST)
            rssi = random.choice(RSSI_LIST)
            sensor_values = random.choice(SENSOR_VALUES_LIST)
            message = "{},0,{},{},{}".format(imei, voltage, rssi, sensor_values).encode("utf-8")
            # test malformed radio tx data
            # message = "3967473,125,10".encode("utf-8")
            try:
                # Send the whole string
                s.sendall(bytes(message))
                print('Message: {} was sent successfully...'.format(message))

                # Close the socket
                s.close()

            except socket.error as err:
                # Send failed
                print('Send failed for {}'.format(str(err)))
                sys.exit()

        except socket.gaierror as err:
            # could not resolve address
            print('Socket Error: {}'.format(str(err)))
            sys.exit()

    except socket.error as err:
        print('The socket returned error {}'.format(str(err)))
        sys.exit()


if __name__ == "__main__":
    for i in range(5):
        time.sleep(0.00005)
        main()
    sys.exit(1)
