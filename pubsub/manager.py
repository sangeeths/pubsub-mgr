from collections import namedtuple, defaultdict
from enum import Enum
from itertools import chain
from threading import Lock as Lock
import logging
import re
import sys
import os

# configurable logging parameters
# TODO: read from a config file
log_filename = '/tmp/EventManager.log'
log_level = logging.DEBUG
log_format = '[%(asctime)s]: %(levelname)s : %(message)s'
log_stream = sys.stdout

# NOTE: use stream=log_stream to print logs to stdout
# NOTE: use filename=log_filename to print logs to a file
logging.basicConfig(filename=log_filename,  #stream=sys.stdout,  #filename=log_filename
                    level=log_level, format=log_format)


# publish topic and event patterns
# allowed: a-z, A-Z and 0-9 (, and - are not allowed)
# NOTE: globbing is not supported in publish()
#       so the 'topic' and 'event' arguments to publish 
#       must not contain any wild-card characters ('*')
valid_pub_topic_pattern = "^[a-zA-Z0-9]+$"
valid_pub_event_pattern = "^[a-zA-Z0-9]+$"

# subscribe topic and event patterns
# allowed: a-z, A-Z, 0-9 and * (, and - are not allowed)
# NOTE: globbing is supported in subscribe()
#       so the 'topic' and 'event' arguments to subscribe
#       could not contain any wild-card characters ('*')
valid_sub_topic_pattern = "^[a-zA-Z0-9*]+$"
valid_sub_event_pattern = "^[a-zA-Z0-9*]+$"

# min and max length of topic (5, 25)
# for both publish and subscribe
topic_min_len = 5
topic_max_len = 25

# min and max length of event (5, 25)
# for both publish and subscribe
event_min_len = 5
event_max_len = 25

