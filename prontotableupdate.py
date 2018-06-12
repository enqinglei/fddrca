#coding:utf-8
#!/usr/bin/env python
import sys

reload(sys)

sys.setdefaultencoding("utf-8")

from datetime import datetime
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g,send_from_directory,jsonify
from flask_sqlalchemy import SQLAlchemy


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from wtforms import StringField, PasswordField, BooleanField, SubmitField

import mysql.connector

from email.mime.text import MIMEText 
from email.header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.utils import parseaddr,formataddr
import smtplib,time,os

from httplib2 import socks
import socket
"""
PROXY_TYPE_HTTP=3
socks.setdefaultproxy(3,"10.144.1.10",8080)
socket.socket = socks.socksocket
"""

basedir = os.path.abspath(os.path.dirname(__file__))



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost:3306/fddrca?charset=utf8'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'secret_key'
app.config['DEBUG'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id',db.Integer , primary_key=True)
    username = db.Column('username', db.String(20), unique=True , index=True)
    password = db.Column('password' , db.String(250))
    email = db.Column('email',db.String(50),unique=True , index=True)
    registered_on = db.Column('registered_on' , db.DateTime)
    todos = db.relationship('Todo' , backref='user',lazy='select')
    todolongcycletimercas = db.relationship('TodoLongCycleTimeRCA' , backref='user',lazy='select')
    def __init__(self , username ,password , email):
        self.username = username
        self.set_password(password)
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self , password):
        self.password = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password , password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class TodoMember(db.Model):
    __tablename__ = 'teammembers'
    ID = db.Column('ID', db.Integer, primary_key=True)
    emailName = db.Column(db.String(64))
    lineManager = db.Column(db.String(32))

    def __init__(self, ID,emailName,lineManager):
        self.ID = ID
        self.emailName = emailName
        self.lineManager = lineManager
    """    
    conn=mysql.connector.connect(host='localhost',user='root',passwd='',port=3306)
    cur=conn.cursor()
    cur.execute('create database if not exists fddrca')
    conn.commit()
    cur.close()
    conn.close()
    """
db.create_all()

class Todo(db.Model):
    __tablename__ = 'rcastatus'
    PRID = db.Column('PRID', db.String(64), primary_key=True)
    PRTitle = db.Column(db.String(1024))
    PRReportedDate = db.Column(db.String(64))
    PRClosedDate=db.Column(db.String(64))
    PROpenDays=db.Column(db.Integer)
    PRRcaCompleteDate = db.Column(db.String(64))
    PRRelease = db.Column(db.String(128))
    PRAttached = db.Column(db.String(128))
    IsLongCycleTime = db.Column(db.String(32))
    IsCatM = db.Column(db.String(32))
    IsRcaCompleted = db.Column(db.String(32)) 
    NoNeedDoRCAReason = db.Column(db.String(64))
    RootCauseCategory=db.Column(db.String(1024))
    FunctionArea = db.Column(db.String(1024))
    CodeDeficiencyDescription = db.Column(db.String(1024))
    CorrectionDescription=db.Column(db.String(1024))
    RootCause = db.Column(db.String(1024))
    IntroducedBy = db.Column(db.String(128))
    Handler = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, PRID,PRTitle,PRReportedDate,PRClosedDate,PROpenDays,PRRcaCompleteDate,PRRelease,PRAttached,IsLongCycleTime,\
                 IsCatM,IsRcaCompleted,NoNeedDoRCAReason,RootCauseCategory,FunctionArea,CodeDeficiencyDescription,\
		 CorrectionDescription,RootCause,IntroducedBy,Handler):
        self.PRID = PRID
        self.PRTitle = PRTitle
        self.PRReportedDate = PRReportedDate
        self.PRClosedDate = PRClosedDate
        self.PROpenDays = PROpenDays
        self.PRRcaCompleteDate = PRRcaCompleteDate
        self.PRRelease = PRRelease
        self.PRAttached = PRAttached
        self.IsLongCycleTime = IsLongCycleTime
        self.IsCatM = IsCatM
        self.IsRcaCompleted = IsRcaCompleted
        self.NoNeedDoRCAReason = NoNeedDoRCAReason
        self.RootCauseCategory = RootCauseCategory
        self.FunctionArea = FunctionArea
        self.CodeDeficiencyDescription = CodeDeficiencyDescription
        self.CorrectionDescription = CorrectionDescription
        self.RootCause = RootCause        
        self.IntroducedBy = IntroducedBy
        self.Handler = Handler

