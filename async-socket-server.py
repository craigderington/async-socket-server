#!/usr/bin/env python3.4
import sys
import config
import asyncio
import logging
from datetime import datetime, timedelta
from database import db_session
from models import RadioData
from sqlalchemy import exc
from tasks import async_to_gateway

# socker server logging
formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
log_handler = logging.FileHandler("asyncio-socket-server.log")
formatter = logging.Formatter(formatter)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)


class SocketServer(asyncio.Protocol):
    
    def connection_made(self, transport):
        client_name = transport.get_extra_info("peername")
        print("Connection received from {}".format(client_name))
        logger.info("Connection received from {}".format(client_name))
        self.transport = transport

    
    def data_received(self, data):
        """
        Implement a specific decoder for each radio type
        data.decode()
        """
        try:
            # format the radio data for database insert
            reading = format_radio_data(data.decode("utf-8"))
            today = datetime.now()
            if isinstance(reading, dict):
                try:
                    # create a new tx record
                    new_tx = RadioData(
                        imei=reading["imei"],
                        voltage=reading["voltage"],
                        rssi=reading["rssi"],
                        sensorval_1=reading["sensor1"],
                        sensorval_2=reading["sensor2"],
                        sensorval_3=reading["sensor3"],
                        sensorval_4=reading["sensor4"],
                        created_on=today,
                        modified_on=today,
                        sync=0
                    )

                    # commit to database
                    db_session.add(new_tx)
                    db_session.commit()
                    db_session.flush()
                    tx_id = new_tx.id
                    
                    # async to gateway
                    async_to_gateway.delay(tx_id)

                    # log and output to console for debugging
                    print("RadioData: {}".format(str(reading)))
                    logger.info("RadioData: {}".format(str(reading)))

                # catch database error
                except exc.SQLAlchemyError as db_err:
                    logger.critical("{}".format(str(db_err)))
                    print("{}".format(str(db_err)))
            
            # catch malformed radio data and log
            elif isinstance(reading, list):
                logger.warning("TX Data Malformed: {}".format(str(reading)))
                print("TX Data Malformed: {}".format(str(reading)))

            elif isinstance(reading, str):
                logger.warning("HEARBEAT: {}".format(str(reading)))
                print("HEARTBEAT: {}".format(str(reading)))
            
            else:
                logger.warning("Unknown Data TX: {}".format(str(reading)))
                print("Unknown Data TX: {}".format(str(reading)))

        # catch value or type error
        except (ValueError, TypeError) as err:
            logger.warning("{}".format(str(err)))
            print("{}".format(str(err)))

    
    def eof_received(self):
        print("EOF")
        return True

    
    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop this event loop')


def format_radio_data(data):
    """
    Format the transmitted radio data into a dict
    :params: data <string>
    :return reading <dict>
    """
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    values = data.split(",")
    reading = dict()
    if len(values) > 3:
        reading["imei"] = values[0]
        if len(reading["imei"]) <= 10:
            reading["sensor1"] = values[1]
            reading["voltage"] = values[2]
            reading["rssi"] = values[3]
            reading["sensor2"] = 0
            reading["sensor3"] = 0
            reading["sensor4"] = 0
            if len(values) == 5:
                reading["sensor2"] = values[4]
            if len(values) == 6:
                reading["sensor3"] = values[5]
            if len(values) == 7:
                reading["sensor3"] = values[5]
                reading["sensor4"] = values[6]
        else:
            reading = str("Heartbeat Probe received: {}...".format(str(today)))
    else:
        # the tx data is of insufficient length
        reading = list(values)
    
    return reading


def main():
    """
    Asyncio server main loop
    :params HOST, PORT
    :return socket server
    """
    
    try:
        today = datetime.now().strftime("%c")
        loop = asyncio.get_event_loop()
        coro = loop.create_server(SocketServer, config.RECEIVER_HOST, config.RECEIVER_PORT)
        server = loop.run_until_complete(coro)

        logger.info("Starting Socket Server...")
        print("Starting Socket Server...")
        print("Socket Server running on {}".format(server.sockets[0].getsockname()))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Socket Server Exited at {}".format(today))
            sys.exit(1)
        finally:
            server.close()
            loop.close()
    
    except asyncio.TimeoutError as te:
        logger.debug("Asyncio timed out:{}".format(str(te)))


if __name__ == "__main__":
    main()
