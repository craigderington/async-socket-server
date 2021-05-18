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

# logging
formatter = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(filename="celery-sync.log", format=formatter, level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            try:
                r = requests.request(
                    method,
                    config.PORTAL_SYNC_URL,
                    headers=hdr,
                    params=params,
                    data=json.dumps(radiodata, default=dec_serializer)
                )

                if r.status_code == 200:
                    radiodata.sync = 1
                    db_session.commit()
                    db_session.flush()
                else:
                    message = "Celery Sync API Call Returned Status Code: {}".format(str(r.status_code))
                    logger.warning("{}".format(str(message)))
                
            except requests.HTTPError as http_err:
                logger.critical("{}".format(str(http_err)))
    
    except exc.SQLAlchemyError as db_err:
        logger.critical("{}".format(str(db_err)))
