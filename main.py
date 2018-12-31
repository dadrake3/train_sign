#!/usr/local/lib/python3.5
# Display a runtext with double-buffering.
from LEDController import LEDController
from LEDContext import LEDContext
import lirc
from multiprocessing import Process, Pipe, Event
import time


# IR input process

def get_input(sim=False):
    if sim:
        return [input()]
    else:
        return lirc.nextcode()
    # print(c, 'here')


    # continue




def main():
    lirc.init("ledsign")

    parent_pipe, child_pipe = Pipe()
    remote_event = Event()
    param_event = Event()
    LED = LEDController()
    context = LEDContext(param_event, remote_event, child_pipe)



    p = Process(target=LED.process, args=(context,))
    p.daemon = False
    p.start()

    # time.sleep(2)
    print('starting IR')



    while 1:

        c = get_input(False)

        if len(c) > 0:
            cmd = c[0]
            print(c[0], 'IR process')
        #
            if cmd == 'up' or cmd == 'down' or cmd == 'left' or cmd == 'right' or cmd == 'vol_up'or cmd == 'vol_down' or cmd == 'back':
                print('setting p')
                context.param_event.set()

            else:
                context.remote_event.set()


            parent_pipe.send(cmd)

            # if cmd == 'restart':
            #     break
            # time.sleep(0.02)



    p.join()



if __name__ == "__main__":
    while 1:
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            lirc.deinit()






