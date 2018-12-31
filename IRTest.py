import lirc

lirc.init("ledsign")
while 1:
    c = lirc.nextcode()
    print(c)
