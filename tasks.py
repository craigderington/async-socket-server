# tasks.py
import config
from celery import Celery
from datetime import datetime, timedelta
from models import RadioData
from database import db_session
import requests
import json
import decimal
from sqlalchemy import exc
import logging
from celery.utils.log import get_logger

# create an instance of celery
celery = Celery(__name__,  
                broker=config.CELERY_BROKER_URL,
                backend=config.CELERY_RESULT_BACKEND)

# set up celery logging
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


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """ Celery heartbeat periodic task watcher """
    # periodic task executes every 2 hours (7200)
    sender.add_periodic_task(600.0, get_tx_to_sync, name="Get TXs to Sync")


@celery.task(max_retries=3)
def get_tx_to_sync():
    """
    Generate a list of TX record IDs that have sync equals zero
    :params None
    :return list
    """
    rows = None
    row_count = 0
    try:
        rows = db_session.query(RadioData).filter(
            RadioData.sync == 0
        ).all()

        if rows:
            for record in rows:
                async_to_gateway.delay(record.id)
                row_count += 1
                logger.info("Sending TX ID: {} to sync to gateway.".format(str(record.id)))
        else:
            current_time = datetime.now().strftime("%c")
            logger.info("ALL Records Synced as of: {}".format(current_time))

    except exc.SQLAlchemyError as err:
        logger.critical("Database error: {}".format(str(err)))
    
    # return the count
    return row_count


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
                "receiver_id":"circnimb",
                "data": [{
                    "id": radiodata.id,
                    "mtu_id": radiodata.imei,
                    "kp_receiver":  1,
                    "kp_system": 0,
                    "value_type": 0,
                    "value": radiodata.sensorval_1,
                    "kp_signal_strength": radiodata.rssi,
                    "kp_signal_level_id": 0,
                    "network_id": radiodata.imei,
                    "receiver_time": tx_timestamp
                }]
            }
            
            try:
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
    
    # return radiodata_id to the console
    return radiodata_id