class TodoLongCycleTimeRCA(db.Model):
    __tablename__ = 'longcycletimercastatus'
    PRID = db.Column('PRID', db.String(64), primary_key=True)
    PRTitle = db.Column(db.String(1024))
    PRReportedDate = db.Column(db.String(64))
    PRClosedDate=db.Column(db.String(64))
    PROpenDays=db.Column(db.Integer)
    PRRcaCompleteDate = db.Column(db.String(64))
    IsLongCycleTime = db.Column(db.String(32))
    IsCatM = db.Column(db.String(32))
    LongCycleTimeRcaIsCompleted = db.Column(db.String(32)) 
    LongCycleTimeRootCause = db.Column(db.String(1024))
    NoNeedDoRCAReason = db.Column(db.String(64))
    Handler = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, PRID,PRTitle,PRReportedDate,PRClosedDate,PROpenDays,PRRcaCompleteDate,IsLongCycleTime,\
                 IsCatM,LongCycleTimeRcaIsCompleted,LongCycleTimeRootCause,NoNeedDoRCAReason,Handler):
        self.PRID = PRID
        self.PRTitle = PRTitle
        self.PRReportedDate = PRReportedDate
        self.PRClosedDate = PRClosedDate
        self.PRRcaCompleteDate = PRRcaCompleteDate
        self.PROpenDays = PROpenDays
        self.IsLongCycleTime = IsLongCycleTime
        self.IsCatM = IsCatM
        self.LongCycleTimeRcaIsCompleted = LongCycleTimeRcaIsCompleted
        self.LongCycleTimeRootCause = LongCycleTimeRootCause
        self.NoNeedDoRCAReason = NoNeedDoRCAReason
        self.Handler = Handler


        
db.create_all()
"""
app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'root',
                          'password': '',
                          'database': 'fddrca', }
						  

mysql://10.68.184.123:8080/jupiter4?autoReconnect=true

Database name: jupiter4, Table names: t_boxi_closed_pronto_daily AND t_boxi_new_pronto_daily

User/pwd: root/jupiter111
"""		  
app.config['dbconfig'] = {'host': '10.68.184.123',
                          'port':8080,
                          'user': 'root',
                          'password': 'jupiter111',
                          'database': 'jupiter4', }						  

class UseDatabase:
    def __init__(self, config):

        self.configuration = config

    def __enter__(self):

        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):

        self.conn.commit()
        self.cursor.close()
        self.conn.close()

class UseDatabaseDict:
    def __init__(self, config):
        """Add the database configuration parameters to the object.

        This class expects a single dictionary argument which needs to assign
        the appropriate values to (at least) the following keys:

            host - the IP address of the host running MySQL/MariaDB.
            user - the MySQL/MariaDB username to use.
            password - the user's password.
            database - the name of the database to use.

        For more options, refer to the mysql-connector-python documentation.
        """
        self.configuration = config

    def __enter__(self):
        """
        Connect to database and create a DB cursor.
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("SELECT * FROM country WHERE Continent = 'Europe'")
        Return the database cursor to the context manager.
        """
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Destroy the cursor as well as the connection (after committing).
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


def compare_time(start_t,end_t):
    s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d'))                        
    #get the seconds for specify date
    e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d'))
    if float(s_time) >= float(e_time):
        return True
    return False 

def comparetime(start_t,end_t):
    s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d'))                        
    #get the seconds for specify date
    e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d'))
    if(float(e_time)- float(s_time)) > float(86400):
        print ("@@@float(e_time)- float(s_time))=%f"%(float(e_time)- float(s_time)))
        return True
    return False 

def leap_year(y):
    if (y % 4 == 0 and y % 100 != 0) or y % 400 == 0:
        return True
    else:
        return False
        
def days_in_month(y, m): 
    if m in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif m in [4, 6, 9, 11]:
        return 30
    else:
        if leap_year(y):
            return 29
        else:
            return 28
            
def days_this_year(year): 
    if leap_year(year):
        return 366
    else:
        return 365
            
def days_passed(year, month, day):
    m = 1
    days = 0
    while m < month:
        days += days_in_month(year, m)
        m += 1
    return days + day

def dateIsBefore(year1, month1, day1, year2, month2, day2):
    """Returns True if year1-month1-day1 is before year2-month2-day2. Otherwise, returns False."""
    if year1 < year2:
        return True
    if year1 == year2:
        if month1 < month2:
            return True
        if month1 == month2:
            return day1 < day2
    return False

def daysBetweenDates(year1, month1, day1, year2, month2, day2):
    if year1 == year2:
        return days_passed(year2, month2, day2) - days_passed(year1, month1, day1)
    else:
        sum1 = 0
        y1 = year1
        while y1 < year2:
            sum1 += days_this_year(y1)
            y1 += 1
        return sum1-days_passed(year1,month1,day1)+days_passed(year2,month2,day2)

