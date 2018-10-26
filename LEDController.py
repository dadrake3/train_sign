##
from RGBMatrixBase import RGBMatrixBase
from rgbmatrix import graphics
import time
import web_helpers as web_h
import datetime

from LEDContext import *



# Send a main event signal to casecade all singals to end of their loop
# decide whether to clear the signal and keep looping or cascade back to dispatch based on the piped in variable


class LEDController(RGBMatrixBase):
    def __init__(self, *args, **kwargs):
        super(LEDController, self).__init__(*args, **kwargs)
        # self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    # main led process loop
    def run(self, context):

        self.matrix.brightness = 100



        # context['max_brightness'] = self.matrix.brightness
        # context['offscreen_canvas'] = self.matrix.CreateFrameCanvas()
        # context['font'] = graphics.Font()
        # context['font'].LoadFont("../../../fonts/7x13.bdf")
        # context['offset_y'] = 12
        # context['textColor'] = graphics.Color(255, 255, 0)
        # context['curr_color'] = 0
        # context['colors'] = [graphics.Color(255, 0, 0), graphics.Color(0, 0, 255), graphics.Color(0, 255, 0), graphics.Color(255, 255, 255), graphics.Color(255, 255, 0), graphics.Color(255, 0, 255), graphics.Color(0, 255, 255)] # change this to a binary of the numbers 0 to 8
        # context['strobe_delay'] = 0.03



        # print(self.matrix.brightness)


        func = 'func_2' # start off in nop loop

        while 1:
            #holds function the same for times tasks
            self.func_dispatch(func, context)
            # while not context.remote_event.is_set():
            context.main_loop(self.matrix)

            if context.remote_event.is_set():
                # print('outer loop')
                func = context.pipe.recv()
                if func == 'restart':
                    break

                context.remote_event.clear()

            # self.train_loop(context)


    def func_dispatch(self, func, context):

        context.task_queue = queue.Queue() #empty the queue on new input



        if func == 'stop':
            self.nop(context)

        elif func == 'func_1':
            self.info_mode(context)

        elif func == 'func_2':
            self.gradient(context)

        elif func == 'func_3':
            self.solid(context)

        elif func == 'func_4':
            self.strobe(context)

        # elif func == 'func_5':
        #     self.color_strobe(context)


    def nop(self, context):
        fg = Foreground()
        bg = Background(static=True)
        context.task_queue.put([fg, bg])

    def info_mode(self, context):
        self.show_trains(context)
        self.show_time(context)
        self.show_weather(context)


    def show_trains(self, context):
        arrivals = web_h.get_trains()

        if not arrivals:
            text = 'No Trains Are Available'
            fg = TextForeground(text, hold_time=0.3, scroll_off=True)
            bg = Background(static=True)
            context.task_queue.put([fg, bg])

            return

        for train in arrivals:
            text = train['dest']
            fg = TextForeground(text, hold_time=2, )
            bg = Background(static=True)
            context.task_queue.put([fg, bg])


            text = train['arr_t'] + ' min'
            fg = TextForeground(text, hold_time=2, flash_text=True)
            bg = Background(static=True)
            context.task_queue.put([fg, bg])

    def show_weather(self, context):
        temp, info = web_h.get_weather()

        fg = TextForeground(temp, hold_time=2, flash_text=True)
        bg = Background(static=True)

        context.task_queue.put([fg, bg])

        fg = TextForeground(info, hold_time=2, flash_text=False)
        bg = Background(static=True)

        context.task_queue.put([fg, bg])

    def show_time(self, context):
        now = datetime.datetime.now()
        text = str((now.hour % 12) + 1) + ':' + str(now.minute) #+ 'and ' + info.lower()
        print(text)
        fg = TextForeground(text, hold_time=2, flash_text=True)
        bg = Background(static=True)

        context.task_queue.put([fg, bg])

    def gradient(self, context):

        fg = Foreground()
        bg = PerlinBackground()

        context.task_queue.put([fg, bg])

    def solid(self, context):
        fg = Foreground()
        bg = FillBackground()

        context.task_queue.put([fg, bg])

    def strobe(self, context):
        fg = Foreground()
        bg = StrobeBackground()

        context.task_queue.put([fg, bg])
