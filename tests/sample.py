#class handlers:
#    def event_handler_1(self, topic, event, **kwargs):
#        print "event_handler_1: [topic=%s] [event=%s] args=%s" % (topic, event, kwargs)
#    def exception_handler_1(self, e, topic, event, **kwargs):
#        print "exception_handler_1: [exception=%s] [topic=%s] [event=%s] args=%s" % (e, topic, event, kwargs)

import sys

#filename = "handler_functions.py"
filename = "tessst.py"
n=10

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



