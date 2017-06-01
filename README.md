# TOC-Bot

A telegram chatbot for NCKU Clubs Associations.

## Setup

### Install Dependency

```
pip install -r requirements.txt
```

### Create Database (Sqlite3)
```
sqlite3 {{dbname.db}} << schema.sql
```
### Secret Data

Setup the following variables in `local.py`
- `API_TOKEN`
- `WEBHOOK_URL` 
  - https://example.com/hook
- `DATABASE_PATH` 
- `SHUTDWON_TIME_EXCEL_KEY` 
  - the key of Google Sheets
- `VIOLATION_POINTS_EXCEL_KEY`
  - the key of Google Sheets

e.g.  
  
Google Sheets (https://docs.google.com/spreadsheets/d/1j44T9IkLB17Ttw3X1tgd2ua4UGvyAHU65362RjSzj_w/ )  
the key is `1j44T9IkLB17Ttw3X1tgd2ua4UGvyAHU65362RjSzj_w`

### Run the server
```
python3 app.py
```

## Telegram commands
- `/shutdown` : lookup the time of Student Activity Center shuting down
- `/violation` : lookup the violation points of club
- `/authenticate` : authenticate club for accepting the newest information from NCKUCA

## Web
- `https://your-https-URL/` Home Page
- `https://your-https-URL/show-clubs` The table of authenticated clubs in database
- `https://your-https-URL/show-fsm` The graph of Finite State Machine
- `https://your-https-URL/send-msg` Send text or img to the authenticated clubs