# exception classes
class InvalidEventHandler(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidExceptionHandler(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidTopic(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidEvent(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class InvalidOperation(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# add new exception class here!
# end: exception classes


#
#
#
#
class EventManager():

    # The column that constitutes a subscription record
    __sub_tuple_columns = ['topic', 
                           'event', 
                           'event_handler', 
                           'exception_handler']

    # subscription record
    __sub_tuple = namedtuple('Subscription', __sub_tuple_columns)

    # subscription table
    __sub_table = []
    
    # subscription lookup table
    # NOTE: whenever __sub_table is updated, the __sub_lookup_table 
    #       must also be updated by calling __update_lookup_table()
    # NOTE: manual sync!! (WARNING)
    __sub_lookup_table = {}

    # the Lock() for both __sub_table and __sub_lookup_table
    __sub_table_lock = Lock()

    # statistics
    # total number-of-times a topic has been published
    __stats_topic = {}
    __stats_topic_lock = Lock()

    # total number-of-times an event has been published
    __stats_event = {}
    __stats_event_lock = Lock()

    # total number-of-times an event handler has been fired
    __stats_event_handler = {}
    __stats_event_handler_lock = Lock()

    # total number-of-times an exception handler has been fired
    __stats_exception_handler = {}
    __stats_exception_handler_lock = Lock()

    # total number-of-times a subscription record is fired
    __stats_subscription = {}
    __stats_subscription_lock = Lock()

    # maxlen [25] : '1234567890123456789012345'
    # minlen [5]  : '12345'
    __event_type = ['ARPReplyEvent',
                    'ARPRequestEvent',
                    'AlarmAddEvent',
                    'AlarmClearEvent',
                    'AlarmRemoveEvent',
                    'AlarmTriggerEvent',
                    'AlarmUpdateEvent',
                    'ChangeOfValueEvent',
                    'DatabaseStartEvent',
                    'DatabaseStopEvent',
                    'DHCPAckEvent',
                    'DHCPDeclineEvent',
                    'DHCPDiscoverEvent',
                    'DHCPInformEvent',
                    'DHCPNakEvent',
                    'DHCPOfferEvent',
                    'DHCPReleaseEvent',
                    'DHCPRequestEvent',
                    'PINGReceivedEvent',
                    'PINGSentEvent',
                    'PacketDroppedEvent',
                    'PacketReceivedEvent',
                    'PacketSentEvent',
                    'RARPReplyEvent',
                    'RARPRequestEvent',
                    'ScheduleChangedEvent',
                    'ScheduleCreatedEvent',
                    'ScheduleRemovedEvent',
                    'ServiceReStartEvent',
                    'ServiceStartEvent',
                    'ServiceStopEvent',
                    'UserLoginEvent',
                    'UserLogoutEvent']
    # add a new event here!
    # minlen [5]  : '12345'
    # maxlen [25] : '1234567890123456789012345'

    def __init__(self):
        self.__validate_all_events()
        self.__update_lookup_table()

    def __validate_all_events(self):
        for event in EventManager.__event_type:
            if not self.__valid_pub_event(event):
                raise InvalidEvent("Invalid Event [%s]" % event)
        logging.info("All events validated.. all good!!")

    def __valid_pub_topic_name(self, topic):
        return True if re.match(valid_pub_topic_pattern, topic) else False

    def __valid_sub_topic_name(self, topic):
        return True if re.match(valid_sub_topic_pattern, topic) else False

    def __valid_pub_event_name(self, event):
        return True if re.match(valid_pub_event_pattern, event) else False

    def __valid_sub_event_name(self, event):
        return True if re.match(valid_sub_event_pattern, event) else False

    def __valid_event_len(self, event):
        return True if len(event) >= event_min_len and \
                       len(event) <= event_max_len \
                    else False

    def __valid_topic_len(self, topic):
        return True if len(topic) >= topic_min_len and \
                       len(topic) <= topic_max_len \
                    else False

    def __lookup_event(self, event):
        return True if event in EventManager.__event_type else False

    def __valid_pub_event(self, event):
        return True if event is not None and \
                       self.__valid_pub_event_name(event) and \
                       self.__valid_event_len(event) and \
                       self.__lookup_event(event) \
                    else False

    def __valid_sub_event(self, event):
        if event is None: return False
        if not self.__valid_sub_event_name(event): return False
        globbing = False if event.find('*') == -1 else True
        if globbing: return True
        if not self.__lookup_event(event): return False
        return True
                
    def __valid_pub_topic(self, topic):
        return True if topic is not None and \
                       self.__valid_pub_topic_name(topic) and \
                       self.__valid_topic_len(topic) \
                    else False

    def __valid_sub_topic(self, topic):
        if topic is None: return False
        if not self.__valid_sub_topic_name(topic): return False
        globbing = False if topic.find('*') == -1 else True
        if globbing: return True
        if not self.__valid_topic_len(topic): return False
        return True 

    # TODO: check whether the event_handler
    #       has the following signature
    #   event_handler(topic, event, **kwargs)
    def __valid_event_handler(self, event_handler):
        return True if event_handler is not None and \
                       hasattr(event_handler, "__call__") \
                    else False

    # TODO: check whether the exception_handler
    #       has the following signature
    #   exception_handler(exception, topic, event, **kwargs)
    def __valid_exception_handler(self, exception_handler):
        return True if exception_handler is not None and \
                       hasattr(exception_handler, "__call__") \
                    else False

    def __inc_topic_stats(self, topic):
        EventManager.__stats_topic_lock.acquire()
        try:
            #t = EventManager.__stats_topic
            if topic in EventManager.__stats_topic:
                EventManager.__stats_topic[topic] += 1
            else:
                EventManager.__stats_topic[topic] = 1
            #t[topic] = t[topic]+1 if topic in t else 1
        finally:
            logging.info("topic stats incremented " \
                        "[topic=%s] [count=%d]" % \
                        (topic, EventManager.__stats_topic[topic]))
            EventManager.__stats_topic_lock.release()

    def __inc_event_stats(self, event):
        EventManager.__stats_event_lock.acquire()
        try:
            e = EventManager.__stats_event
            e[event] = e[event]+1 if event in e else 1
        finally:
            logging.info("event stats incremented " \
                        "[event=%s] [count=%d]" % \
                        (event, e[event]))
            EventManager.__stats_event_lock.release()

    def __inc_event_handler_stats(self, event_h):
        EventManager.__stats_event_handler_lock.acquire()
        try:
            eh = EventManager.__stats_event_handler
            eh[event_h] = eh[event_h]+1 if event_h in eh else 1
        finally:
            logging.info("event_handler stats incremented " \
                        "[event_handler=%s] [count=%d]" % \
                        (event_h, eh[event_h]))
            EventManager.__stats_event_handler_lock.release()

    def __inc_exception_handler_stats(self, exec_h):
        EventManager.__stats_exception_handler_lock.acquire()
        try:
            exh = EventManager.__stats_exception_handler
            exh[exec_h] = exh[exec_h]+1 if exec_h in exh else 1
        finally:
            logging.info("exception_handler stats incremented " \
                        "[exception_handler=%s] [count=%d]" % \
                        (exec_h, exh[exec_h]))
            EventManager.__stats_exception_handler_lock.release()

    def __inc_subscription_stats(self, sub):
        EventManager.__stats_subscription_lock.acquire()
        try:
            s = EventManager.__stats_subscription
            s[sub] = s[sub]+1 if sub in s else 1
        finally:
            logging.info("subscription stats incremented " \
                        "[subscription=%s] [count=%d]" % \
                        (sub, s[sub]))
            EventManager.__stats_subscription_lock.release()

    def __draw_line(self, style='-'):
        rows, columns = os.popen('stty size', 'r').read().split()
        return style * int(columns)

    def dump_sub_table(self):
        final_str = "\n"
        final_str +=  self.__draw_line(style='=')
        final_str += "\n"
        final_str += "\t\t\t\t\t\tS U B S C R I P T I O N - T A B L E\n"
        final_str += "\t\t\t\t\t\t-----------------------------------\n"
        final_str += "%-4s %-25s %s \n" % \
                     ('Id', 'Topic', 'Event/Event-/Exception- Handler')
        final_str += "%-4s %-25s %s \n" % \
                     ('--', '-----', '-------------------------------')
        for index, item in enumerate(EventManager.__sub_table):
            final_str += "%-4s %-25s %s\n"\
                         "%-30s %r \n" \
                         "%-30s %r \n" % \
                         (index, item.topic, str(item.event), "",\
                         item.event_handler, "", item.exception_handler)  
            #final_str +=  self.__draw_line(style='.')
            final_str += "\n"
        final_str += "\t\t\t\t\tS U B S C R I P T I O N   L O O K U P   T A B L E\n"
        final_str += "\t\t\t\t\t-------------------------------------------------\n"
        for item in EventManager.__sub_tuple_columns:
            final_str +=  "%s \n" % item
            for k, v in EventManager.__sub_lookup_table[item].items():
                if item == 'topic':
                    final_str +=  "\t%s : %s \n" % (k, v)
                if item == 'event':
                    final_str +=  "\t%s : %s \n" % (k, v)
                if item == 'event_handler' or item == 'exception_handler':
                    final_str +=  "\t%s : %s \n" % (k, v)
        final_str +=  self.__draw_line(style='=')
        final_str += "\n"
        logging.info(final_str)

    def __dump_topic_stats(self):
        final_str = "\n"
        final_str += "T O P I C (stats)\n"
        final_str += "-----------------\n"
        for topic, count in EventManager.__stats_topic.items():
            final_str += "%7d : %s \n" % (count, topic)
        final_str += "\n"
        logging.info(final_str)

    def __dump_event_stats(self):
        final_str = "\n"
        final_str += "E V E N T (stats)\n"
        final_str += "-----------------\n"
        for event, count in EventManager.__stats_event.items():
            final_str += "%7d : %s \n" % (count, event)
        final_str += "\n"
        logging.info(final_str)

    def __dump_event_handler_stats(self):
        final_str = "\n"
        final_str += "E V E N T  H A N D L E R (stats)\n"
        final_str += "--------------------------------\n"
        for event_handler, count in EventManager.__stats_event_handler.items():
            final_str += "%7d : %s \n" % (count, event_handler)
        final_str += "\n"
        logging.info(final_str)

    def __dump_exception_handler_stats(self):
        final_str = "\n"
        final_str += "E X C E P T I O N  H A N D L E R (stats)\n"
        final_str += "----------------------------------------\n"
        for exception_handler, count in \
            EventManager.__stats_exception_handler.items():
            final_str += "%7d : %s \n" % (count, exception_handler)
        final_str += "\n"
        logging.info(final_str)

    def __dump_subscription_stats(self):
        final_str = "\n"
        final_str += "S U B S C R I P T I O N\n"
        final_str += "-----------------------\n"
        for subscription, count in EventManager.__stats_subscription.items():
            final_str += "%7d : %s \n" % (count, subscription)
        final_str += "\n"
        logging.info(final_str)

    def dump_all_stats(self):
        self.__dump_topic_stats()
        self.__dump_event_stats()
        self.__dump_event_handler_stats()
        self.__dump_exception_handler_stats()
        self.__dump_subscription_stats()

    def publish(self, topic=None, event=None, **kwargs):
        # validate topic and event
        if not self.__valid_pub_topic(topic): 
            raise InvalidTopic("Invalid Topic [%s]" % topic)
        if not self.__valid_pub_event(event): 
            raise InvalidEvent("Invalid Event [%s]" % event)

        # topic_list = index of subscription records in
        #              __sub_table whose topic matches
        #              the published topic.
        # NOTE: including globbing
        topic_list = []
        for entry in EventManager.__sub_lookup_table['topic'].items():
            if re.compile(str(entry[0]).replace('*','.*')).search(topic):
                topic_list.append(entry[1])
        topic_list = list(chain(*topic_list))
        self.__inc_topic_stats(topic)
        logging.debug("publish: topic_list: %s" % topic_list)

        # event_list = index of subscription records in
        #              __sub_table whose events matches
        #              the published event.
        # NOTE: including globbing
        event_list = []
        for entry in EventManager.__sub_lookup_table['event'].items():
            if re.compile(str(entry[0]).replace('*','.*')).search(event):
                event_list.append(entry[1])
        event_list = list(chain(*event_list))
        self.__inc_event_stats(event)
        logging.debug("publish: event_list: %s" % event_list)

        # pub_list = list of (index of) subscription records in
        #            __sub_table whose topic matches the published 
        #            topic and event matches the published event.
        pub_list = list(set(topic_list) & set(event_list))
        logging.debug("publish: pub_list: %s" % pub_list)

        # fire event handlers (or exception handlers)
        # for all the subscribers in the pub_list
        for item in pub_list:
            self.__inc_subscription_stats(EventManager.__sub_table[item])
            try:
                eh = EventManager.__sub_table[item].event_handler
                logging.debug('publish: firing event_handler for ' \
                    '[topic=%s] [event=%s] [event_handler=%r]' % \
                   (EventManager.__sub_table[item].topic, \
                    EventManager.__sub_table[item].event, eh))
                self.__inc_event_handler_stats(eh)
                eh(topic, event, **kwargs)
            except Exception, e:
                try:
                    exh = EventManager.__sub_table[item].exception_handler
                    logging.debug('firing exception_handler for [topic=%s] ' \
                        '[event=%s] [exception_handler=%r] [exception=%s]' % \
                        (EventManager.__sub_table[item].topic, \
                         EventManager.__sub_table[item].event, exh, e))
                    self.__inc_exception_handler_stats(exh)
                    exh(e, topic, event, **kwargs)
                except:
                    logging.exception("Oops!!")
        # publish() : end

    # n-way lookup
    def __sub_lookup(self, **kwargs):
        result = []             # lookup result
        first_iteration = 1     # flag for first iteration
#        logging.debug("......................................................")
        for k, v in kwargs.items():
            if k not in EventManager.__sub_tuple_columns:
                raise NameError('Invalid lookup argument: %s' % k)
            result_so_far = []
            for index in EventManager.__sub_lookup_table[k].get(v, []):
                result_so_far.append(EventManager.__sub_table[index])
            # CAUTION: the first_iteration flag and the below check
            #          is needed. otherwise the & operation on the 
            #          set(result) will always produce null set
            #          because result is initialized to empty list []
            if first_iteration: 
                result = result_so_far
            else: 
                result = list(set(result) & set(result_so_far))
            # after the very first iteration, unset first_iteration!
            if first_iteration: first_iteration = 0
#            logging.debug("key = %s, result           = %s" % (k, result))
#            logging.debug("key = %s, result_so_far    = %s" % (k, result_so_far))
#            logging.debug("======================================================")
        logging.debug("lookup (%s) = %s" %(kwargs, result))
        return result if result else None
    # __sub_look : end

    # manual sync!!
    # NOTE: whenever the __sub_table is updated [subscribe(), 
    #       unsubscribe() and unsubscribe_all() are called], 
    #       this function must be called manually to 
    #       [re-]generate the __sub_lookup_table
    def __update_lookup_table(self):
        # generate the keys for the __sub_lookup_table
        # lookup keys = defaultdict for each column 
        #               in the __sub_tuple_columns
        EventManager.__sub_lookup_table = \
            {field: defaultdict(list) \
            for field in EventManager.__sub_tuple_columns}
        for index, record in enumerate(EventManager.__sub_table):
            for field in EventManager.__sub_tuple_columns:
                value = getattr(record, field)
                EventManager.__sub_lookup_table[field][value].append(index)

    # perform add(append)/remove subscriptions to/from
    # the __sub_table and [re-]generate __sub_lookup_table
    # using the same lock (__sub_table_lock)
    # NOTE: 'op' could hold one of the following values:
    #   'add'    : subscribe
    #   'remove' : unsubscribe, unsubscribe_all
    def __update_sub_table(self, op, *sublist):
        op = op.lower()
        if op != 'add' and op != 'rem':
            logging.error('Invalid Operation [%s]' % op)
            raise InvalidOperation("Invalid Operation [%s] - " \
                                   "Supported Operations: [add]/[rem]" % op)
        EventManager.__sub_table_lock.acquire()
        try:
            for record in sublist:
                if op == 'add': EventManager.__sub_table.append(record)
                else:           EventManager.__sub_table.remove(record)
            # update the __sub_lookup_table as well in the same lock!
            self.__update_lookup_table()
        except:
            logging.error("Unable to %s subscription [%s]" % \
                         ('add' if op == 'add' else 'rem', sublist))
        finally:
            EventManager.__sub_table_lock.release()
    # __update_sub_table : end

    def __subscribe(self, **kwargs):
        if self.__sub_lookup(**kwargs) is None:
            # subscription not exist for the given parameters
            # so create a new subscription record
            record = [EventManager.__sub_tuple(**kwargs)]
            # add subscription record to the __sub_table
            # and [re-]generate __sub_table_lock using 
            # the same lock!!
            self.__update_sub_table('add', *record) 
        else:
            logging.info("Already Subscribed For %s" % kwargs)

    def subscribe(self, topic='*', event='*',
                  event_handler=None, 
                  exception_handler=None):
        # validate the subscribe parameters
        if not self.__valid_sub_topic(topic):
            raise InvalidTopic("Invalid Topic [%s]" % topic)
        if not self.__valid_sub_event(event):
            raise InvalidEvent("Invalid Event [%s]" % event)
        if not self.__valid_event_handler(event_handler):
            raise InvalidEventHandler("Invalid Event Handler [%s]" % \
                                      event_handler)
        if not self.__valid_exception_handler(exception_handler):
            raise InvalidExceptionHandler("Invalid Exception " \
                                          "Handler [%s]" % event)
        # compose dictionary
        keywords = {'topic':topic, 'event':event,
                    'event_handler':event_handler,
                    'exception_handler':exception_handler}
        self.__subscribe(**keywords)
        
    def __unsubscribe(self, **kwargs):
        lookup = self.__sub_lookup(**kwargs)
        if lookup is not None:
            # if subscription record exist for the given 
            # parameters then remove them from __sub_table
            # and [re-]generate __sub_table_lock using 
            # the same lock!!
            self.__update_sub_table('rem', *lookup) 
        else:
            logging.info("Subscription Does NOT Exist for %s" % kwargs)

    def unsubscribe(self, topic='*', event='*',
                    event_handler=None, 
                    exception_handler=None):
        # validate the unsubscribe parameters
        if not self.__valid_sub_topic(topic):
            raise InvalidTopic("Invalid Topic [%s]" % topic)
        if not self.__valid_sub_event(event):
            raise InvalidEvent("Invalid Event [%s]" % event)
        if not self.__valid_event_handler(event_handler):
            raise InvalidEventHandler("Invalid Event Handler [%s]" % \
                                      event_handler)
        if not self.__valid_exception_handler(exception_handler):
            raise InvalidExceptionHandler("Invalid Exception " \
                                          "Handler [%s]" % event)
        # compose dictionary
        keywords = {'topic':topic, 'event':event,
                    'event_handler':event_handler,
                    'exception_handler':exception_handler}
        self.__unsubscribe(**keywords)

    def __unsubscribe_all(self, **kwargs):
        lookup = self.__sub_lookup(**kwargs)
        if lookup is not None:
            # get all the subscription records which calls 
            # the given event_handler and remove them from
            # __sub_table and [re-]generate __sub_lookup_table
            # using the same lock!!
            self.__update_sub_table('rem', *lookup) 
        else:
            logging.info("No subscription exist for %s" % kwargs)

    def unsubscribe_all(self, event_handler=None):
        if not self.__valid_event_handler(event_handler):
            raise InvalidEventHandler("Invalid Event Handler [%s]" % \
                                      event_handler)
        keywords = {'event_handler':event_handler}
        self.__unsubscribe_all(**keywords)
 

if __name__ == '__main__':
    def event_handler(topic, event, **kwargs):
        print "I am an event handler."
        print "     topic = %s" % topic
        print "     event = %s" % event
        print "     args  = %s" % kwargs

    def exception_handler(e, topic, event, **kwargs):
        print "I am an event handler."
        print "     exception = %s" % e
        print "     topic = %s" % topic
        print "     event = %s" % event
        print "     args  = %s" % kwargs

    em = EventManager()
    em.subscribe(topic='*', event='*', 
                 event_handler=event_handler, 
                 exception_handler=exception_handler)
    
    em.publish(topic="randomtopic", event="AlarmUpdateEvent")
    em.publish(topic="topic", event="ServiceStopEvent",
               arg1="argument1", arg2="argument2", arg3="argument3")

    em.dump_sub_table()
    em.dump_all_stats()

# __END__

