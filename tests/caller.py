from handlers import C

c = C() 
n = 5 # n contains the number of functions

# Now here I want to call all the functions in class C 
# in a loop starting from 0 to 99
for i in range(0, n):
    c.f1()
#    func_name = "c.f%d" % i
#    print func_name
#    func_name()