"""
    ip_set = [int(i) for i in ip_addr.split('.')]
    ip_number = (ip_set[0] << 24) + (ip_set[1] << 16) + (ip_set[2] << 8) + ip_set[3]
    return ip_number
    ext = fname.rsplit('.', 1)[1]
    
"""
def daysBetweenDate(start,end):
    year1=int(start.split('-',2)[0])
    month1=int(start.split('-',2)[1])
    day1=int(start.split('-',2)[2])

    year2=int(end.split('-',2)[0])
    month2=int(end.split('-',2)[1])
    day2=int(end.split('-',2)[2])
    print ("daysBetweenDates(year1, month1, day1, year2, month2, day2)=%d"%daysBetweenDates(year1, month1, day1, year2, month2, day2))
    return daysBetweenDates(year1, month1, day1, year2, month2, day2)

def insert_item(team,PRID,PRTitle,PRReportedDate,PRClosedDate,PRRelease,PRAttached):
    """
    PRID = internaltask_sheet.cell_value(i+1,2)
    print PRID
    PRTitle = internaltask_sheet.cell_value(i+1,9)
    PRReportedDate = internaltask_sheet.cell_value(i+1,5)    
    PRClosedDate =internaltask_sheet.cell_value(i+1,44)
    PRRelease = internaltask_sheet.cell_value(i+1,6)
    PRAttached = internaltask_sheet.cell_value(i+1,27)
    """
    PROpenDays=daysBetweenDate(PRReportedDate,PRClosedDate)
    PRRcaCompleteDate =''

    if daysBetweenDate(PRReportedDate,PRClosedDate) > 14:
        IsLongCycleTime = 'Yes'
    else:
        IsLongCycleTime = 'No'
    
    IsCatM =''
    IsRcaCompleted='No'
    LongCycleTimeRcaIsCompleted='No'
    NoNeedDoRCAReason =''
    RootCauseCategory = ''
    FunctionArea = ''

    CodeDeficiencyDescription = ''
    CorrectionDescription = ''
    RootCause=''
    LongCycleTimeRootCause=''

    IntroducedBy=''
    Handler = team
    todo_item = Todo.query.get(PRID)
    registered_user = Todo.query.filter_by(PRID=PRID).all()
    if len(registered_user) ==0:
        todo = Todo(PRID,PRTitle,PRReportedDate,PRClosedDate,PROpenDays,PRRcaCompleteDate,PRRelease,PRAttached,IsLongCycleTime,\
                     IsCatM,IsRcaCompleted,NoNeedDoRCAReason,RootCauseCategory,FunctionArea,CodeDeficiencyDescription,\
             CorrectionDescription,RootCause,IntroducedBy,Handler)
            #g.user=Todo.query.get(team)
        #todo.user = g.user
        #print("todo.user = g.user=%s"%todo.user)
        hello = User.query.filter_by(username=team).first()
        todo.user_id=hello.id
        print("todo.user_id=hello.user_id=%s"%hello.id)
        db.session.add(todo)
        db.session.commit()
    else:
        print ("registered_user.PRTitle=%s"%PRID)

    registered_user = TodoLongCycleTimeRCA.query.filter_by(PRID=PRID).all()
    if len(registered_user) ==0 and IsLongCycleTime=='Yes':
        print 'OK#################################################'
        todo = TodoLongCycleTimeRCA(PRID,PRTitle,PRReportedDate,PRClosedDate,PROpenDays,PRRcaCompleteDate,IsLongCycleTime,\
                     IsCatM,LongCycleTimeRcaIsCompleted,LongCycleTimeRootCause,NoNeedDoRCAReason,Handler)

        hello = User.query.filter_by(username=team).first()
        todo.user_id=hello.id
        print("todo.user_id=hello.user_id=%s"%hello.id)
        db.session.add(todo)
        db.session.commit()
    else:
        print ("registered_user.PRTitle=%s"%PRID)


"""
class TodoMember(db.Model):
    __tablename__ = 'teammembers'
    ID = db.Column('ID', db.Integer, primary_key=True)
    emailName = db.Column(db.String(64))
    lineManager = db.Column(db.String(32))

    internal_task_dict[username].setdefault(item.TaskId,0)
"""
   
