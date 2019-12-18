# QASchedule
Schedule for job


QASchedule 是为了做什么的?

![image.png](http://pic.yutiansut.com/Frk8C_HjxTrYzlwT-J0UJMUSOx4h)

很多时候, 我们的策略需要定时去执行一些任务, 比如 定时1小时来进行一次选股, 但是很多时候的策略执行的中间状态并不为人所知.

QASchedule是为了实现一个可视化版本的job flow


本QASchedule移植于 QAUnicorn, 一个内部的定时管理任务


1. 内部定时任务指派
2. long-running job的自动运维和状态汇报
3. 支持QAEventMQ/ QAWebsocket/ QAREST 等多个接入模式



常见场景：

1. 你持有股票，设定一个止损价格， 如果当价格跌破某个价位， 就进行平仓【汇报状态】 【检查周期： tick】

2. 你有一个日内策略， 需要对于一个股票池进行监控， 当A股票发生异常行为时， 产生一个事件【汇报状态】， 并对b股票进行操作【汇报状态】

3. 你有一个选股策略，在每个小时都对全市场进行扫描，选择出股票后进行一系列操作

4. 你有一些待执行的任务， 形成一个rpc服务， 当远程调用的时候自动执行这个流程


希望做成什么:

## 内部的定时任务
这是一种模式, 基于@的


```python
@every(frequence='1hour')
def do_1hour():
    sumbit_event(event_type='x')
@every(frequence='1tick')
def do_every_tick()
@every(frequence='event_driven', routing_key='x')
def do_while_calling()
```
这是另外一种模式, 基于on_xxx

```python
class xxx(QAStrategy):
    def on_bar():
        pass
```

## 外部的定时任务

基于celery beat, 实现心跳检查和一些定时的运维活动

提供可视化界面和http接口




## 状态汇报协议：


```json
{
    "source": "jobxxx",
    "filepath": "xxxx",
    "name" : "xxx",
    "status": "xxxx",
    "confirm": false,
    "context": "xxxx"
}
```

## 动态进程创建/指派

基于http的动态进程创建
post: http://ip:port/job/new?content=xxx

会自动在开启此服务的服务器的缓存位置: ~/.quantaxis/cache中创建一个随机uuid.py文件

然后动态运行



## 使用QASchedule以后

QAEventMQ会产生一个新的exchange: QAEventTopic

此Exchange为topic模式, 需要使用QAPUBSUB.consumer.subscriber_topic来订阅

routing_key 

- "#"  为监听所有事件
- "*.event " 监听所有event事件
- "1min.#" 监听所有1min事件
- "5min.#" 监听所有5min事件
- "15min.#" 监听所有15min事件

直接调试: 

```
qaps_sub --model topic --exchange QAEventTopic --routing_key "#"
```