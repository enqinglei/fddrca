#coding:utf-8
#!/usr/bin/env python
import sys

reload(sys)

sys.setdefaultencoding("utf-8")

from datetime import datetime
from flask import Flask,session, request, flash, url_for, redirect, render_template, abort ,g,send_from_directory,jsonify
from flask_sqlalchemy import SQLAlchemy
import calendar

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
    todoaps= db.relationship('TodoAP' , backref='user',lazy='select')
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
    rca5whys = db.relationship('Rca5Why' , backref='todo',lazy='select')
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


class TodoAP(db.Model):
    __tablename__ = 'apstatus'
    APID = db.Column('APID', db.String(64), primary_key=True)
    PRID = db.Column(db.String(64))
    APDescription = db.Column(db.String(1024))
    APCreatedDate = db.Column(db.String(64))
    APDueDate = db.Column(db.String(64))
    APCompletedOn = db.Column(db.String(64))
    IsApCompleted = db.Column(db.String(32))
    APAssingnedTo = db.Column(db.String(128))
    QualityOwner = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, APID,PRID,APDescription,APCreatedDate,APDueDate,APCompletedOn,IsApCompleted,APAssingnedTo,QualityOwner):
        self.APID = APID
        self.PRID = PRID
        self.APDescription = APDescription
        self.APCreatedDate = APCreatedDate
        self.APDueDate = APDueDate
        self.APCompletedOn = APCompletedOn
        self.IsApCompleted = IsApCompleted
        self.APAssingnedTo = APAssingnedTo
        self.QualityOwner = QualityOwner


class Rca5Why(db.Model):
    __tablename__ = 'rca5why'
    id = db.Column('why_id', db.Integer, primary_key=True)
    PRID=db.Column(db.String(64))
    Why1 = db.Column(db.String(1024))
    Why2 = db.Column(db.String(1024))
    Why3=db.Column(db.String(1024))
    Why4 = db.Column(db.String(1024)) 
    Why5 = db.Column(db.String(1024))
    pr_id = db.Column(db.String(64), db.ForeignKey('rcastatus.PRID'))

    def __init__(self, PRID,Why1,Why2,Why3,Why4,Why5):
        self.PRID = PRID
        self.Why1 = Why1
        self.Why2 = Why2
        self.Why3 = Why3
        self.Why4 = Why4
        self.Why5 = Why5

        
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


def create_rca_report(username):
    
    file_dir = os.path.join(basedir, username)
    
                            
    if not os.path.exists(file_dir):
                            
        os.makedirs(file_dir)
    new_filename='rca_report.html'
    filename=os.path.join(file_dir, new_filename)
    with app.app_context():
                            
        hello = User.query.filter_by(username=username).first()
        todos=Todo.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',IsRcaCompleted ='No').order_by(Todo.PRClosedDate.asc()).all()
        count=len(todos)
                            
        with open(filename,'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report.html',user=username,count=count,todos=Todo.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',IsRcaCompleted ='No').order_by(Todo.PRClosedDate.asc()).all())))




def create_longcycletimerca_report(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename='longcycletimerca_report.html'
    filename=os.path.join(file_dir, new_filename)
    with app.app_context():
        hello = User.query.filter_by(username=username).first()
        todos=TodoLongCycleTimeRCA.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',LongCycleTimeRcaIsCompleted ='No').order_by(TodoLongCycleTimeRCA.PRClosedDate.asc()).all()
        count= len (todos)
        with open(filename,'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('longcycletimerca_report.html',user=username,count=count,todos=todos)))

def create_rca_report_dashboard(username):
    
    file_dir = os.path.join(basedir, username)
    
                            
    if not os.path.exists(file_dir):
                            
        os.makedirs(file_dir)
    new_filename='rca_report_dashboard.html'
    filename=os.path.join(file_dir, new_filename)
    with app.app_context():
                            
        hello = User.query.filter_by(username=username).first()
        todos=Todo.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',IsRcaCompleted ='No').order_by(Todo.PRClosedDate.asc()).all()
        count=len(todos)
                            
        with open(filename,'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report_dashboard.html')))





"""
@app.route('/dashboard')
def dashboard():
    #logout_user()
    return render_template('chart_index.html')
"""

def _format_addr(s):
    name,addr = parseaddr(s)
    print name
    print addr
    return formataddr((Header(name,'utf-8').encode(),addr.encode("utf-8") if isinstance(addr,unicode) else addr))                            
                            

def rcafilepath(username):

    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    filepath = file_dir
                            
                            
    
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'rca_report.html')
    return filename

def longcycletimercafilepath(username):

    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    filepath = file_dir
                            
                            
    
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'longcycletimerca_report.html')
    return filename

def rca_dashboard_filepath(username):

    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    filepath = file_dir
                            
                            
    
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'rca_report_dashboard.html')
    return filename
                            