def update_from_tbox():

    #list=['Ma, Cong 2. (NSB - CN/Hangzhou)']
    teams=['chenlong','xiezhen','yangjinyong','hanbing','lanshenghai','liumingjing','lizhongyuan','caizhichao']
    member_map={}
    memberlist=[]
    with UseDatabaseDict(app.config['dbconfig']) as cursor:
        #_SQL = "select * from t_boxi_closed_pronto_daily where PRGroupIC='LTE_DEVCAHZ_CHZ_UPMACPS'"
        _SQL="SELECT DISTINCT prcls.PRID,prcls.PRTitle, prcls.PRGroupIC, prcls.PRRelease, prcls.PRReportedDate, prcls.PRState, \
                date_format(prcls.ClosedEnter, '%Y-%m-%d') as PRClosedDate,prcls.PRAttached,\
                prnew.RespPerson FROM t_boxi_closed_pronto_daily as prcls LEFT JOIN t_boxi_new_pronto_daily as prnew\
                ON prcls.PRID = prnew.PRID WHERE prcls.PRGroupIC in ('LTE_DEVCAHZ_CHZ_UPMACPS','LTE_DEVPFHZ_CHZ_UPMACPS')\
                 and prcls.PRState='Closed'and prcls.ClosedEnter >='2018-01-01' and prcls.identicalFlag='1' and prcls.isFNR='0'"
        cursor.execute(_SQL)
        contents = cursor.fetchall()
        count=len(contents)
    for linename in teams:
        memberlist = []
        members = TodoMember.query.filter_by(lineManager=linename).all()
        for member in members:
            email=member.emailName
            email=email.encode('utf-8').strip()
            memberlist.append(email)
        member_map.setdefault(linename,memberlist)
        print 'before hello'

        for content in contents:
            PRID = content['PRID'].encode('utf-8').strip()
            todo_item = Todo.query.get(PRID)
            if todo_item:
                continue
            RespPerson = []
            resp= content['RespPerson'].encode('utf-8').strip()
            RespPerson=resp_members(resp)
            #RespPerson.append(resp)
            a=list(set(member_map[linename]).intersection(set(RespPerson)))
            memberline=set(RespPerson)
            retA = [val for val in RespPerson if val in member_map[linename]]
            #RespPerson = set(RespPerson)
            #retA = [i for i in listA if i in listB]
            MemberOfLine= set(member_map[linename])
            s=MemberOfLine.intersection(memberline)
            if MemberOfLine.intersection(memberline):
                print 'hello'
                PRID = content['PRID'].encode('utf-8').strip()
                print PRID
                PRTitle = content['PRTitle'].encode('utf-8').strip()
                PRReportedDate = str(content['PRReportedDate'])
                PRClosedDate = content['PRClosedDate'].encode('utf-8').strip()
                PRRelease = content['PRRelease'].encode('utf-8').strip()
                PRAttached = content['PRAttached'].encode('utf-8').strip()

                insert_item(linename, PRID, PRTitle, PRReportedDate, PRClosedDate, PRRelease, PRAttached)


               
def view_the_pr():
    """Display the contents of the log file as a HTML table."""
    with UseDatabaseDict(app.config['dbconfig']) as cursor:
        _SQL = "select * from t_boxi_closed_pronto_daily where PRGroupIC='LTE_DEVCAHZ_CHZ_UPMACPS'"
        _SQL="SELECT DISTINCT prcls.PRID,prcls.PRTitle, prcls.PRGroupIC, prcls.PRRelease, prcls.PRReportedDate, prcls.PRState, \
                date_format(prcls.ClosedEnter, '%Y-%m-%d') as PRClosedDate,prcls.PRAttached,\
                prnew.RespPerson FROM t_boxi_closed_pronto_daily as prcls LEFT JOIN t_boxi_new_pronto_daily as prnew\
                ON prcls.PRID = prnew.PRID WHERE prcls.PRGroupIC in ('LTE_DEVCAHZ_CHZ_UPMACPS','LTE_DEVPFHZ_CHZ_UPMACPS')\
                 and prcls.PRState='Closed'and prcls.ClosedEnter >='2018-01-01'"
        cursor.execute(_SQL)
        contents = cursor.fetchall() 
        count=len(contents)
        print count 

def test():
     b = 'Ma, Cong 2. (NSB - CN/Hangzhou)'
     s=resp_members(b)
     print s

def resp_members(b):
    members = []
    #b = 'Ma, Cong 2. (NSB - CN/Hangzhou),Ma, Cong 3. (NSB - CN/Hangzhou),'
    a=b.split('),')
    #c=a[0]+')'
    n=len(a)
    if n>1:
        for i in range(n-1):
            c = a[i] + ')'
            members.append(c.encode('utf-8').strip())
        members.append(a[n-1].encode('utf-8').strip())
    else:
        members.append(b.encode('utf-8').strip())
    return members
    print a

def sleeptime(day,hour,min,sec):
    return day*24*3600+hour*3600 + min*60 + sec

counting=0
def update():
    global counting
    s1 = '11:41'
    s2 = datetime.now().strftime('%H:%M')
    if s2 == s2:
        counting=counting+1
        print 'Action now!'
        print counting
        update_from_tbox()
        print 'update completed!!'
        second = sleeptime(0,0,0,10)
        time.sleep(second)
if __name__ == "__main__":

    print 'Update from T-Boxi is Ready now!!!!'
    while 1==1:
        update()



