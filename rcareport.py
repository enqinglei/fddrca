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
from email.mime.image import MIMEImage
from httplib2 import socks
import socket
from selenium import webdriver
from PIL import Image
import urllib2
import urllib
PROXY_TYPE_HTTP=3

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

    # New added field for JIRA deployment
    LteCategory = db.Column(db.String(32))
    CustomerOrInternal = db.Column(db.String(32))
    JiraFunctionArea = db.Column(db.String(32))
    TriggerScenarioCategory = db.Column(db.String(128))
    FirstFaultEcapePhase = db.Column(db.String(32))
    FaultIntroducedRelease = db.Column(db.String(256))
    TechnicalRootCause = db.Column(db.String(1024))
    TeamAssessor = db.Column(db.String(64))
    EdaCause = db.Column(db.String(1024))
    RcaRootCause5WhyAnalysis = db.Column(db.String(2048))
    JiraRcaBeReqested = db.Column(db.String(32))
    JiraIssueStatus = db.Column(db.String(32))
    JiraIssueAssignee = db.Column(db.String(128))
    JiraRcaPreparedQualityRating = db.Column(db.Integer)
    JiraRcaDeliveryOnTimeRating = db.Column(db.Integer)
    RcaSubtaskJiraId = db.Column(db.String(32))
    # End of new added field for JIRA

    rca5whys = db.relationship('Rca5Why' , backref='todo',lazy='select')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, PRID, PRTitle, PRReportedDate, PRClosedDate, PROpenDays, PRRcaCompleteDate, PRRelease,
                 PRAttached, IsLongCycleTime, \
                 IsCatM, IsRcaCompleted, NoNeedDoRCAReason, RootCauseCategory, FunctionArea, CodeDeficiencyDescription, \
                 CorrectionDescription, RootCause, IntroducedBy, Handler, LteCategory, CustomerOrInternal,
                 JiraFunctionArea, TriggerScenarioCategory, \
                 FirstFaultEcapePhase, FaultIntroducedRelease, TechnicalRootCause, TeamAssessor, EdaCause,
                 RcaRootCause5WhyAnalysis, \
                 JiraRcaBeReqested, JiraIssueStatus, JiraIssueAssignee, JiraRcaPreparedQualityRating,
                 JiraRcaDeliveryOnTimeRating, RcaSubtaskJiraId):
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

        # New added for JIRA
        self.LteCategory = LteCategory
        self.CustomerOrInternal = CustomerOrInternal
        self.JiraFunctionArea = JiraFunctionArea
        self.TriggerScenarioCategory = TriggerScenarioCategory
        self.FirstFaultEcapePhase = FirstFaultEcapePhase
        self.FaultIntroducedRelease = FaultIntroducedRelease
        self.TechnicalRootCause = TechnicalRootCause
        self.TeamAssessor = TeamAssessor
        self.EdaCause = EdaCause
        self.RcaRootCause5WhyAnalysis = RcaRootCause5WhyAnalysis
        self.JiraRcaBeReqested = JiraRcaBeReqested
        self.JiraIssueStatus = JiraIssueStatus
        self.JiraIssueAssignee = JiraIssueAssignee
        self.JiraRcaPreparedQualityRating = JiraRcaPreparedQualityRating
        self.JiraRcaDeliveryOnTimeRating = JiraRcaDeliveryOnTimeRating
        self.RcaSubtaskJiraId = RcaSubtaskJiraId
        # End of new added field for JIRA


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

    #New added for JIRA
    InjectionRootCauseEdaCause = db.Column(db.String(1024))
    RcaEdaCauseType = db.Column(db.String(128))
    RcaEdaActionType = db.Column(db.String(32))
    TargetRelease = db.Column(db.String(128))
    CustomerAp = db.Column(db.String(32))
    ApCategory = db.Column(db.String(32)) # RCA/EDA
    ShouldHaveBeenDetected = db.Column(db.String(128))
    ApJiraId = db.Column(db.String(32))  # JIRA ID
    #End of added new field for JIRA

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def __init__(self, APID,PRID,APDescription,APCreatedDate,APDueDate,APCompletedOn,IsApCompleted,APAssingnedTo,QualityOwner,\
                 InjectionRootCauseEdaCause,RcaEdaCauseType,RcaEdaActionType,TargetRelease,CustomerAp,ApCategory,\
                 ShouldHaveBeenDetected,ApJiraId):
        self.APID = APID
        self.PRID = PRID
        self.APDescription = APDescription
        self.APCreatedDate = APCreatedDate
        self.APDueDate = APDueDate
        self.APCompletedOn = APCompletedOn
        self.IsApCompleted = IsApCompleted
        self.APAssingnedTo = APAssingnedTo
        self.QualityOwner = QualityOwner

        # New added field for JIRA
        self.InjectionRootCauseEdaCause = InjectionRootCauseEdaCause
        self.RcaEdaCauseType = RcaEdaCauseType
        self.RcaEdaActionType = RcaEdaActionType
        self.TargetRelease = TargetRelease
        self.CustomerAp = CustomerAp
        self.ApCategory = ApCategory  # RCA/EDA
        self.ShouldHaveBeenDetected = ShouldHaveBeenDetected
        self.ApJiraId = ApJiraId
        #JIRA End

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


