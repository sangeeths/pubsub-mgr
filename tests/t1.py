# NOTE: add the top level directory to sys.path
import sys, os
sys.path.append(os.getcwd().replace("tests",""))

#for item in sys.path:
#    print item

from pubsub.manager import EventManager
import cProfile
import string
import random
import importlib
import inspect 

em = EventManager()

#
# NOTE: the following are the event names 
#       **copied** from pubsub/manager.py
#
# WARNING: DO NOT MODIFY THE FOLLOWING LIST
#
__event_type = ['ARPReplyEvent',
                'ARPRequestEvent',
                'AlarmAddEvent',
                'AlarmClearEvent',
                'AlarmRemoveEvent',
                'AlarmTriggerEvent',
                'AlarmUpdateEvent',
                'ChangeOfValueEvent',
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
evt_len = len(__event_type) 



def generate_topic(n):
    topic_list = []
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
    t_len = 5
    for count in range(0, n):
        topic_list.append(''.join(random.choice(char_set) for x in range(t_len)))
    return topic_list


def generate_handler_functions(n):
    filename = "handler_functions.py"
    try:
        h_file = open(filename, 'w')
        file_data = "class handlers: \n"
        h_file.write(file_data) 
        for i in range(0, n):
            file_data  = "\tdef event_handler_%d(self, topic, event, **kwargs):\n" \
                "\t\tprint \"event_handler_%d: [topic=%%s] [event=%%s] args=%%s\" %% (topic, event, kwargs)\n" \
                "\tdef exception_handler_%d(self, e, topic, event, **kwargs):\n" \
                "\t\tprint \"exception_handler_%d: [exception=%%s] [topic=%%s] [event=%%s] args=%%s\" %% (e, topic, event, kwargs)\n" % \
                (i, i, i, i)
            h_file.write(file_data) 
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        h_file.close()


def add_subscriber(n):
    generate_handler_functions(n)
    from handler_functions import handlers
    h = handlers()
    topic_list = generate_topic(n)
    for i in range(0, n):
        eh = getattr(h, "event_handler_%d" % i)
        exh = getattr(h, "exception_handler_%d" % i)
        em.subscribe(topic=topic_list[i], \
                     event=__event_type[i % evt_len], \
                     event_handler=eh, exception_handler=exh)
    em.subscribe(topic='a*', event='*', event_handler=h.event_handler_0, exception_handler=h.exception_handler_0)
    a_list = [x for x in topic_list if x.startswith('a')]
    print "a_list = %s" % a_list
    for topic in a_list:
        for event in __event_type:
            em.publish(topic=topic, event=event)

    em.dump_sub_table()
    em.dump_all_stats()

if __name__ == '__main__':
#    add_subscriber(1000)
    cProfile.run("add_subscriber(1000)")
#    topic = generate_topic(10000)
   # print "Duplicates: ", len(set(topic))
    #print topic


