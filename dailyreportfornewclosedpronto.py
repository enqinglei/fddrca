#coding:utf-8
#!/usr/bin/env python

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

PROXY_TYPE_HTTP=3
socks.setdefaultproxy(3,"10.144.1.10",8080)
socket.socket = socks.socksocket


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
    """"
    conn=mysql.connector.connect(host='localhost',user='root',passwd='',port=3306)
    cur=conn.cursor()
    cur.execute('create database if not exists fddrca')
    conn.commit()
    cur.close()
    conn.close()
    """
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

app.config['dbconfig'] = {'host': '127.0.0.1',
                          'user': 'root',
                          'password': '',
                          'database': 'fddrca', }

class UseDatabase:
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
        """Connect to database and create a DB cursor.

        Return the database cursor to the context manager.
        """
        self.conn = mysql.connector.connect(**self.configuration)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Destroy the cursor as well as the connection (after committing).
        """
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        



"""
addr_dict1={}
addr_dict1['yangjinyong']={'tolist':'enqing.lei@nokia-sbell.com','cclist':'enqing.lei@nokia-sbell.com'}


username1=['leienqing','yangjinyong']
"""

#todos=Todo.query.filter_by(SuitableTeam = team,Status='InProgress').order_by(Todo.TaskId.desc()).first()





def _format_addr(s):
    name,addr = parseaddr(s)
    print name
    print addr
    return formataddr((Header(name,'utf-8').encode(),addr.encode("utf-8") if isinstance(addr,unicode) else addr))                            
                            
                            
addr_dict={}
addr_dict['admin']={'tolist':'I_EXT_MBB_GLOBAL_LTE_TDD_RRM_TMT@nokia.com','cclist':''}
addr_dict['chenlong']={'tolist':'loong.chen@nokia-sbell.com','cclist':'zhuofei.chen@nokia-sbell.com,li-daniel.wang@nokia-sbell.com,I_MN_4GRAN_L2HZH_SG3@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['yangjinyong']={'tolist':'jinyong.yang@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG4@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['xiezhen']={'tolist':'jason.xie@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG6@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['hanbing']={'tolist':'frank.han@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG1@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['lanshenghai']={'tolist':'shenghai.lan@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG2@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['liumingjing']={'tolist':'mingjing.liu@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG7@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['lizhongyuan']={'tolist':'zhongyuan.y.li@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG5@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['caizhichao']={'tolist':'zhi_chao.cai@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG8@nokia.com,enqing.lei@nokia-sbell.com'}

teams=['chenlong','xiezhen','yangjinyong','hanbing','lanshenghai','liumingjing','lizhongyuan','caizhichao']

internal_task_dict={}
internal_task_dict['chenlong']={}
internal_task_dict['hanbing']={}
internal_task_dict['lanshenghai']={}
internal_task_dict['lizhongyuan']={}
internal_task_dict['xiezhen']={}
internal_task_dict['caizhichao']={}
internal_task_dict['yangjinyong']={}
internal_task_dict['liumingjing']={}


task_status_dict={}
task_status_dict['chenlong']=[]
task_status_dict['hanbing']=[]
task_status_dict['lanshenghai']=[]
task_status_dict['lizhongyuan']=[]
task_status_dict['xiezhen']=[]
task_status_dict['caizhichao']=[]
task_status_dict['yangjinyong']=[]
task_status_dict['liumingjing']=[]

internal_task_dict1={}
internal_task_dict1['chenlong']={}
internal_task_dict1['hanbing']={}
internal_task_dict1['lanshenghai']={}
internal_task_dict1['lizhongyuan']={}
internal_task_dict1['xiezhen']={}
internal_task_dict1['caizhichao']={}
internal_task_dict1['yangjinyong']={}
internal_task_dict1['liumingjing']={}


task_status_dict1={}
task_status_dict1['chenlong']=[]
task_status_dict1['hanbing']=[]
task_status_dict1['lanshenghai']=[]
task_status_dict1['lizhongyuan']=[]
task_status_dict1['xiezhen']=[]
task_status_dict1['caizhichao']=[]
task_status_dict1['yangjinyong']=[]
task_status_dict1['liumingjing']=[]

start=0

def create_longcycletimerca_report(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename='daily_longcycletimerca_report.html'
    filename=os.path.join(file_dir, new_filename)
    with app.app_context():
        hello = User.query.filter_by(username=username).first()
        todos=TodoLongCycleTimeRCA.query.filter(TodoLongCycleTimeRCA.user_id == hello.id,TodoLongCycleTimeRCA.PRID.in_(task_status_dict[username])).order_by(TodoLongCycleTimeRCA.PRClosedDate.asc()).all()
        count= len (todos)
        with open(filename,'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('daily_longcycletimerca_report.html',user=username,count=count,todos=todos)))
			
def create_rca_report(username):
    
    file_dir = os.path.join(basedir, username)
    
                            
    if not os.path.exists(file_dir):                
        os.makedirs(file_dir)
    new_filename='daily_rca_report.html'
    filename=os.path.join(file_dir, new_filename)
    with app.app_context():
        taskIdlist=task_status_dict[username]                    
        hello = User.query.filter_by(username=username).first()
        todos=Todo.query.filter(Todo.user_id == hello.id,Todo.PRID.in_(task_status_dict[username])).order_by(Todo.PRID.asc()).all()
        count=len(todos)

        indication_messages='Please Complete RCA for these New Closed Prontos'
            
        with open(filename,'w') as f:
            f.write(str(render_template('daily_rca_report.html',user=username,count=count,todos=todos,indication_messages=indication_messages)))

def rcafilepath(username):

    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    filepath = file_dir
                            
                            
    
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'daily_rca_report.html')
    return filename

def longcycletimercafilepath(username):

    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    filepath = file_dir
                            
                            
    
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'daily_longcycletimerca_report.html')
    return filename                            			

def send2user(username):
    from_addr = "leienqing@gmail.com"
    password = 'Azure&123'
    smtp_server = 'smtp.gmail.com' 
    smtp_port = 587

    create_rca_report(username)
    content=''       
    filepath = rcafilepath(username)
    with open(filepath,'rb') as f:
        content = f.read()

    content1=''
    if task_status_dict1[username]:
        create_longcycletimerca_report(username)
        filepath = longcycletimercafilepath(username)
        with open(filepath,'rb') as f:
            content1 = f.read()
        task_status_dict1[username]=[]

    """    
    to_addr = addr_dict[username]['tolist']
    print ("to_addr====%s"%to_addr)
    cc_addr = addr_dict[username]['cclist']
    print ("cc_addr====%s"%cc_addr)
    """
    to_addr = 'enqing.lei@nokia-sbell.com'

    cc_addr = ''
    
    
    msg = MIMEText(content+content1,'html','utf-8')

    msg['From'] = _format_addr(u'New Closed Pronto for FDD RCA <%s>'%from_addr)
    #msg['To'] = _format_addr(u'Need your action for your part<%s>'%to_addr)
    #msg['Cc'] = _format_addr(u'Need you attention and support for your team part<%s>'%cc_addr)
    msg['To'] ='enqing.lei@nokia-sbell.com' 
    msg['Cc'] =''
    msg['Subject'] = Header(u'FDD New Closed PRs Arrived, RCA Action now ---'+ time.strftime("%Y-%m-%d"),'utf-8').encode()
    msg['Date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")


    server = smtplib.SMTP(smtp_server,smtp_port)
    server.set_debuglevel(1)
    server.starttls()
    server.login(from_addr,password)
    server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msg.as_string())
    #server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msg.as_string())
    server.quit()



def update_user_status():
    for username in teams:
        hello = User.query.filter_by(username=username).first()
        if not hello:
            continue

        todos=Todo.query.filter_by(user_id = hello.id).order_by(Todo.PRID.asc()).all()
        print ("username=%s,user_id=%d"%(username,hello.id))
        count= len (todos)    
        if count ==0:
            print 'No New closed PRs'
        else:
            for item in todos:
                if start==0:
                    internal_task_dict[username].setdefault(item.PRID,1)
                else:
                    internal_task_dict[username].setdefault(item.PRID,0)
                print internal_task_dict[username]
                
              
            keys= internal_task_dict[username].keys()
            for k in keys:
                print k
                if internal_task_dict[username][k]==0:
                    internal_task_dict[username][k]=1
                    task_status_dict[username].append(k)
        
        todos=TodoLongCycleTimeRCA.query.filter_by(user_id = hello.id).order_by(TodoLongCycleTimeRCA.PRID.asc()).all()
        count= len(todos)           
        if count ==0:
            print 'No New closed LongCycleTime PRs'
        else:
            for item in todos:
                if start==0:
                    internal_task_dict1[username].setdefault(item.PRID,1)
                else:
                    internal_task_dict1[username].setdefault(item.PRID,0)
                print internal_task_dict1[username]
                
              
            keys= internal_task_dict1[username].keys()
            for k in keys:
                print k
                if internal_task_dict1[username][k]==0:
                    internal_task_dict1[username][k]=1
                    task_status_dict1[username].append(k)
                    
            print internal_task_dict1[username]
            print task_status_dict1[username]
            


def sendmail():
    """
    from_addr = "leienqing@tsinghua.org.cn"
    password = "Forgetting2011"
     
    smtp_server = 'smtp.tsinghua.org.cn' 
    smtp_port = 25
    """
    global start
    global start1
    with app.app_context():
        update_user_status()
        start=1
        start1=1
        for username in teams:
            if task_status_dict[username]:
                send2user(username)                
                task_status_dict[username]=[]
                task_status_dict1[username] = []

def sleeptime(day,hour,min,sec):
    return day*24*3600+hour*3600 + min*60 + sec



def update():

    s1 = '09:38'
    s2 = datetime.now().strftime('%H:%M')
    if s2 == s2:
        print s2
        print 'Action now!'
        sendmail()
        print 'Daily Report Email has been sent to all the stakeholders!!!'
        second = sleeptime(0,0,1,35)
        time.sleep(second)

    
if __name__ == "__main__":

    print 'Daily screening Be ready now!'
    while 1==1:
        update()







    

