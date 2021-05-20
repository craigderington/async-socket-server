#!.env/bin/python
# -*- coding: utf-8 -*-

import socket
import sys
import time
import binascii
import random

# client vars
# host = "demo.owlsite.net"
host = "0.0.0.0"
port = 7182

IMEI_LIST = ["5551190","5551191", "5551192", "5551193", "5551194", "55551195", "5551196", "5551197", "5551198"]
VOLTAGE_LIST = ["321", "365", "375", "385", "390", "395", "400", "405"]
RSSI_LIST = ["-67", "-70", "-58", "-68", "-69", "-71", "-80"]
SENSOR_VALUES_LIST = ["125", "100", "105", "101", "103", "110", "99", "107"]


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
            message = "{},{},{},{}".format(imei, sensor_values, voltage, rssi).encode("utf-8")
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
    for i in range(25):
        time.sleep(0.00005)
        main()
    sys.exit(1)
