import json
import requests
import time
import datetime
import logging
import logging.handlers
import threading
from json import JSONDecodeError


lock = threading.Lock()

FILE_NAME = 'corona_data.json'

def f_write(text:str):
    f = open("log.txt", 'a+')
    f.write(str(text)+"\n")

def save(x):
    with open(FILE_NAME, 'w') as f:
        json.dump(x, f)
    
def load():
    res = {}
    with open(FILE_NAME, 'r') as f:
        try:
            res = json.load(f)
        except JSONDecodeError:
            pass
    return res

URL = 'https://api.covid19india.org/data.json'

FORMAT = '[%(asctime)-15s] %(message)s'
log_file = 'corona_bot.log'
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=500*1024,backupCount=5)
logging.basicConfig(format=FORMAT, level=logging.WARNING, handlers = [handler])


def corona_bot(args):  
    cur_data = []
    info = []
    message = []
    any_change = False
    try:
        past_data = load()
        response = requests.get(URL)
        jsonData = response.json()
        state_wise_data = jsonData['statewise']
        info = []
        for state in state_wise_data:
            changed = False
            current_state = state['state']
            cur_data = [state['confirmed'], state['recovered'], state['deaths'], state['deltaconfirmed']]
            
            if current_state not in past_data:
                past_data[current_state] = {}
                changed = True
                any_change = True

            else:
                if past_data[current_state] != cur_data:
                    changed = True
                    any_change = True
                    if past_data[current_state][0] == "0":
                        data = f"*New case/cases appeared in {current_state}*: \n\nConfirmed cases = {state['confirmed']} \nCured/Discharged/Migrated = {state['recovered']}\nPossible Deaths = {state['deaths']}\n\n\n"
                        info.append(data)
                        message.append(data)

                    else:
                        data = f"*Change in data of {current_state}*: \n\nConfirmed cases = {past_data[current_state][0]} --> {state['confirmed']} \nCured/Discharged/Migrated = {past_data[current_state][1]} --> {state['recovered']}\nPossible Deaths = {past_data[current_state][2]} --> {state['deaths']}\nNew cases registered today = {state['deltaconfirmed']}\n\n\n"
                        info.append(data)
                        if current_state == 'Total':
                            message.append(data)

            if changed == True:
                past_data[current_state] = cur_data
                
        bot_data = {"changed": any_change,"message": message, "newData": past_data}

        if any_change == True and args == 1:
            lock.acquire()
            logging.warning("SAVING DATA")
            save(past_data)
            lock.release()

        for event in info:
            logging.critical(event)

    except Exception as e:
        logging.exception(f"Some Failure in the handler Script!! : {e}")

    return bot_data

if __name__ == "__main__":
    corona_bot(1)