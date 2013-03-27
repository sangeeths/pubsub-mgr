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



def generate_topic(n, globbing=False, length=5):
    topic_list = []
    char_set = string.ascii_lowercase + string.ascii_uppercase + string.digits
    for count in range(0, n):
        t = ''.join(random.choice(char_set) for x in range(length))
        if globbing: t = t.replace(random.choice(t), '*')
        topic_list.append(t)
    return topic_list

def generate_event():
    event_list = ['ARP*Event', 'Alarm*Event', 'DHCP*Event', 
                  'PING*Event', 'Packet*Event', 'RARP*Event',
                  'Schedule*Event', 'Service*Event', 'User*Event',
                  'A*', 'D*', 'P*', 'R*', 'S*', 'U*', 'B*', '*Event', '*']
    return event_list
    

file_header = \
"# NOTE: this is automatically generated!\n" \
"#       DO NOT MODIFY!!! \n\n" \
"import logging \n" \
"class handlers: \n"

file_body = \
"\tdef event_handler_%d(self, topic, event, **kwargs):\n" \
"\t\tlogging.info(\"...................................................\")\n" \
"\t\tlogging.info(\"Entering event_handler_%d\")\n" \
"\t\tlogging.info(\"\\t[topic=%%s] [event=%%s]\" %% (topic, event))\n" \
"\t\tlogging.info(\"\\targs=%%s\" %% kwargs)\n" \
"\t\tlogging.info(\"...................................................\")\n" \
"\tdef exception_handler_%d(self, e, topic, event, **kwargs):\n" \
"\t\tlogging.info(\"...................................................\")\n" \
"\t\tlogging.info(\"Entering exception_handler_%d\")\n" \
"\t\tlogging.info(\"\\t[topic=%%s] [event=%%s]\" %% (topic, event))\n" \
"\t\tlogging.info(\"\\targs=%%s\" %% kwargs)\n" \
"\t\tlogging.info(\"\\texception=%%s\" %% e)\n" \
"\t\tlogging.info(\"...................................................\")\n" \

def generate_handler_functions(n):
    filename = "handler_functions.py"
    try:
        h_file = open(filename, 'w')
        h_file.write(file_header) 
        for i in range(0, n):
            h_file.write(file_body % (i, i ,i ,i)) 
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        h_file.close()


# r = regular subscriber
# g = subscribers with globbing for topic and event
def subscribe_and_publish(r, g):
    # generate the event handler functions and 
    # exception handler functions
    generate_handler_functions(r)
    from handler_functions import handlers
    h = handlers()
    
    if r != 0:
        # generate a list of topics
        topic_list = generate_topic(r, length=15)
        for i in range(0, r):
            eh = getattr(h, "event_handler_%d" % i)
            exh = getattr(h, "exception_handler_%d" % i)
            em.subscribe(topic=topic_list[i], \
                         event=__event_type[i % evt_len], \
                         event_handler=eh, exception_handler=exh)

    if g != 0:
        # generate a list of topics
        g_topic_list = generate_topic(g, globbing=True, length=10)
        g_event_list = generate_event()
        for i in range(0, g):
            eh = getattr(h, "event_handler_%d" % i)
            exh = getattr(h, "exception_handler_%d" % i)
            em.subscribe(topic=g_topic_list[i], \
                         event=g_event_list[i % len(g_event_list)], \
                         event_handler=eh, exception_handler=exh)

    # randomly publish
    # 
    # publish all topic that starts with 'a' (with all events)
    pub_list  = [x for x in topic_list if x.startswith('a')]
    pub_list += [x for x in topic_list if x.startswith('A')]
    pub_list += [x for x in topic_list if x.endswith('a')]
    pub_list += [x for x in topic_list if x.endswith('A')]
    for topic in pub_list:
        for event in __event_type:
            em.publish(topic=topic, event=event)

    em.dump_sub_table()
    em.dump_all_stats()


if __name__ == '__main__':
    cProfile.run("subscribe_and_publish(50, 20)")


