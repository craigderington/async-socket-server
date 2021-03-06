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
            
            data =  {
                "id": radiodata.id,
                "tx_date": tx_timestamp,
                "imei": radiodata.imei,
                "voltage": radiodata.voltage,
                "rssi": radiodata.rssi,
                "sensor1": radiodata.sensorval_1,
                "sensor2": radiodata.sensorval_2,
                "sensor3": radiodata.sensorval_3,
                "sensor4": radiodata.sensorval_4
            }
            
            try:
                r = requests.request(
                    method,
                    config.PORTAL_SYNC_URL,
                    headers=hdr,
                    params=params,
                    data=json.dumps(data, default=dec_serializer)
                )

                if r.status_code == 200:
                    resp = r.json()
                    radiodata.sync = 1
                    db_session.commit()
                    db_session.flush()
                    logger.info("API Response: {}".format(str(resp)))
                    logger.info("Radio ID: {} sync flag updated.".format(str(radiodata.imei)))
                else:
                    message = "Celery Sync API Call Returned Status Code: {}".format(str(r.status_code))
                    logger.warning("{}".format(str(message)))
                
            except requests.HTTPError as http_err:
                logger.critical("{}".format(str(http_err)))
    
    except exc.SQLAlchemyError as db_err:
        logger.critical("{}".format(str(db_err)))
