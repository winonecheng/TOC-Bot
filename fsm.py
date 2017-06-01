from transitions.extensions import GraphMachine
import requests
import sqlite3 as sql
from local import *


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(
            model = self,
            **machine_configs
        )

    def is_going_to_shutdown(self, update):
        text = update.message.text
        return text.lower() == '/shutdown'
    def on_enter_shutdown(self, update):
        print('Entering shutdown')
        update.message.reply_text("Which date?")

    def on_enter_shutdown_date(self, update):
        text = update.message.text
        date_index = -1
        data = requests.get("https://spreadsheets.google.com/feeds/cells/{}/1/public/values?alt=json".format(SHUTDWON_TIME_EXCEL_KEY)).json()
        
        for idx, entry in enumerate(reversed(data['feed']['entry'])):
            if entry['content']['$t'] == text:
                date_index = idx
                break
        reply_text = ""
        if date_index != -1:      
            club = data['feed']['entry'][0-date_index+1]['content']['$t']
            time = data['feed']['entry'][0-date_index]['content']['$t']
            reply_text = text+ "\n"+ "一活閉管時間："+time + "\n" + "負責閉館社團："+club
        else:
            reply_text = "Not Found"

        update.message.reply_text(reply_text)
        self.go_back(update)

    def is_going_to_violation(self, update):
        text = update.message.text
        return text.lower() == '/violation'
    def on_enter_violation(self, update):
        print('Entering violation')
        update.message.reply_text("Which club?")

    def on_enter_violation_club(self, update):
        text = update.message.text
        data = requests.get("https://spreadsheets.google.com/feeds/cells/{}/1/public/values?alt=json".format(VIOLATION_POINTS_EXCEL_KEY)).json()        
        cell = -1
        for idx, entry in enumerate(reversed(data['feed']['entry'])):
            if entry['content']['$t'] == text:
                cell = entry['gs$cell']
                break
        reply_text = ""
        date = ""
        point = ""

        if cell != -1:
            for entry in data['feed']['entry']:
                if int(entry['gs$cell']['row']) == int(cell['row'])+1 and int(entry['gs$cell']['col']) == 1:
                    date = entry['content']['$t']
                if int(entry['gs$cell']['row']) == int(cell['row'])+1 and int(entry['gs$cell']['col']) == int(cell['col']):
                    point = entry['content']['$t']
                    break
            reply_text = text + " 違規記點累計：" + "\n" + point + "\n" + "登記於 " + date
        else:
            reply_text = "Not Found"

        update.message.reply_text(reply_text)
        self.go_back(update)



    def is_going_to_authenticate(self, update):
        text = update.message.text
        return text.lower() == '/authenticate'

    def on_enter_authenticate(self, update):
        update.message.reply_text("Which club are you?")

    def on_enter_authenticate_club(self, update):
        text = update.message.text
        insert_club_into_db(update.message.chat_id, text)
        update.message.reply_text(text + " 已成功認證!")
        self.go_back(update)

def insert_club_into_db(uid, club_name):
    con = sql.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO clubs (uid, club_name) VALUES (?,?)",(uid, club_name))
    con.commit()
    con.close()
    print("insert club "+club_name+" into db!")