def create_ap_report(username):
    file_dir = os.path.join(basedir, username)
    file_dir = os.path.join(file_dir, 'ap')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'ap_report.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        todos = TodoAP.query.filter_by(QualityOwner=username,IsApCompleted='No').all()
        count = len(todos)
        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('ap_report.html', user=username, count=count,todos=todos)))


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
            f.write(str(render_template('rca_report_dashboard.html',titlemessage=username)))


def create_rca_report_dashboard1(username):
    file_dir = os.path.join(basedir, username)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'rca_report_dashboard1.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        hello = User.query.filter_by(username=username).first()
        todos = Todo.query.filter_by(user_id=hello.id, NoNeedDoRCAReason='', IsRcaCompleted='No').order_by(
            Todo.PRClosedDate.asc()).all()
        count = len(todos)

        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report_dashboard1.html', titlemessage='MN 4G L2 R&D HZH')))

def create_ap_report_dashboard(username):
    file_dir = os.path.join(basedir, 'ap')
    file_dir = os.path.join(file_dir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'rca_report_dashboard.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report_dashboard.html', titlemessage='MN 4G L2 R&D HZH')))



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

def apfilepath(username):
    file_dir = os.path.join(basedir, username)
    file_dir = os.path.join(file_dir, 'ap')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath, 'ap_report.html')
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

def rca_dashboard_filepath1(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath, 'rca_report_dashboard1.html')
    return filename

def rca_dashboard_image_filepath(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'1.png')
    return filename

def ap_dashboard_image_filepath(username):
    file_dir = os.path.join(basedir, 'ap')
    file_dir = os.path.join(file_dir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'ap.png')
    return filename
                            
