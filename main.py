#!/usr/local/lib/python3.5
# Display a runtext with double-buffering.
from RGBMatrixBase import RGBMatrixBase #rename file
from rgbmatrix import graphics
import time
import lirc
from multiprocessing import Process, Pipe, Event
import web_helpers as web_h

# TODO
# calculate walking distance via gps and make trains that are within walking distance be a special alert
#have this scroll in with the text for the arrival time be in the upper right corner when it is close by, or have a guy that is walking, like a walkable checkmark
# after for loop, have weather and the time and other cool things flash to the screen, maybe include traffic times
# make stock ticker, use the solid deltas ▼




## non blocking
## have dispatch call function on the running process that switch the role without having to reinitialize. Make the child process be run_text.process

## have dispatch determine if the screen needs to be cleared, then assign the functor to the function being called in the for loop. Dispatch could be called every loop, but it will set a flag after the signal so as to not recall until a new signal is received


##remote thread will handle signaling the LED process with the function to execute
#
# def f(conn):
#     print(time.sleep(5))
#     for i in range(2):
#         conn.send(['packet ', i])
#         # conn.send(['packet 2'])
#     conn.close()
#
#
# if __name__ == '__main__':
#     parent_conn, child_conn = Pipe()
#     p = Process(target=f, args=(child_conn,))
#     p.start()
#     print(parent_conn.recv())   # prints "[42, None, 'hello']"
#     p.join()

#thread helper functions for pipeable while loops
# update these
def w_loop_(f, args, conn):
    while 1:
        f(args)
#
# def f_loop(f, args, con, n):
#     for i in range(0, n):
#         f(args)


import threading
import signal


# class Job(threading.Thread):
#
#     def __init__(self, target, args):
#         threading.Thread.__init__(self)
#         self._target = target
#         self._args = args
#
#         # The shutdown_flag is a threading.Event object that
#         # indicates whether the thread should be terminated.
#         self.shutdown_flag = threading.Event()
#
#         # ... Other thread setup code here ...
#
#     def run(self):
#         print('Thread #%s started' % self.ident)
#
#         while not self.shutdown_flag.is_set():
#             print(self.shutdown_flag.is_set())
#             self._target(self._args)
#             # ... Job code here ...
#             # time.sleep(0.5)
#
#         # ... Clean shutdown code here ...
#         print('Thread #%s stopped' % self.ident)




# def service_shutdown(signum, frame):
#     print('Caught signal %d' % signum)
#     raise ServiceExit
#
# class ServiceExit(Exception):
#     """
#     Custom exception which is used to trigger the clean exit
#     of all running threads and the main program.
#     """
# pass

class RemoteException(Exception):
#
#
#
    pass

