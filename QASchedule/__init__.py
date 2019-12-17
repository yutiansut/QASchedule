# coding:utf-8

import datetime
import json
import os
import shlex
import subprocess
import sys
import threading
import uuid
from datetime import timedelta

import pymongo
from celery import Celery, platforms
from celery.schedules import crontab
from qaenv import (eventmq_amqp, eventmq_ip, eventmq_password, eventmq_port,
                   eventmq_username, mongo_ip, mongo_port)
from QAPUBSUB.consumer import subscriber, subscriber_routing
from QAPUBSUB.producer import publisher, publisher_routing, publisher_topic
platforms.C_FORCE_ROOT = True  # 加上这一行


publisher_R = publisher_topic(host=eventmq_ip, port= eventmq_port, exchange='QAEventTopic')


class celeryconfig():
    broker_url = eventmq_amqp
    RESULT_BACKEND = "rpc://"
    task_default_queue = 'default'
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['application/json']
    task_compression = 'gzip'
    timezone = "Asia/Shanghai"  #时区设置
    result_backend = "rpc://"
    enable_utc = False
    worker_hijack_root_logger = False  #celery默认开启自己的日志，可关闭自定义日志，不关闭自定义日志输出为空
    result_expires = 60 * 60 * 24  #存储结果过期时间（默认1天）

    imports = (
        "QASchedule"
    )
    
    beat_schedule = {
        'interval1': {
            'task': 'QASchedule.min1_event',
            'schedule': crontab(minute='*', hour='*')
        },
        'interval5': {
            'task': 'QASchedule.min5_event',
            'schedule': crontab(minute='*/5', hour='*')
        },
        'interval15': {
            'task': 'QASchedule.min15_event',
            'schedule': crontab(minute='*/15', hour='*')
        },
    }
app = Celery('quantaxis_jobschedule')
app.config_from_object(celeryconfig)


def callback(a, b, c, d, data):
    data = json.loads(data)
    try:
        threading.Thread(do_task(data['cmd'])).start()
    except:
        pass

def node(shell_cmd):
    """run shell
    Arguments:
        shell_cmd {[type]} -- [description]
    Node
    """
    node_id = uuid.uuid4()
    listener = subscriber_routing(host=eventmq_ip, port=eventmq_port, user=eventmq_username, password=eventmq_password,
                                  exchange='qaschedule', routing_key=str(node_id))
    listener.callback = callback
    listener.start()

@app.task(bind=True)
def standard_task(self):
    """这是一个标准的task组件
    用于schedule定时任务
    """
    pass

def do_task(shell_cmd):
    cmd = shlex.split(shell_cmd)
    p = subprocess.Popen(
        cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while p.poll() is None:
        line = p.stdout.readline()
        pass


def submit_task(taskfile):
    pass

@app.task(bind=True)
def min1_event(self):
    print("interval 1min")
    publisher_R.pub(json.dumps({'topic': '1min_event'}), routing_key='1min.event')

@app.task(bind=True)
def min5_event(self):
    print("interval 5min")
    publisher_R.pub(json.dumps({'topic': '5min_event'}), routing_key='5min.event')

@app.task(bind=True)
def min15_event(self):
    print("interval 15min")
    publisher_R.pub(json.dumps({'topic': '15min_event'}), routing_key='15min.event')