addr_dict={}
addr_dict['chenlong']={'tolist':'loong.chen@nokia-sbell.com','cclist':'zhuofei.chen@nokia-sbell.com,li-daniel.wang@nokia-sbell.com,I_MN_4GRAN_L2HZH_SG3@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['yangjinyong']={'tolist':'jinyong.yang@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG4@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['xiezhen']={'tolist':'jason.xie@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG6@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['zhangyijie']={'tolist':'yijie.zhang@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG1@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['lanshenghai']={'tolist':'shenghai.lan@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG2@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['liumingjing']={'tolist':'mingjing.liu@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG7@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['lizhongyuan']={'tolist':'zhongyuan.y.li@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG5@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['leienqing']={'tolist':'zhi_chao.cai@nokia-sbell.com,jinyong.yang@nokia-sbell.com,loong.chen@nokia-sbell.com,jason.xie@nokia-sbell.com,\
                        yijie.zhang@nokia-sbell.com,mingjing.liu@nokia-sbell.com,jun-julian.hu@nokia-sbell.com,zhongyuan.y.li@nokia-sbell.com,\
                        shenghai.lan@nokia-sbell.com,I_MN_4GRAN_L2HZH_LT@nokia.com','cclist':'zhuofei.chen@nokia-sbell.com,li-daniel.wang@nokia-sbell.com,enqing.lei@nokia-sbell.com'}
addr_dict['caizhichao']={'tolist':'zhi_chao.cai@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_SG8@nokia.com,enqing.lei@nokia-sbell.com'}
addr_dict['hujun']={'tolist':'jun-julian.hu@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_CATM_EFS@nokia.com,bin.7.li@nokia-sbell.com,enqing.lei@nokia-sbell.com'}
addr_dict['wangli']={'tolist':'jun-julian.hu@nokia-sbell.com,yuan_xing.wu@nokia-sbell.com','cclist':'I_MN_4GRAN_L2HZH_ARCH@nokia.com,enqing.lei@nokia-sbell.com'}
username1=['chenlong','yangjinyong','xiezhen','zhangyijie','lanshenghai','liumingjing','lizhongyuan','caizhichao','hujun','wangli']

def sendmail():
    socks.setdefaultproxy(3,"10.144.1.10",8080)
    #socks.setdefaultproxy()
    socket.socket = socks.socksocket
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
            count = len(todos)
            apcount = TodoAP.query.filter_by(QualityOwner=username, IsApCompleted='No', ).count()
            content=''
            if count == 0 and apcount == 0:
                print 'No RCA'
            else:
                create_rca_report(username)
                create_ap_report(username)
                create_rca_report_dashboard(username)
                create_ap_report_dashboard(username)

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

                filepath = apfilepath(username)
                with open(filepath,'rb') as f:
                    content3 = f.read()

                to_addr = addr_dict[username]['tolist']
                print ("to_addr====%s"%to_addr)
                cc_addr = addr_dict[username]['cclist']
                print ("cc_addr====%s"%cc_addr)
                msgRoot = MIMEMultipart('related')
                msgRoot['Subject'] = 'test message'
                msg = MIMEText(content2+content+content1+content3,'html','utf-8')
                msgRoot.attach(msg)
                imagefile= rca_dashboard_image_filepath(username)
                fp = open(imagefile, 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()

                msgImage.add_header('Content-ID', '<image1>')
                msgRoot.attach(msgImage)

                imagefile= ap_dashboard_image_filepath(username)
                fp = open(imagefile, 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                msgImage.add_header('Content-ID', '<image2>')
                msgRoot.attach(msgImage)

                msgRoot['From'] = _format_addr(u'JIRA Customer RCA/EDA and FDD Formal RCA/EDA Tracking<%s>'%from_addr)
                #msg['To'] = _format_addr(u'Need your action for your part<%s>'%to_addr)
                #msg['Cc'] = _format_addr(u'Need you attention and support for your team part<%s>'%cc_addr)
                msgRoot['To'] ='enqing.lei@nokia-sbell.com'
                msgRoot['Cc'] =''
                msgRoot['Subject'] = Header(u'Action now for your part---'+ time.strftime("%Y-%m-%d"),'utf-8').encode()
                msgRoot['Date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")


                server = smtplib.SMTP(smtp_server,smtp_port)
                server.set_debuglevel(1)
                server.starttls()
                server.login(from_addr,password)
                server.sendmail(from_addr,'enqing.lei@nokia-sbell.com',msgRoot.as_string())
                #server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msg.as_string())
                server.quit()

#JIRA code

def create_jira_rca_report(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'jira_rca_report.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        JIRA_STATUS = ['Closed','Resolved']
        #filter(Todo.user_id == hello.id, Todo.TaskId.in_(taskIdlist))
        hello = User.query.filter_by(username=username).first()
        todos = Todo.query.filter_by(user_id=hello.id, JiraRcaBeReqested = 'Yes').order_by(
            Todo.PRClosedDate.asc()).all()
        todos = Todo.query.filter(Todo.user_id == hello.id,\
                Todo.JiraRcaBeReqested == 'Yes',~Todo.JiraIssueStatus.in_(['Closed','Resolved'])).order_by(
            Todo.PRClosedDate.asc()).all()
        count = len(todos)

        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('jira_rca_report.html', user=username, count=count,todos= todos)))


def create_jira_ap_report(username):
    file_dir = os.path.join(basedir, username)
    file_dir = os.path.join(file_dir, 'ap')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'jira_ap_report.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        todos = TodoAP.query.filter_by(QualityOwner=username, IsApCompleted='No').all()
        count = len(todos)
        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('jira_ap_report.html', user=username, count=count, todos=todos)))

def create_jira_rca_report_dashboard(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'jira_rca_report_dashboard.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        hello = User.query.filter_by(username=username).first()
        todos = Todo.query.filter_by(user_id=hello.id, NoNeedDoRCAReason='', IsRcaCompleted='No').order_by(
            Todo.PRClosedDate.asc()).all()
        count = len(todos)

        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('jira_rca_report_dashboard.html', titlemessage=username)))


def create_jira_rca_report_dashboard1(username):
    file_dir = os.path.join(basedir, username)

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'jira_rca_report_dashboard1.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        hello = User.query.filter_by(username=username).first()
        todos = Todo.query.filter_by(user_id=hello.id, NoNeedDoRCAReason='', IsRcaCompleted='No').order_by(
            Todo.PRClosedDate.asc()).all()
        count = len(todos)

        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report_dashboard1.html', titlemessage='MN 4G L2 R&D HZH')))


def create_jira_ap_report_dashboard(username):
    file_dir = os.path.join(basedir, 'ap')
    file_dir = os.path.join(file_dir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    new_filename = 'rca_report_dashboard.html'
    filename = os.path.join(file_dir, new_filename)
    with app.app_context():
        with open(filename, 'w') as f:
            print "file is opened***********************************************************"
            f.write(str(render_template('rca_report_dashboard.html', titlemessage='MN 4G L2 R&D HZH')))


def jira_rcafilepath(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'rca_report.html')
    return filename

def jira_apfilepath(username):
    file_dir = os.path.join(basedir, username)
    file_dir = os.path.join(file_dir, 'ap')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath, 'jira_ap_report.html')
    return filename

def jira_rca_dashboard_filepath(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'jira_rca_report_dashboard.html')
    return filename

def jira_rca_dashboard_filepath1(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath, 'rca_report_dashboard1.html')
    return filename

def jira_rca_dashboard_image_filepath(username):
    file_dir = os.path.join(basedir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'1.png')
    return filename

def jira_ap_dashboard_image_filepath(username):
    file_dir = os.path.join(basedir, 'ap')
    file_dir = os.path.join(file_dir, username)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    filepath = file_dir
    listdirs = os.listdir(filepath)
    listdir = sorted(listdirs)
    filename = os.path.join(filepath,'ap.png')
    return filename

def jira_sendmail():
    socks.setdefaultproxy(3, "10.144.1.10", 8080)
    # socks.setdefaultproxy()
    socket.socket = socks.socksocket
    from_addr = "leienqing@gmail.com"
    password = 'Azure&123'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    with app.app_context():
        for username in username1:
            hello = User.query.filter_by(username=username).first()
            todos = Todo.query.filter_by(user_id=hello.id, JiraRcaBeReqested='Yes').order_by(
                Todo.PRClosedDate.asc()).all()
            print ("username=%s,user_id=%d" % (username, hello.id))
            count = len(todos)
            apcount = TodoAP.query.filter_by(QualityOwner=username, CustomerAp='Yes', ).count()
            content = ''
            if count == 0 and apcount == 0:
                print 'No RCA'
            else:
                create_jira_rca_report(username)
                create_jira_ap_report(username)
                create_jira_rca_report_dashboard(username)
                create_jira_ap_report_dashboard(username)

                filepath = jira_rcafilepath(username)
                with open(filepath, 'rb') as f:
                    content = f.read()

                filepath = jira_rca_dashboard_filepath(username)
                with open(filepath, 'rb') as f:
                    content2 = f.read()

                filepath = jira_apfilepath(username)
                with open(filepath, 'rb') as f:
                    content3 = f.read()

                to_addr = addr_dict[username]['tolist']
                print ("to_addr====%s" % to_addr)
                cc_addr = addr_dict[username]['cclist']
                print ("cc_addr====%s" % cc_addr)
                msgRoot = MIMEMultipart('related')
                msgRoot['Subject'] = 'Customer PR RCA/EDA Report'
                msg = MIMEText(content2 + content + content1 + content3, 'html', 'utf-8')
                msgRoot.attach(msg)
                imagefile = jira_rca_dashboard_image_filepath(username)
                fp = open(imagefile, 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()

                msgImage.add_header('Content-ID', '<image1>')
                msgRoot.attach(msgImage)

                imagefile = jira_ap_dashboard_image_filepath(username)
                fp = open(imagefile, 'rb')
                msgImage = MIMEImage(fp.read())
                fp.close()
                msgImage.add_header('Content-ID', '<image2>')
                msgRoot.attach(msgImage)

                msgRoot['From'] = _format_addr(u'JIRA Customer RCA Tracking<%s>' % from_addr)
                # msg['To'] = _format_addr(u'Need your action for your part<%s>'%to_addr)
                # msg['Cc'] = _format_addr(u'Need you attention and support for your team part<%s>'%cc_addr)
                msgRoot['To'] = 'enqing.lei@nokia-sbell.com'
                msgRoot['Cc'] = ''
                msgRoot['Subject'] = Header(u'Customer Pronto RCA Action reminder ---' + time.strftime("%Y-%m-%d"),
                                            'utf-8').encode()
                msgRoot['Date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")

                server = smtplib.SMTP(smtp_server, smtp_port)
                server.set_debuglevel(1)
                server.starttls()
                server.login(from_addr, password)
                server.sendmail(from_addr, 'enqing.lei@nokia-sbell.com', msgRoot.as_string())
                # server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msg.as_string())
                server.quit()


def sendmail2line():
    socks.setdefaultproxy(3, "10.144.1.10", 8080)
    socket.socket = socks.socksocket
    from_addr = "leienqing@gmail.com"
    password = 'Azure&123'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    with app.app_context():
        username = 'leienqing'
        create_rca_report_dashboard1(username)
        filepath = rca_dashboard_filepath1(username)
        with open(filepath, 'rb') as f:
            content2 = f.read()

        to_addr = addr_dict[username]['tolist']
        print ("to_addr====%s" % to_addr)
        cc_addr = addr_dict[username]['cclist']
        print ("cc_addr====%s" % cc_addr)
        msgRoot = MIMEMultipart('related')
        msg = MIMEText(content2, 'html', 'utf-8')
        msgRoot.attach(msg)
        imagefile = rca_dashboard_image_filepath(username)
        fp = open(imagefile, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)

        imagefile = ap_dashboard_image_filepath(username)
        fp = open(imagefile, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image2>')
        msgRoot.attach(msgImage)
        msgRoot['From'] = _format_addr(u'Weekly Report for JIRA Customer RCA/EDA and FDD Formal RCA/EDA Progress<%s>' % from_addr)
        msgRoot['To'] = to_addr
        msgRoot['Cc'] = cc_addr
        msgRoot['Subject'] = Header(u'Attention for your part ---' + time.strftime("%Y-%m-%d"),
                                    'utf-8').encode()
        msgRoot['Date'] = time.strftime("%a,%d %b %Y %H:%M:%S %z")

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1)
        server.starttls()
        server.login(from_addr, password)
        #server.sendmail(from_addr, 'enqing.lei@nokia-sbell.com', msgRoot.as_string())
        server.sendmail(from_addr,to_addr.split(',')+cc_addr.split(','),msgRoot.as_string())
        server.quit()

def sleeptime(hour,min,sec):
    return hour*3600 + min*60 + sec



def update():

    s1 = '09:30'
    dayOfWeek = datetime.today().weekday()
    today = datetime.today()
    m = calendar.MONDAY
    
    s2 = datetime.now().strftime('%H:%M')
    
    if m == dayOfWeek and s2 == s1: # fisrt start need to synch up.
	
        print s2
        print today
        print 'Action now!'
        screen_shot_by_div()
        ap_screenshot_team()
        sendmail()
        screen_shot_by_div1()
        ap_screenshot()
        sendmail2line()
        second = sleeptime(0,10,0)
        print datetime.now()
        print 'Weekly Report Email has been sent to all the stakeholders!!!'

from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.proxy import Proxy, ProxyType




def screen_shot_by_div():
    socks.setdefaultproxy()
    socket.socket = socks.socksocket
    basedir = os.path.basename(os.path.dirname(__file__))
    print basedir
    driver = webdriver.PhantomJS(executable_path='C:/Python27/phantomjs/bin/phantomjs')
    driver.viewportSize = {'width': 1024, 'height': 800}
    driver.maximize_window()
    #driver.get("http://127.0.0.1:3344/dashboard")
    time.sleep(1)
    for username in username1:
        imagefilename=rca_dashboard_image_filepath(username)
        # driver.find_element_by_id('username').click()
        # driver.find_element_by_id('username').send_keys(username)
        # driver.find_element_by_id('password').click()
        # driver.find_element_by_id('password').send_keys(username)  # 自动敲入密码
        # driver.find_element_by_id('submitlogin').click()  # 点击“登录”按钮
        driver.get("http://127.0.0.1:3344/dashboard/%s"%username)
        time.sleep(1)

        driver.save_screenshot(imagefilename)
        element = driver.find_element_by_id("main2")
        print(element.location)
        print(element.size)
        left = element.location['x']
        top = element.location['y']
        right = element.location['x'] + element.size['width']
        bottom = element.location['y'] + element.size['height']
        im = Image.open(imagefilename)
        im = im.crop((left, top, right, bottom))
        im.save(imagefilename)
        # driver.find_element_by_link_text('Logout').click()
        # driver.get("http://127.0.0.1:3344/dashboard")
    driver.close()

def screen_shot_by_div1():

    socks.setdefaultproxy()
    socket.socket = socks.socksocket
    basedir = os.path.basename(os.path.dirname(__file__))

    driver = webdriver.PhantomJS(executable_path='C:/Python27/phantomjs/bin/phantomjs')

    driver.viewportSize = {'width': 1024, 'height': 800}
    driver.maximize_window()
    #driver.get("http://127.0.0.1:3344/dashboard")
    driver.get("http://127.0.0.1:3344/dashboard/leienqing")
    time.sleep(10)
    username = 'leienqing'
    imagefilename=rca_dashboard_image_filepath(username)
    # driver.find_element_by_id('username').click()
    # driver.find_element_by_id('username').send_keys(username)
    # driver.find_element_by_id('password').click()
    # driver.find_element_by_id('password').send_keys(username)
    # driver.find_element_by_id('submitlogin').click()
    time.sleep(10)
    driver.save_screenshot(imagefilename)
    element = driver.find_element_by_id("main1")
    print(element.location)
    print(element.size)
    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']
    im = Image.open(imagefilename)
    im = im.crop((left, top, right, bottom))
    im.save(imagefilename)
    # driver.find_element_by_link_text('Logout').click()
    driver.close()

def ap_screenshot():

    socks.setdefaultproxy()
    socket.socket = socks.socksocket
    basedir = os.path.basename(os.path.dirname(__file__))

    driver = webdriver.PhantomJS(executable_path='C:/Python27/phantomjs/bin/phantomjs')

    driver.viewportSize = {'width': 1024, 'height': 800}
    driver.maximize_window()
    driver.get("http://127.0.0.1:3344/dashboard")
    time.sleep(1)
    username = 'leienqing'
    imagefilename=ap_dashboard_image_filepath(username)
    driver.find_element_by_id('username').click()
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').click()
    driver.find_element_by_id('password').send_keys(username)
    driver.find_element_by_id('submitlogin').click()
    time.sleep(5)
    driver.save_screenshot(imagefilename)
    element = driver.find_element_by_id("main3")
    print(element.location)
    print(element.size)
    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']
    im = Image.open(imagefilename)
    im = im.crop((left, top, right, bottom))
    im.save(imagefilename)
    driver.find_element_by_link_text('Logout').click()
    driver.close()

def ap_screenshot_team():

    socks.setdefaultproxy()
    socket.socket = socks.socksocket
    basedir = os.path.basename(os.path.dirname(__file__))

    driver = webdriver.PhantomJS(executable_path='C:/Python27/phantomjs/bin/phantomjs')

    driver.viewportSize = {'width': 1024, 'height': 800}
    driver.maximize_window()
    driver.get("http://127.0.0.1:3344/dashboard")
    time.sleep(2)
    for username in username1:
        imagefilename=ap_dashboard_image_filepath(username)
        driver.find_element_by_id('username').click()
        driver.find_element_by_id('username').send_keys(username)
        driver.find_element_by_id('password').click()
        driver.find_element_by_id('password').send_keys(username)
        driver.find_element_by_id('submitlogin').click()
        time.sleep(5)
        driver.save_screenshot(imagefilename)
        element = driver.find_element_by_id("main4")
        left = element.location['x']
        top = element.location['y']
        right = element.location['x'] + element.size['width']
        bottom = element.location['y'] + element.size['height']
        im = Image.open(imagefilename)
        im = im.crop((left, top, right, bottom))
        im.save(imagefilename)
        driver.find_element_by_link_text('Logout').click()
        driver.get("http://127.0.0.1:3344/dashboard")
    driver.close()


if __name__ == "__main__":
    print 'Be Ready now!'
    """
    screen_shot_by_div1()
    ap_screenshot()
    sendmail2line()
    second = sleeptime(0,10,0)
    """
    while 1==1:
        update()

    

