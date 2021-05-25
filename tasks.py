# tasks.py
import config
from datetime import datetime, timedelta
from models import RadioData
from database import db_session
import requests
import json
import decimal
from app import celery
from sqlalchemy import exc
import logging
from celery.utils.log import get_logger

# celery logging
formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logger = get_logger(__name__)
logger.setLevel("DEBUG")
log_handler = logging.FileHandler("celery-worker.log")
formatter = logging.Formatter(formatter)
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)



def dec_serializer(o):
    if isinstance(o, decimal.Decimal):
        return float(o)


@celery.task(max_retries=3)
def async_to_gateway(radiodata_id):
    """ Sync the new radio data record to the Portal gateway """
    method = "POST"
    hdr = {"Content-Type": "application/json"}
    params = None

    try:
        radiodata = db_session.query(RadioData).filter(
            RadioData.id == radiodata_id
        ).one()

        if radiodata:
            
            tx_timestamp = radiodata.created_on.strftime("%Y-%m-%d %H:%M:%S")
            
            post_data =  {
                "receiver_id": 'circnimb',
                "data": {
                    "mtu_id": radiodata.imei,
                    "network_id": radiodata.imei,
                    "receiver_time": tx_timestamp,
                    "gateway_time": tx_timestamp,
                    "sensor_value_type": 1,
                    "sensor_value_raw": radiodata.sensorval_1,
                    "voltage": radiodata.voltage,
                    "kp_signal_strength": radiodata.rssi,
                    "receiver_id": "circnimb",
                    "receiver_ip": "0.0.0.0",
                    "sensor_value": radiodata.sensorval_1,
                    "last_sync_date": tx_timestamp
                }
            }
            
            try:
                hdr["Content-Length"] = len(post_data)
                r = requests.request(
                    method,
                    config.PORTAL_SYNC_URL,
                    headers=hdr,
                    params=params,
                    data=json.dumps(post_data, default=dec_serializer)
                )

                if r.status_code == 204:
                    resp = 'DONE'
                    radiodata.sync = 1
                    db_session.commit()
                    db_session.flush()
                    logger.info("API Response: {}".format(str(resp)))
                    logger.info("Radio ID: {} sync flag updated.".format(str(radiodata.imei)))
                elif r.status_code == 400:
                    resp = 'FAILED'
                    logger.info("API Response: {}".format(str(resp)))
                    logger.info("Radio ID: {} sync failed.".format(str(radiodata.imei)))
                else:
                    message = "Celery Sync API Call Returned Status Code: {}".format(str(r.status_code))
                    logger.warning("{}".format(str(message)))
                
            except requests.HTTPError as http_err:
                logger.critical("{}".format(str(http_err)))
    
    except exc.SQLAlchemyError as db_err:
        logger.critical("{}".format(str(db_err)))
