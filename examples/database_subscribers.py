# NOTE: add the top level directory to sys.path
import sys, os
sys.path.append(os.getcwd().replace("examples",""))

#for item in sys.path:
#    print item

from examples.database_publisher import MongoDB, Cassandra, PostgreSQL, Oracle
from pubsub.manager import EventManager
import logging


def print_line():
    logging.info("=" * 80)


def print_args(message, topic, event, e=False, **kwargs):
    print_line()
    logging.info(message)
    if e is not False:
        logging.info("      exception = %s" % e)
    logging.info("      topic     = %s" % topic)
    logging.info("      event     = %s" % event)
    logging.info("      arguments = %s" % kwargs)
    print_line()


##
# Event and Exception handlers for topic='*' and event='*'
#
def All_Database_All_events(topic, event, **kwargs):
    print_args("Entering All_Database_start_event:", topic, event, **kwargs)

def All_Database_All_exceptions(e, topic, event, **kwargs):
    print_args("Entering All_Database_start_exception:", topic, event, e, **kwargs)
#
##

##
# Event and Exception handlers for topic='*' and event='DatabaseStartEvent'
#                                            and event='DatabaseStopEvent'
#
def All_Database_start_event(topic, event, **kwargs):
    print_args("Entering All_Database_start_event:", topic, event, **kwargs)

def All_Database_start_exception(e, topic, event, **kwargs):
    print_args("Entering All_Database_start_exception:", topic, event, e, **kwargs)

def All_Database_stop_event(topic, event, **kwargs):
    print_args("Entering All_Database_stop_event:", topic, event, **kwargs)

def All_Database_stop_exception(e, topic, event, **kwargs):
    print_args("Entering All_Database_stop_exception:", topic, event, e, **kwargs)
#
##

##
# Event and Exception handlers for topic='MongoDB' and event='DatabaseStartEvent'
#                                                  and event='DatabaseStopEvent'
#
def MongoDB_start_event(topic, event, **kwargs):
    print_args("Entering MongoDB_start_event:", topic, event, **kwargs)

def MongoDB_start_exception(e, topic, event, **kwargs):
    print_args("Entering MongoDB_start_exception:", topic, event, e, **kwargs)

def MongoDB_stop_event(topic, event, **kwargs):
    print_args("Entering MongoDB_stop_event:", topic, event, **kwargs)

def MongoDB_stop_exception(e, topic, event, **kwargs):
    print_args("Entering MongoDB_stop_exception:", topic, event, e, **kwargs)
#
##

##
# Event and Exception handlers for topic='Cassandra' and event='DatabaseStartEvent'
#                                                    and event='DatabaseStopEvent'
#
def Cassandra_start_event(topic, event, **kwargs):
    print_args("Entering Cassandra_start_event:", topic, event, **kwargs)

def Cassandra_start_exception(e, topic, event, **kwargs):
    print_args("Entering Cassandra_start_exception:", topic, event, e, **kwargs)

def Cassandra_stop_event(topic, event, **kwargs):
    print_args("Entering Cassandra_stop_event:", topic, event, **kwargs)

def Cassandra_stop_exception(e, topic, event, **kwargs):
    print_args("Entering Cassandra_stop_exception:", topic, event, e, **kwargs)
#
##

##
# Event and Exception handlers for topic='PostgreSQL' and event='DatabaseStartEvent'
#                                                     and event='DatabaseStopEvent'
#
def PostgreSQL_start_event(topic, event, **kwargs):
    print_args("Entering PostgreSQL_start_event:", topic, event, **kwargs)

def PostgreSQL_start_exception(e, topic, event, **kwargs):
    print_args("Entering PostgreSQL_start_exception:", topic, event, e, **kwargs)

def PostgreSQL_stop_event(topic, event, **kwargs):
    print_args("Entering PostgreSQL_stop_event:", topic, event, **kwargs)

def PostgreSQL_stop_exception(e, topic, event, **kwargs):
    print_args("Entering PostgreSQL_stop_exception:", topic, event, e, **kwargs)
#
##

##
# Event and Exception handlers for topic='Oracle' and event='DatabaseStartEvent'
#                                                 and event='DatabaseStopEvent'
#
def Oracle_start_event(topic, event, **kwargs):
    print_args("Entering Oracle_start_event:", topic, event, **kwargs)

def Oracle_start_exception(e, topic, event, **kwargs):
    print_args("Entering Oracle_start_exception:", topic, event, e, **kwargs)

def Oracle_stop_event(topic, event, **kwargs):
    print_args("Entering Oracle_stop_event:", topic, event, **kwargs)

def Oracle_stop_exception(e, topic, event, **kwargs):
    print_args("Entering Oracle_stop_exception:", topic, event, e, **kwargs)
#
##



