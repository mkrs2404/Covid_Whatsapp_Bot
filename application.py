from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from covid_bot import load
from twilio.rest import Client
import logging
import threading
import time
from datetime import datetime
import covid_bot

def f_write(text:str):
    f = open("log.txt", 'a+')
    f.write(str(text)+"\n")

lock = threading.Lock()
FORMAT = '[%(asctime)-15s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.WARNING, filename = 'corona_bot.log', filemode = 'a')
account_sid = 'ACb5059ad22b3814f11c9f836d471864bc'
auth_token = 'c4818f9094f5aed589f1aeec66c9791f'
client = Client(account_sid, auth_token)

application = Flask(__name__)

@application.route('/bot', methods=['POST'])

def bot():
    state_ut_list = {'Andhra Pradesh': 1, 'Arunachal Pradesh': 2, 'Assam': 3, 'Bihar': 4, 'Chhattisgarh': 5, 'Goa': 6, 'Gujarat': 7, 'Haryana': 8, 'Himachal Pradesh': 9, 'Jharkhand': 10, 'Karnataka': 11, 'Kerala': 12, 'Madhya Pradesh': 13, 'Maharashtra': 14, 'Manipur': 15, 'Meghalaya': 16, 'Mizoram': 17, 'Nagaland': 18, 'Odisha': 19, 'Punjab': 20, 'Rajasthan': 21, 'Sikkim': 22, 'Tamil Nadu': 23, 'Telangana': 24, 'Tripura': 25, 'Uttar Pradesh': 26, 'Uttarakhand': 27, 'West Bengal': 28, 'Andaman and Nicobar Islands': 29, 'Chandigarh': 30, 'Dadra and Nagar Haveli': 31, 'Daman and Diu': 32, 'Delhi': 33, 'Jammu and Kashmir': 34, 'Ladakh': 35, 'Lakshadweep': 36, 'Puducherry': 37, 'Total': 38}
    data = covid_bot.corona_bot(0)
    try:
        incoming_msg = request.values.get('Body', '').lower()
        incoming_user = request.values.get('From')
        logging.critical(f"{incoming_user} : {incoming_msg}")
        resp = MessagingResponse()
        msg = resp.message()

        cur_data = data["newData"]

    except Exception as e:
        logging.exception(f"Error in reading the message sent by a user: {e}")

    message = ''
    key_list = list(state_ut_list.keys()) 
    val_list = list(state_ut_list.values())
    try:
        if 'hi' in incoming_msg:
            #sending the list of states
            message = f"*Which State's/UT's data would you like to know?* \n\n"
            for state in state_ut_list:
                message += f"{state_ut_list[state]}. {state} \n\n"
            message += "\n*Type the number.* \n\n_The data shown is not official. It is collected from state press bulletins and official handles and reliable news channels._ "

        elif incoming_msg.isdigit() and int(incoming_msg) in range(1,39):
            state = key_list[val_list.index(int(incoming_msg))]
            if state in cur_data and cur_data[state][0] != '0':
                message = f'*Data for {state}*.\n\nTotal Confirmed cases  = {cur_data[state][0]} \nCured/Discharged/Migrated = {cur_data[state][1]} \nPossible Deaths = {cur_data[state][2]}\nNew cases registered today = {cur_data[state][3]}\n\n_Stay at home. Stay safe._'
            else:
                message = f'No cases currently in {state}.'

        else:
            message = 'Please provide correct input.'
 
        msg.body(message)
    
    except Exception as e:
        logging.exception(f"Some Failure in the  bot Script!! : {e}")
    
    return(str(resp))


def searchUpdates():
    try:
        while(True):
            logging.warning("Thread Running")
            message_body = ''
            bot_data = covid_bot.corona_bot(1)
            change_in_data = bot_data["changed"]
            message = bot_data['message']
            users = set()
            if change_in_data == True and len(message) != 0:
                client_data = client.messages.list()             
                for msg in client_data:
                    if msg.to != 'whatsapp:+14155238886':
                        users.add(msg.to)

                for msg in message:
                    message_body += msg

                for user in users:
                    client.messages.create(body=message_body,from_='whatsapp:+14155238886',to=user)
                    logging.warning(f"Message sent to {user}")
                    time.sleep(1)
                 
                # client.messages.create(body=message_body,from_='whatsapp:+14155238886',to='whatsapp:+917004784338')
                # time.sleep(1)
                logging.warning("All Messages sent to users")
            time.sleep(3600 * 3)
    except Exception as e:
        logging.warning(e)

if __name__ == "__main__":
    search_updates = threading.Thread(target=searchUpdates)
    search_updates.start()
    application.env='production'
    application.run(debug = True, host='0.0.0.0',port='5000',use_reloader=False)
    search_updates.join()
    