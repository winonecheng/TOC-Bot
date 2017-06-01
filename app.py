import sys
from io import BytesIO

import telegram
import sqlite3 as sql
from flask import Flask, request, url_for, render_template, send_file
from fsm import TocMachine
from local import *

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'shutdown',
        'shutdown_date',
        'violation',
        'violation_club',
        'authenticate',
        'authenticate_club'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'shutdown',
            'conditions': 'is_going_to_shutdown'
        },
        {
            'trigger': 'advance',
            'source': 'shutdown',
            'dest': 'shutdown_date',
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'violation',
            'conditions': 'is_going_to_violation'
        },
        {
            'trigger': 'advance',
            'source': 'violation',
            'dest': 'violation_club',
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'authenticate',
            'conditions': 'is_going_to_authenticate'
        },
        {
            'trigger': 'advance',
            'source': 'authenticate',
            'dest': 'authenticate_club',
        },        
        {
            'trigger': 'go_back',
            'source': [
                'shutdown_date',
                'violation_club',
                'authenticate_club'
            ],
            'dest': 'user'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/show-clubs')
def show_clubs():
    con = sql.connect(DATABASE_PATH)
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from clubs")
   
    clubs = cur.fetchall(); 
    return render_template("show_clubs.html",clubs = clubs)

@app.route('/hook', methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    machine.advance(update)
    return 'ok'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='fsm.png', mimetype='image/png')

@app.route('/send-msg')
def send_msg():
    con = sql.connect(DATABASE_PATH)
    con.row_factory = sql.Row
   
    cur = con.cursor()
    cur.execute("select * from clubs")
   
    clubs = cur.fetchall(); 
    return render_template("send_msg.html",clubs = clubs)

@app.route('/submit',methods = ['POST', 'GET'])
def submit():
    if request.method == 'POST':
        try:
            msg_to = request.form.getlist('msg_to')
            msg_title = request.form['title']
            msg_content = request.form['content']
            msg_img = request.form['img']

            for uid in msg_to:
                bot.send_message(chat_id=uid,
                                 text="*來自社聯會的最新訊息* \n\n標題\n`{}`\n\n內容```{}```".format(msg_title, msg_content),
                                 parse_mode=telegram.ParseMode.MARKDOWN)
                bot.send_photo(chat_id=uid, photo=msg_img)
            msg = "Successfully sended msg !"
        except:
            msg = "Error in sending msg !"
        finally:
            return render_template("send_msg_result.html",msg = msg)

if __name__ == "__main__":
    _set_webhook()
    app.run()