if __name__ == "__main__":
    em = EventManager()

    #
    #   S U B S C R I P T I O N ' S
    ##

    # Subscribe to all events (i.e. event='*')
    # for all database (i.e. topic='*')
    em.subscribe(topic='*', event='*', 
                 event_handler=All_Database_All_events, 
                 exception_handler=All_Database_All_exceptions)



    # Subscribe to event='DatabaseStartEvent'
    # for all database (i.e. topic='*')
    em.subscribe(topic='*', event='DatabaseStartEvent', 
                 event_handler=All_Database_start_event, 
                 exception_handler=All_Database_start_exception)

    # Subscribe to event='DatabaseStopEvent'
    # for all database (i.e. topic='*')
    em.subscribe(topic='*', event='DatabaseStopEvent', 
                 event_handler=All_Database_stop_event, 
                 exception_handler=All_Database_stop_exception)



    # Subscribe to event='DatabaseStartEvent'
    # for all MongoDB database (i.e. topic='MongoDB')
    em.subscribe(topic='MongoDB', event='DatabaseStartEvent', 
                 event_handler=MongoDB_start_event, 
                 exception_handler=MongoDB_start_exception)

    # Subscribe to event='DatabaseStopEvent'
    # for all MongoDB database (i.e. topic='MongoDB')
    em.subscribe(topic='MongoDB', event='DatabaseStopEvent', 
                 event_handler=MongoDB_stop_event, 
                 exception_handler=MongoDB_stop_exception)



    # Subscribe to event='DatabaseStartEvent'
    # for all cassandra database (i.e. topic='Cassandra')
    em.subscribe(topic='Cassandra', event='DatabaseStartEvent', 
                 event_handler=Cassandra_start_event, 
                 exception_handler=Cassandra_start_exception)

    # Subscribe to event='DatabaseStopEvent'
    # for all cassandra database (i.e. topic='Cassandra')
    em.subscribe(topic='Cassandra', event='DatabaseStopEvent', 
                 event_handler=Cassandra_stop_event, 
                 exception_handler=Cassandra_stop_exception)



    # Subscribe to event='DatabaseStartEvent'
    # for all postgresql database (i.e. topic='PostgreSQL')
    em.subscribe(topic='PostgreSQL', event='DatabaseStartEvent', 
                 event_handler=PostgreSQL_start_event, 
                 exception_handler=PostgreSQL_start_exception)

    # Subscribe to event='DatabaseStopEvent'
    # for all postgresql database (i.e. topic='PostgreSQL')
    em.subscribe(topic='PostgreSQL', event='DatabaseStopEvent', 
                 event_handler=PostgreSQL_stop_event, 
                 exception_handler=PostgreSQL_stop_exception)



    # Subscribe to event='DatabaseStartEvent'
    # for all oracle database (i.e. topic='Oracle')
    em.subscribe(topic='Oracle', event='DatabaseStartEvent', 
                 event_handler=Oracle_start_event, 
                 exception_handler=Oracle_start_exception)

    # Subscribe to event='DatabaseStopEvent'
    # for all oracle database (i.e. topic='Oracle')
    em.subscribe(topic='Oracle', event='DatabaseStopEvent', 
                 event_handler=Oracle_stop_event, 
                 exception_handler=Oracle_stop_exception)


    #
    #   end: S U B S C R I P T I O N ' S
    ##


    mdb = MongoDB("customer_database")
    mdb.start()
    mdb.stop()
    cdb = Cassandra("Analytics_db")
    cdb.start()
    logging.info("Cassandra running: %s" % cdb.is_running())
    cdb.stop()
    cdb.stats()
    odb = Oracle("Inventory_database")
    odb.start()
    odb.stop()
    pdb = PostgreSQL("log_database")
    pdb.start()
    pdb.stop()

    em.dump_sub_table()
    em.dump_all_stats()

    #
    #   U N - S U B S C R I P T I O N ' S
    ##

    em.unsubscribe_all(event_handler=All_Database_All_events)
    em.unsubscribe_all(event_handler=All_Database_start_event)
    em.unsubscribe_all(event_handler=All_Database_stop_event)
    em.unsubscribe_all(event_handler=MongoDB_start_event)
    em.unsubscribe_all(event_handler=MongoDB_stop_event)
    em.unsubscribe_all(event_handler=Cassandra_start_event)
    em.unsubscribe_all(event_handler=Cassandra_stop_event)
    em.unsubscribe_all(event_handler=PostgreSQL_start_event)
    em.unsubscribe_all(event_handler=PostgreSQL_stop_event)
    em.unsubscribe_all(event_handler=Oracle_start_event)
    em.unsubscribe_all(event_handler=Oracle_stop_event)

    #
    #   end: U N - S U B S C R I P T I O N ' S
    ##

    em.dump_sub_table()
    em.dump_all_stats()

    print "Done! - check logs for details :)"
    print 

# __END__
