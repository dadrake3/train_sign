#!/usr/local/lib/python3.5
# Display a runtext with double-buffering.
from LEDController import LEDController
import lirc
from multiprocessing import Process, Pipe, Event
import time


# IR input process


def main():
    lirc.init("myprogram")

    parent_pipe, child_pipe = Pipe()
    remote_event = Event()
    param_event = Event()
    LED = LEDController()

    context = {}
    context['param_event'] = param_event
    context['remote_event'] = remote_event
    context['pipe'] = child_pipe

    p = Process(target=LED.process, args=(context,))
    p.daemon = False
    p.start()

    while 1:
        c = lirc.nextcode()
        if len(c) > 0:
            cmd = c[0]


            if cmd == 'up' or cmd == 'down' or cmd == 'left' or cmd == 'right' or cmd == 'vol_up'or cmd == 'vol_down':
                print('setting p')
                context['param_event'].set()

            context['remote_event'].set()
            parent_pipe.send(cmd)

            # if cmd == 'restart':
            #     break
            time.sleep(0.02)

    p.join()



if __name__ == "__main__":
    while 1:
        main()
