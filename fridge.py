import paho.mqtt.client as mqtt
import requests
from datetime import datetime
from config import TOKEN, CHAT_ID, ALERT_THRESHOLD, MQTT_BROKER, USER, PASSWORD, TOPIC
from db_handler import db_record
import logging
import string
import random

# logging configuration
logging.basicConfig(filename='fridge.log',
                    format='%(asctime)s '
                           'LOGGER=%(name)s '
                           'MODULE=%(module)s.py '
                           'FUNC=%(funcName)s'
                           ' %(levelname)s '
                           '%(message)s',
                    datefmt='%d-%m-%Y %H:%M:%S',
                    level='INFO',
                    encoding='utf8')

# create logger
logger = logging.getLogger('fridge')

# first init alert flag
ALERT_FLAG = False


def time_date() -> str:
    """Auxiliary function, return formatted date and time (for debug print)"""
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def id_generator() -> str:
    """Auxiliary function, generate unique ID with lower, upper english letters and digits,
    this unique ID is used for mqtt client"""
    letters_digits = string.ascii_letters + string.digits
    s = (random.choice(letters_digits) for _ in range(10))
    id = ''.join(s)
    print(f'id = {id}')
    logger.info(f'New client id = {id}')
    return id


def send_alert(msg: str) -> None:
    """Sends alert message (msg) to telegram chat with CHAT_ID"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    try:
        requests.get(url, timeout=5)
        logger.info('Alert has been sent')
    except Exception as e:
        logger.error(f'Alert sending error {e}')


def file_record(value: bytes) -> None:
    """Record temperature value from MQTT message payload (bytes) to file"""
    data = str(float(value))
    try:
        with open('data', 'w', encoding="utf-8") as f:
            f.write(time_date() + ' ')
            f.write(data)
    except Exception as e:
        logger.error(f'Error writing data to file {e}')


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f'Client is connected, rc={reason_code}')
    logger.info(f'Client is connected, rc={reason_code}')


def on_disconnect(client, userdata, flags, reason_code, properties=None) -> None:
    print(f'Client was disconnected, rc={reason_code}')
    logger.info(f'Client was disconnected, rc={reason_code}')


def on_message(client, userdata, msg: mqtt.MQTTMessage) -> None:
    """handling with MQTT message when in the topic subscribed was published new message"""

    # use global variable ALERT_FLAG
    global ALERT_FLAG

    value = msg.payload
    # write temp to file
    file_record(value)

    # write temperature to database lrb_fridge.db
    try:
        db_record(float(value))
    except Exception as e:
        logging.error(f'Database record error {e}')

    # debug printing
    print(time_date(), float(value), sep=' ')

    # processing alert (alert flag becomes TRUE) when temperature is exceeding alert thershold
    if (float(value) > ALERT_THRESHOLD) and (ALERT_FLAG is not True):
        ALERT_FLAG = True
        send_alert(f'\U0001F198 Превышена температура холодильной камеры ЛРБ: {float(value)} °C')
        logger.info(f'Превышена температура холодильной камеры ЛРБ: {float(value)} °C')

    # set alert to off if temperature is OK (below ALERT_THRESHOLD)
    if float(value) < ALERT_THRESHOLD:
        ALERT_FLAG = False


def connect_and_subsribe() -> None:
    """Connect client to broker and subscribe to topic (simple function to optimize code)"""
    client.connect(MQTT_BROKER, port=1883, keepalive=60, clean_start=True)
    client.subscribe(TOPIC, qos=1)


if __name__ == '__main__':
    # create mqtt client (from class Client in paho-mqtt package)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=f'{id_generator()}',
                         protocol=5,
                         reconnect_on_failure=True)
    # set credentials
    client.username_pw_set(username=USER, password=PASSWORD)

    # enable logger
    client.enable_logger(logger=logger)

    connect_and_subsribe()

    # define actions for events
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # starting client main loop
    while True:
        try:
            rc = client.loop(timeout=1.0)

            if rc != 0:
                client.disconnect()
                connect_and_subsribe()
                print('Client reconnected after error inside the main loop')
                logger.info('Client reconnected after error inside the main loop')

        except KeyboardInterrupt:
            client.disconnect()
            print('Client was interrupted by keyboard')
            logger.info('Client was interrupted by keyboard')
            exit()

        except Exception as e:
            logger.error(f'There was an error during main loop {e}')


# this code below is an old loop before refactoring :
# try:
#     client.loop_forever(timeout=1.0, retry_first_connection=True)
# except KeyboardInterrupt:
#     client.disconnect()
#     print('Subscriber was interrupted by keyboard')
# except Exception as e:
#     print(e)
#     logging.error(f'Loop was interrupted due to a error {e}')
