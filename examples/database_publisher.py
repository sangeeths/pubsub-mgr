# NOTE: add the top level directory to sys.path
import sys, os
sys.path.append(os.getcwd().replace("examples",""))

#for item in sys.path:
#    print item

from pubsub.manager import EventManager
import logging

class Database:
    em = EventManager()
    def __init__(self, name):
        self.running = False
        self.name = name
    def start(self):
        self.running = True
        logging.info("Starting %s [DB=%s]" % \
                    (self.__class__.__name__, self.name))
        Database.em.publish(topic=self.__class__.__name__, 
                            event='DatabaseStartEvent',
                            database_type=self.__class__.__name__,
                            database_name=self.name)
    def stop(self):
        self.running = False
        logging.info("Stopping %s [DB=%s]" % \
                    (self.__class__.__name__, self.name))
        Database.em.publish(topic=self.__class__.__name__, 
                            event='DatabaseStopEvent',
                            database_type=self.__class__.__name__,
                            database_name=self.name)
    def is_running(self):
        logging.info("status [DB=%s] [name=%s] is %s" % \
                    (self.__class__.__name__, self.name, self.running))
        return self.running 

    def stats(self):
        Database.em.dump_sub_table()
        Database.em.dump_all_stats()

class MongoDB(Database):
    def __init__(self, name="defaultMongoDB", *args, **kwargs):
        Database.__init__(self, name)
        # initialize other parameters
    def start(self):
        Database.start(self)
        # Anyother MongoDB specific 
        # threads/process can be started here!!
    def stop(self):
        # Anyother MongoDB specific 
        # threads/process can be stopped here!!
        Database.stop(self)
    def is_running(self):
        return Database.is_running(self)
    def print_stats(self):
        return Database.stats(self)

class Cassandra(Database):
    def __init__(self, name="defaultCassandra", *args, **kwargs):
        Database.__init__(self, name)
        # initialize other parameters
    def start(self):
        Database.start(self)
        # Anyother Cassandra specific 
        # threads/process can be started here!!
    def stop(self):
        # Anyother Cassandra specific 
        # threads/process can be stopped here!!
        Database.stop(self)
    def is_running(self):
        return Database.is_running(self)
    def print_stats(self):
        return Database.stats(self)

class PostgreSQL(Database):
    def __init__(self, name="defaultPostgreSQL", *args, **kwargs):
        Database.__init__(self, name)
        # initialize other parameters
    def start(self):
        Database.start(self)
        # Anyother PostgreSQL specific 
        # threads/process can be started here!!
    def stop(self):
        # Anyother PostgreSQL specific 
        # threads/process can be stopped here!!
        Database.stop(self)
    def is_running(self):
        return Database.is_running(self)
    def print_stats(self):
        return Database.stats(self)

class Oracle(Database):
    def __init__(self, name="defaultOracle", *args, **kwargs):
        Database.__init__(self, name)
        # initialize other parameters
    def start(self):
        Database.start(self)
        # Anyother Oracle specific 
        # threads/process can be started here!!
    def stop(self):
        # Anyother Oracle specific 
        # threads/process can be stopped here!!
        Database.stop(self)
    def is_running(self):
        return Database.is_running(self)
    def print_stats(self):
        return Database.stats(self)

if __name__ == "__main__":
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
    pdb = Oracle("log_database")
    pdb.start()
    pdb.stop()