addr_dict={}
addr_dict['chenlong']={'tolist':'loong.chen@nokia-sbell.com','cclist':'zhuofei.chen@nokia-sbell.com,li-daniel.wang@nokia-sbell.com,I_MN_4GRAN_L2HZH_SG3@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['yangjinyong']={'tolist':'jinyong.yang@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG4@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['xiezhen']={'tolist':'jason.xie@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG6@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['hanbing']={'tolist':'frank.han@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG1@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['lanshenghai']={'tolist':'shenghai.lan@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG2@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['liumingjing']={'tolist':'mingjing.liu@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG7@internal.nsn.com,enqing.lei@nokia-sbell.com'}
addr_dict['lizhongyuan']={'tolist':'zhongyuan.y.li@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG5@internal.nsn.com,enqing.lei@nokia-sbell.com'}


addr_dict['leienqing']={'tolist':'enqing.lei@nokia-sbell.com','cclist':''}

username1=['chenlong','yangjinyong','xiezhen','hanbing','lanshenghai','liumingjing','lizhongyuan']

def sendmail():
 
    from_addr = "leienqing@gmail.com"
    password = 'Azure&123'
    smtp_server = 'smtp.gmail.com' 
    smtp_port = 587
    
    """
    from_addr = "leienqing@tsinghua.org.cn"
    password = "Forgetting2011"
     
    smtp_server = 'smtp.tsinghua.org.cn' 
    smtp_port = 25
    """                            
    with app.app_context():  
        for username in username1:
            hello = User.query.filter_by(username=username).first()
            todos=Todo.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',IsRcaCompleted ='No').order_by(Todo.PRClosedDate.asc()).all()
            print ("username=%s,user_id=%d"%(username,hello.id))
            count= len (todos)
            content=''
            if count ==0:
                print 'No RCA'
            else:
                create_rca_report(username)
                
                create_rca_report_dashboard(username)
                
                hello = User.query.filter_by(username=username).first()
                todos=TodoLongCycleTimeRCA.query.filter_by(user_id = hello.id,NoNeedDoRCAReason='',LongCycleTimeRcaIsCompleted ='No').order_by(TodoLongCycleTimeRCA.PRClosedDate.asc()).all()
                count= len(todos)
                content1=''
                if count !=0:
                    create_longcycletimerca_report(username)
                    filepath = longcycletimercafilepath(username)
                    with open(filepath,'rb') as f:
                        content1 = f.read()
                            
                filepath = rcafilepath(username)
                with open(filepath,'rb') as f:
                    content = f.read()

                filepath = rca_dashboard_filepath(username)
                with open(filepath,'rb') as f:
                    content2 = f.read()
                    
                to_addr = addr_dict[username]['tolist']
                print ("to_addr====%s"%to_addr)
                cc_addr = addr_dict[username]['cclist']
                print ("cc_addr====%s"%cc_addr)
                msg = MIMEText(content2+content+content1,'html','utf-8')

                msg['From'] = _format_addr(u'FDD Formal RCA Tracking<%s>'%from_addr)
                #msg['To'] = _format_addr(u'Need your action for your part<%s>'%to_addr)
                #msg['Cc'] = _format_addr(u'Need you attention and support for your team part<%s>'%cc_addr)
                msg['To'] ='enqing.lei@nokia-sbell.com' 
                msg['Cc'] =''
                msg['Subject'] = Header(u'Action now for your part---'+ time.strftime("%Y-%m-%d"),'utf-8').encode()
                msg['Date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")


                server = smtplib.SMTP(smtp_server,smtp_port)
                server.set_debuglevel(1)
                server.starttls()
                server.login(from_addr,password)
                server.sendmail(from_addr,'enqing.lei@nokia-sbell.com',msg.as_string())
                #server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msg.as_string())
                server.quit()

def sleeptime(hour,min,sec):
    return hour*3600 + min*60 + sec



tag=0

def update():
    global tag
    s1 = '10:00'
    s='Monday'
    dayOfWeek = datetime.today().weekday()
    today = datetime.today()
    m = calendar.MONDAY
    print(dayOfWeek)
    s2 = datetime.now().strftime('%H:%M')
    if m == dayOfWeek and s2 == s1 and tag == 0:# fisrt start need to synch up.
        tag=1
        print ("tag=%d" % tag)
        print s2
    if tag == 1:
        print 'Action now!'
        sendmail()
        print 'Weekly Report Email has been sent to all the stakeholders!!!'


if __name__ == "__main__":
    update()
    #time.sleep(second)
    #sendmail()
    """
    #filedir = filepath()
    #second = sleeptime(168,0,0)
    #while 1==1:
        print 'Action now!'
        #time.sleep(second)
        #sendmail()
        print 'Report Email has been sent to all the stakeholders!!!'
        time.sleep(second)
        print 'do action'     
        #sendmail()
    """

    

