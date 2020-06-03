from flask import Flask, render_template, request, url_for, abort
import sqlite3
import json
from collections import OrderedDict
from datetime import date
#import models as dbHandler

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
def profile():
    uname = request.args.get('uname')
    return render_template('profile.html',uname=uname)

@app.route('/insertMood',methods=['POST'])
def insertMood():
    print("inserting mood")
    uname = request.form['username']
    mood = int(request.form['mood'])
    datestring = request.form['day']
    ret = getMood(uname, datestring)

    conn = sqlite3.connect('db_response.db')
    cursor = conn.cursor()

    sqlquery = "insert into userdata(username,entryDate,trackerName,value) values ('%s','%s','mood',%d)" % (uname,datestring,mood)
    if (ret == -1):
        cursor.execute(sqlquery)
        conn.commit()
        conn.close()
    else:
        print("Item not inserted, mood already entered for that date")
        return("Uh oh! You already have a mood already entered for that date")
    return ""

#returns overall average mood for the user
@app.route('/getAvgMood',methods=['GET'])
def getAvgMood():
    uname = request.args.get("uname")

    conn = sqlite3.connect('db_response.db')
    cursor = conn.cursor()

    sqlquery = "select avg(value) from userdata where username='%s' and trackerName='mood'" % (uname)
    cursor.execute(sqlquery)
    avgmood = cursor.fetchone()[0]
    conn.close()

    if avgmood is None:
        avgmood = -1
    else:
        avgmood = round(avgmood,2)

    return str(avgmood)

@app.route('/getAvgMonthlyMood',methods=['GET'])
def getAvgMonthlyMood():
    uname = request.args.get("uname")
    months_before = int(request.args.get("monthsbefore")) #0 would be the current month

    print(singleMonthAverageMood(uname, 2))

    averages = OrderedDict()
    for i in range(months_before+1):
        average = float(singleMonthAverageMood(uname, i))
        if (average==-1):
            average=0
        averages.update( {str(i): average} )

    return json.dumps(averages)

#@app.route('/getMood', methods=['GET'])
def getMood(uname, date): #gets mood for a specific date
    print("in python get mood")
    #uname = request.args.get("uname")
    #date = request.args.get("day")
    conn = sqlite3.connect('db_response.db')
    cursor = conn.cursor()
    sqlquery = "select value from userdata where username='%s' and trackerName='mood' and entryDate='%s'" % (uname, date)
    cursor.execute(sqlquery)
    ret = str(cursor.fetchone())
    print(ret)
    if (ret == "None"):
        print("no data already entered")
        return -1
        #ret = "-1"
    return ret


# This is not associated with a route
def singleMonthAverageMood(uname, months_before):
    conn = sqlite3.connect('db_response.db')
    cursor = conn.cursor()


    if(months_before<2):
        endmonthstr = '+%d month' % (1-months_before)
    else:
        endmonthstr = '%d month' % (1-months_before)

    sqlquery = "select avg(value) from userdata where username='%s' and entryDate between DATE('now', 'start of month', '-%d month') and DATE('now', 'start of month', '%s', '-1 day') and trackerName='mood'" % (uname,months_before,endmonthstr)
    cursor.execute(sqlquery)
    avgmood = cursor.fetchone()[0]
    conn.close()

    if avgmood is None:
        avgmood = -1
    else:
        avgmood = round(avgmood,2)

    return str(avgmood)

if __name__ == '__main__':
    app.run(debug=True)
    #TEMPLATE_AUTO_RELOAD = True
