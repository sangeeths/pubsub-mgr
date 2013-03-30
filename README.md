Topic and Event based Publish/Subscribe Model
=============================================

By [Sangeeth Saravanaraj](https://github.com/sangeeths)

## About

The `Event Manager` provides a centralized hub for `publishing` and `subscribing` to (a combination of) `topics` and `events`. 

## Definitions

 * `Producer` produces an `event` on a particular `topic` by calling `EventManager.publish(topic, event, arguments-to-the-event-handlers)`
 * `Consumer` subscribes to an `event` on a particular `topic` by calling `EventManager.subscribe(topic, event, event_handler, exception_handler)`. When the `event` occurs, the `event_handler` is called (or `exception_handler` whenever an exception occurs!)

## Features
 * `Produces` and `Consumers` are independent (IOW absolutely NO dependency) - The event manager works in a way where the `producer` need not be aware of the existence of the `subscribers` and the `subscribers` need not be aware of the existence of the `producers`. 
 * The communication (`publish` and `subscribe`) includes two components; #1 `topics` (higher level) #2 `events` (lower level). Read further down on `topics` and `events`.
 * Ability to handle higher volumes of subscriptions!
 * Provides logging and debugging at various levels. Ability to print the internal data structures like `subscription table` and `subscription look up table`. 
 * Provides statistics - total number of hits on `topics`, `events`, `event_handler`, `exception_handler` and `subscription record`.
 * No Mixins or multiple inheritance. 
 * Supports (limited) `globbing` on both `topic` and `event`.
 * Easier way to add/remove/modify `events`. 

## What is a `topic`?
The zero coupling between the producer and consumer are achieved by supporting `topics`. A `topic` is a high(er) level category of communication. A `topic` identifies a "publisher" or a "module" that publishes a particular `event`. For example: "class Database" can publish under `topic` "database". But "class MongoDB(Database)" can publish under `topic` "MongoDB". Currently there are no restriction on who can publish on what `topic`. IOW any publisher can publish on any `topic`. The `topic`s are not predefined. They are dynamically created when the publisher publishes for the first time or a subscriber subscriber for the first time (using that `topic`), and the `topics` stays for ever! 

## What is an `event`?
An `event` is an occurrence of a particular predefined incident. For example: `DatabaseStartEvent` and `DatabaseStopEvent` are predefined `events` for starting and stopping any database. An `event` should be published under a particular `topic`. For example: `EventManager.publish(topic="MongoDB", event="DatabaseStartEvent", db_name=self.db_name, db_type=self.db_type, db_username=self.username, db_pwd=self.password)` is an `event` published under `topic="MongoDB"` and should be published in `"class MongoDB(Database)::start()"`. An `event` (during `publish`) can take any number of arguments with it!
 
## What is publish?
```EventManager.publish(topic="", event="", **kwargs)```
Any `publisher`/`producer` calls `publish()` method to publish an `event` on a particular `topic`. Whenever a `publish()` is called, the event manager queries the `subscription (look-up) table` based on `topic` and `events` and get a list of subscribers who has subscribed for that particular `topic` and `event`, and fires their `event_handler()` functions. A publisher can pass any number of supporting arguments for that `event` (and `topic`) to the subscribers event handler functions (`**kwargs`). It is up to the subscribers event handler functions to use them or ignore them. 

## What is Subscribe?
```EventManager.subscribe(topic="", event="", event_handler="", exception_handler="")```
Any `subscriber`/`consumer` calls `subscribe()` to register their subscription for a particular `topic` and `event`. The `subscribe()` (all) parameters takes non None values; `event` could be a predefined `event`; `event`_handler and execption_handler must be callables. Whenever a subscribe is done, the `event` manager creates an entry of this subscription in the subscriber (look-up) table. 

## What is unsubscribe?

```
EventManager.unsubscribe(topic="", event="", event_handler="", exception_handler="")
```
The `unsubscribe()` takes all non None values. When `unsubscribe()` is called, the event manager look up for a subscription record for the given parameters in the subscriber table and removes the entry if present. Else no action is performed. 

```
EventManager.unsubscribe_all(event_handler="")
``` 
A particular `consumer`/`subscriber` may have subscribed to various `topics` and `events` and could have used a single event_handler for all the processing. In this scenario, the `unsubscribe_all()` would come in handy to unsubscribe all the subscription that is made for a particular event handler. 


## What is an event_handler and exception_handler?

The event handler is a function/method in the subscribers scope which is called whenever a particular `topic` and `event` occurred/published. When any exception is encountered while executing event handler, then the exception handlers are called with that exception. Both event and exception handlers must be `callables`. The event handler and exception handler must have the following prototypes:

```
def event_handler(topic, event, **kwargs):
def exception_handler(e, topic, event, **kwargs):
```

## What are the data structures used?

###Subscription record:

A subscription record is a `namedtuple` (`Python collections`) which is created for each and every call to the `subscribe()` method. The subscription record constitutes of four components - topic, `event`, `event_handler` and `execption_handler`. A subscription record looks as follows:

```Subscription(topic='', event='', event_handler=<event-handler-function>, exception_handler=<exception-handler-function>)```


###Subscription table:
A subscription table is a Python List which contains zero or more subscription record (`namedtuple`). `class EventManager::__sub_table` is the subscription table. The `subscribe()` adds subscription record to the subscription table, `publish()` look-up a subscription record from the subscription table and `unsubscribe()` and `unsubscribe_all()` removes one or more subscription record from the subscription table. As the subscription table is a List the worst case look-up time would be `O(n)` and to reduce the look-up time, we need a new data structure which is `subscription look-up table`. 

###Subscription look-up table:
A subscription look-up table is a `Python Dictionary`. The keys are `topic`, `event`, `event_handler` and `exception_handler`. At any point in time, the subscription look-up table will contain only four entries. The value of each and every key is a `defaultdict(list)` [`Python collections`] which contains the index of the subscriber record in the subscription table.

```
EventManager.__sub_lookup_table = {
    "topic" : defaultdict({"topic1":[1,3,10], "topic2":[0,2,7]}),
    "event" : defaultdict({"event1":[1,2,3], "event2":[4,5,6]}),
    "event_handler" : defaultdict({"evhdlr1":[1], "evthdlr2":[2], "evthdlr3":[5,6]}),
    "exception_handler" : defaultdict({"exchdlr1":[1], "exchdlr2":[3], "exchdlr3":[5,7]})
}
```

For example - `"topic" : defaultdict({"topic1":[1,3,10], "topic2":[0,2,7]}),` means the subscription records which are located at `EventManager.__sub_table[1]`, `EventManager.__sub_table[3]` and `EventManager.__sub_table[10]` are subscribed to `topic` "topic1"

This will help us fetch the records quickly i.e. I believe it is `O(log n) < here < O(n)` 
Pending: Mathematical proof for this time complexity!

##How to get the statistics?
###Subscribe:
To get the current state of the subscription table and subscription look-up table, call `EventManager.dump_sub_table()`

###Publish:
To get information on how many times a `topic`, `event`, `event_handler`, `exception_handler` and `subscription record` is called, run `EventManager.dump_all_stats()`

##Globbing
The new event manager supports globbing for `topics` and `events`. The only supported wild-card character (as of now) is `"*"`. The `"*"` can appear at the beginning, middle and end of a `topic` or `event`. The globbing is supported only in the `subscribe()` [actually it does not make any sense to have globbing in `publish()`]. The following are some examples of globbing:

 * `topic="*" and event=*"` : subscribe to all the events from all the `topics`
 * `topic="*" and event="ChangeOfValueEvent"` : subscribe to "ChangeOfValueEvent" event from all the `topics`
 * `topic="*DB" and event="DatabaseStartEvent"` : subscribe to "DatabaseStartEvent" `event` from all `topics` that ends with "DB" which includes `topics` like "MongoDB", "CassandraDB", "OracleDB" etc
 * `topic="Scheduler" and event="*"` : subscribe to all events from the `topic` "Scheduler"

##What has been tested?
Pretty much each and every component has been tested. The stress test is available at `tests/stress_test.py`

##Enhancements/Improvements:
 * Optimize `lookup`; perhaps new data structure to replace `subscription look-up table`
 * Better locking mechanism - do we need lock while `publishing`? `Lock()` vs `Rlock()`
 * Better display format for stats/subscribe-table
 * Should we make this library into a process? 
 * `Serialize` and send event information over the network (basically event is a string with some variable length argument list) - find out tools and packages which supports this! 
 * Globbing: support $, ^, +, etc 

##Logging
```tail -f /tmp/EventManager.log```


__END__
