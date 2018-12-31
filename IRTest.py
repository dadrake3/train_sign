import lirc

lirc.init("myprogram")
while 1:
    c = lirc.nextcode()
    print(c)