#get all stops near you, claculate closest L times by inclusind walking distance from google earth api
class RunText(RGBMatrixBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    # def run(self, runArgs):
    #     # SETUP CODE
    #
    #     pass

        # signal.signal(signal.SIGTERM, service_shutdown) # Ctl - C
        # signal.signal(signal.SIGINT, service_shutdown)
    def dynamic_run(self, conn):
        self.thread = ''



        # have this spawn a thread for the active function


        context = {}
        context['offscreen_canvas'] = self.matrix.CreateFrameCanvas()
        context['font'] = graphics.Font()
        context['font'].LoadFont("../../../fonts/7x13.bdf")
        context['textColor'] = graphics.Color(255, 255, 0)
        context['process'] = ''
        context['connection'] = conn


        while 1:
            try:
                self.train_loop(context)
            except RemoteException as e:
                print('signal recived')
                self.blank_screen(0, context['offscreen_canvas'], context['font'])
                time.sleep(3)

        # future form of the main loop
        # f = self.train_loop(context)
        # while 1:
        #     try:
        #         f
        #     except RemoteException as e:
        #         f = dispatcher(e)
        # while 1:






    def color_loop(self, context):
        self.usleep(2 * 1000)
        context['continuum'] += 1
        context['continuum'] %= 3 * 255

        red = 0
        green = 0
        blue = 0

        if context['continuum'] <= 255:
            c = context['continuum']
            blue = 255 - c
            red = c
        elif context['continuum'] > 255 and context['continuum'] <= 511:
            c = context['continuum'] - 256
            red = 255 - c
            green = c
        else:
            c = context['continuum'] - 512
            green = 255 - c
            blue = c

        context['offscreen_canvas'].Fill(red, green, blue)
        context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])




    def train_loop(self, context):
        exit_condition = False
        while 1:
            # try:


            self.blank_screen(0.5, context['offscreen_canvas'], context['font'])



            arrivals = web_h.get_trains()

            # arrivals = [1,1,1,1]
            for train in arrivals:
                # pos = offscreen_canvas.width
                text = train['dest']
                text_length = 7 * (len(text))
                stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
                self.blank_screen(0.5, context['offscreen_canvas'], context['font'])
                self.scroll_text_to(text, 1 / 30, context['offscreen_canvas'].width, stop_x, 12, 1, context)


                text = train['arr_t'] + ' min'
                text_length = 7 * (len(text))
                stop_x = int((text_length + 64) / 2)

                self.blank_screen(0.5, context['offscreen_canvas'], context['font'])
                self.flash_text(stop_x - text_length, text, context['textColor'], 2, context['offscreen_canvas'], context['font'], 12)
            # except Exception as e:
            #     print(e)



    #right side of screen is text.RHS_x = 64, left side is where text.RHS_x = 0
    #this is represented by pos for now

    def scroll_text_to(self, text, delta_t, start_location, stop_location, offset_y, delay, context):
        # text = 'A'
        # start_location =
        offscreen_canvas = context['offscreen_canvas']
        font = context['font']
        textColor = context['textColor']

        RHS = start_location

        # rewrite this into a dispatch loop function


        #while event.is_not_set():
        #   while body
        #check for command, i.e send ready signal 


        while True:
            cmd = context['connection'].recv()
            print(cmd)
            if cmd[0] == 1:
                print('here')
                raise RemoteException

            offscreen_canvas.Clear()

            # this is the length of the printed text
            l = graphics.DrawText(offscreen_canvas, font, RHS, offset_y, textColor, text)

            RHS -= 1
            if (RHS + l < stop_location):
                time.sleep(delay) # make this based on transition time
                #
                break

            time.sleep(delta_t) # this is speed in ticks per second
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)




    def flash_text(self, RHS, text, textColor, dur, offscreen_canvas, font, offset_y):
        offscreen_canvas.Clear()

        # this is the length of the printed text
        graphics.DrawText(offscreen_canvas, font, RHS, offset_y, textColor, text)

        time.sleep(dur)

        print(offscreen_canvas)
        print('a')
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        print('f')

    def blank_screen(self, dur, offscreen_canvas, font):
        self.flash_text(0, '', graphics.Color(0,0,0), dur, offscreen_canvas, font, 12)








# from multiprocessing import Process, Pipe
# import time


def dispatch(cmd, conn):
    if len(cmd) > 0 and cmd == ['play_pause']:
        conn.send([0])
        pass


    elif cmd == ['func_1']:
        conn.send([0])
        pass



    elif cmd == ['stop']:

        conn.send([1])



# Main function
if __name__ == "__main__":
    lirc.init("myprogram", blocking=False)

    parent_conn, child_conn = Pipe()
    event = Event()

    LED = RunText()
    LED.run = lambda: LED.dynamic_run(child_conn)

    # if (not run_text.process()):
    # run_text.print_help()


    p = Process(target=LED.process, args=())
    p.daemon = False
    p.start()
    #
    # time.sleep(3)

    for i in range(100):
        dispatch(['play_pause'], parent_conn)

    print('here')
    # while 1:
        # parent_conn.send([1])

    dispatch(['stop'], parent_conn)

        # dispatch(['play_pause'], parent_conn)
    # lirc.nextcode()








    p.join()
