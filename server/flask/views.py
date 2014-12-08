#encoding=utf8
# with app.open_resource('schema.sql') as f:
#     contents = f.read()
#     do_something_with(contents)
#     http://dormousehole.readthedocs.org/en/latest/api.html#application-object

from scrapyc.server.flask.app import flask_app
from flask import render_template
from flask import request
from datetime import datetime

def start_job(project_name,spider_name,task_name,params):
    scheduler = flask_app.config["scheduler_proxy"]
    ret,msg = scheduler.task_start(project_name,spider_name,task_name,params)
    return ret,msg


@flask_app.route('/')
def index():
    return render_template('index.html', flask_app=flask_app)


def str2date(st):
    if not st:
        return None
    spl = st.replace(":"," ").replace("-"," ").split()
    return datetime(*[ int(x) for x in spl])
def str2int(v,default=None):
    v=v.strip()
    if not v:return default
    try:
        return int(v)
    except Exception, e:
        return  default


@flask_app.route('/task_start',methods=['POST', 'GET'])
def task_start():
    try:
        print request.form
        project_name = request.form["project_name"].strip()
        spider_name = request.form["spider_name"].strip()
        task_name = request.form["task_name"].strip()
        spider_params = request.form["spider_params"].strip()
        cron_type = request.form["cron_type"].strip()

        
    except  KeyError, e:
        return e
    params = {}
    for line in  spider_params.split():
        line = line.split("=",1)
        if len(line)  !=2 :
            continue
        params[line[0]] = line[1]

    apscheduler = flask_app.config["apscheduler"]
    if cron_type == "no":
        scheduler = flask_app.config["scheduler_proxy"]
        ret,msg = scheduler.task_start(project_name,spider_name,task_name,params)
        if ret == True:
            return "Success"
        else:
            return msg
    elif cron_type == "interval":
        cron_minute = str2int( request.form["cron_minute"],0)
        cron_hour = str2int(request.form["cron_hour"],0)
        cron_day = str2int(request.form["cron_day"],0)
        cron_month = str2int(request.form["cron_month"],0)
        cron_week = str2int(request.form["cron_week"],0)
        start_date = str2date(request.form["start_date"].strip())
        end_date = str2date(request.form["end_date"].strip())
        job = apscheduler.add_job(
            name=task_name,
            func="scrapyc.server.flask.views:start_job",
            trigger=cron_type,
            kwargs={"project_name":project_name,'spider_name':spider_name,'task_name':task_name,'params':params},
            max_instances=1, replace_existing=True,
            days = cron_day,
            weeks = cron_week,
            hours =cron_hour,
            minutes = cron_minute,
            start_date=start_date,
            end_date =end_date,)
    elif cron_type == "cron":
        cron_minute = request.form["cron_minute"]
        cron_hour = request.form["cron_hour"]
        cron_day = request.form["cron_day"]
        cron_month = request.form["cron_month"]
        cron_week = request.form["cron_week"]
        start_date = str2date(request.form["start_date"].strip())
        end_date = str2date(request.form["end_date"].strip())

        job = apscheduler.add_job(
            name=task_name,
            func="scrapyc.server.flask.views:start_job",
            trigger=cron_type,
            kwargs={"project_name":project_name,'spider_name':spider_name,'task_name':task_name,'params':params},
            max_instances=1, replace_existing=True,
            months = cron_month,
            days = cron_day,
            weeks = cron_week,
            hours =cron_hour,
            minutes = cron_minute,
            start_date=start_date,
            end_date =end_date,)       
    elif cron_type == "date":
         start_date = str2date(request.form["start_date"].strip())
         print "[nimei]",start_date
         job = apscheduler.add_job(
            name=task_name,
            func="scrapyc.server.flask.views:start_job",
            trigger=cron_type,
            kwargs={"project_name":project_name,'spider_name':spider_name,'task_name':task_name,'params':params},
            max_instances=1, replace_existing=True,
            run_date = start_date)
    else:
        return "unkown cron_type:%s"%cron_type
    
    if job:
        return 'success'
    return "failed"

    
@flask_app.route('/task_kill',methods=['POST', 'GET'])
def task_kill():
    task_id = request.args.get('task_id', '')
    if not task_id:
        return {"ok":False,"msg":"no param:task_id"}
    scheduler = flask_app.config["scheduler_proxy"]
    ret,msg = scheduler.task_kill(task_id)
    return {"ok":ret,"msg":msg}


@flask_app.route('/task_stop',methods=['POST', 'GET'])
def task_stop():
    task_id = request.args.get('task_id', '')
    if not task_id:
        return {"ok":False,"msg":"no param:task_id"}
    scheduler = flask_app.config["scheduler_proxy"]
    ret,msg = scheduler.task_stop(task_id)
    return {"ok":ret,"msg":msg}

@flask_app.route('/crontab')
def crontab():

        return render_template('crontab.html', flask_app=flask_app)

@flask_app.route('/new_task')
def new_task():
     return render_template('new_task.html', flask_app=flask_app)

@flask_app.route('/cronjob_modify')
def cronjob_modify():
    return {}

@flask_app.route('/cronjob_pause',methods=['POST'])
def cronjob_pause(): 
    job_id = request.args.get('job_id', '')
    if not job_id:
        return {"ok":False,"msg":"no param:job_id"}    
    apscheduler = flask_app.config["apscheduler"]
    job = apscheduler.get_job(job_id)
    if not job:
        return  {"ok":False,"msg":"job not found.job_id:%s"%job_id}
    apscheduler.pause_job(job)
    return  {"ok":True,"msg":"success"}

@flask_app.route('/cronjob_remove',methods=['POST'])
def cronjob_remove():
    job_id = request.args.get('job_id', '')
    if not job_id:
        return {"ok":False,"msg":"no param:job_id"}    
    apscheduler = flask_app.config["apscheduler"]
    job = apscheduler.get_job(job_id)
    if not job:
        return  {"ok":False,"msg":"job not found.job_id:%s"%job_id}
    apscheduler.pause_job(job)
    return  {"ok":True,"msg":"success"}

@flask_app.route('/cronjob_removeall',methods=['POST'])
def cronjob_removeall():
  
    apscheduler = flask_app.config["apscheduler"]
    apscheduler.remove_all_jobs()
    return  {"ok":True,"msg":"success"}    

