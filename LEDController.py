##
from RGBMatrixBase import RGBMatrixBase
from rgbmatrix import graphics
import time
import web_helpers as web_h
import datetime





# Send a main event signal to casecade all singals to end of their loop
# decide whether to clear the signal and keep looping or cascade back to dispatch based on the piped in variable





class LEDController(RGBMatrixBase):
    def __init__(self, *args, **kwargs):
        super(LEDController, self).__init__(*args, **kwargs)
        # self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    # main led process loop
    def run(self, context):
        context['max_brightness'] = self.matrix.brightness
        context['offscreen_canvas'] = self.matrix.CreateFrameCanvas()
        context['font'] = graphics.Font()
        context['font'].LoadFont("../../../fonts/7x13.bdf")
        context['offset_y'] = 12
        context['textColor'] = graphics.Color(255, 255, 0)
        context['curr_color'] = 0
        context['colors'] = [graphics.Color(255, 0, 0), graphics.Color(0, 0, 255), graphics.Color(0, 255, 0), graphics.Color(255, 255, 255), graphics.Color(255, 255, 0), graphics.Color(255, 0, 255), graphics.Color(0, 255, 255)] # change this to a binary of the numbers 0 to 8
        context['strobe_delay'] = 0.03



        # print(self.matrix.brightness)
        self.matrix.brightness = 100

        context['next_func'] = 'func_1' # start off in nop loop

        while 1:
            while not context['remote_event'].is_set():
                self.func_dispatch(context)
                self.loop_dispatch(context)

            # print('outer loop')
            context['next_func'] = context['pipe'].recv()
            if context['next_func'] == 'restart':
                break
            context['remote_event'].clear()
            # self.train_loop(context)
            # return

    def func_dispatch(self, context):
        context['remote_event'].clear()

        self.blank_screen(0, context)

        if context['next_func'] == 'stop':
            self.nop(context)

        elif context['next_func'] == 'func_1':
            self.info_mode(context)

        elif context['next_func'] == 'func_2':
            self.color_fade(context)

        elif context['next_func'] == 'func_3':
            self.solid(context)

        elif context['next_func'] == 'func_4':
            self.strobe(context)

        elif context['next_func'] == 'func_5':
            self.color_strobe(context)


    # put this at the end of every while loop
    def loop_dispatch(self, context):
        if context['remote_event'].is_set():
            print('here', 'remote_event')
            if context['param_event'].is_set():
                cmd = context['pipe'].recv()
                print(cmd, 'param_event')

                if cmd == 'up':
                    self.brightness_util(5, context)

                elif cmd == 'down':
                    self.brightness_util(-5, context)

                elif cmd == 'left':
                    self.color_util(context, -1)

                elif cmd == 'right':
                    self.color_util(context, 1)

                elif cmd == 'vol_up':
                    self.speed_util(context, -0.005)

                elif cmd == 'vol_down':
                    self.speed_util(context, 0.005)




                context['param_event'].clear()
                context['remote_event'].clear()



    def nop(self, context):
        print('nop')
        while not context['remote_event'].is_set():
            self.loop_dispatch(context)

    def strobe(self, context):
        while not context['remote_event'].is_set():
            i = context['curr_color']
            delay = context['strobe_delay']
            context['offscreen_canvas'].Fill(context['colors'][i].red, context['colors'][i].green, context['colors'][i].blue)
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])
            context['remote_event'].wait(delay * 2)

            black = graphics.Color(0, 0, 0)
            context['offscreen_canvas'].Fill(black.red, black.green, black.blue)
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])
            context['remote_event'].wait(delay * 2)

    def color_strobe(self, context):
        i = 0
        while not context['remote_event'].is_set():
            delay = context['strobe_delay']
            context['offscreen_canvas'].Fill(context['colors'][i].red, context['colors'][i].green, context['colors'][i].blue)
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])
            context['remote_event'].wait(delay * 2)

            black = graphics.Color(0, 0, 0)
            context['offscreen_canvas'].Fill(black.red, black.green, black.blue)
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])
            context['remote_event'].wait(delay * 2)

            i = (i + 1) % len(context['colors'])


    def solid(self, context):
        while not context['remote_event'].is_set():
            i = context['curr_color']
            context['offscreen_canvas'].Fill(context['colors'][i].red, context['colors'][i].green, context['colors'][i].blue)
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])

            # context['brightness_event'].wait(100)

            self.loop_dispatch(context)

    def brightness_util(self, delta, context):
            b = self.matrix.brightness
            b = max(0, min(100, b + delta))
            print(b)
            self.matrix.brightness = b

            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])

            # `self.matrix.brightness = b
            # context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])`

    def color_util(self, context, delta):
        i = context['curr_color']
        if delta > 0:
            context['curr_color'] = (i + 1) % len(context['colors'])

        elif delta < 0:
            context['curr_color'] = (i - 1) % (-1 * len(context['colors']))


        context['textColor'] = context['colors'][context['curr_color']]

    def speed_util(self, context, delta):
        d = context['strobe_delay']
        d = max(0, min(0.6, d + delta))
        context['strobe_delay'] = d

    def color_fade(self, context):
        # red = graphics.Color(255, 0, 0)
        context['continuum'] = 0

        while not context['remote_event'].is_set():

            delay = context['strobe_delay']

            context['remote_event'].wait(delay)
            # self.usleep(2 * 1000)
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

            self.loop_dispatch(context)

    def info_mode(self, context):
        # self.show_time(context)
        # self.show_weather(context)
        self.show_trains(context)

    def show_trains(self, context):
        # while 1:

        self.blank_screen(0, context)

        #prevents against there being no trains
        arrivals = web_h.get_trains()

        if not arrivals or 1:
            text = 'No Trains Are Available'
            text_length = 7 * (len(text))
            stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
            if self.blank_screen(0.5, context) < 0:
                return -1
            self.scroll_text_to_end(text, 1 / 30, context)

            return -1

        # arrivals = [1,1,1,1]
        for train in arrivals:
            # pos = offscreen_canvas.width
            text = train['dest']
            text_length = 7 * (len(text))
            stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
            if self.blank_screen(0.5, context) < 0:
                return -1
            if self.scroll_text_to(text, 1 / 30, stop_x, context['offscreen_canvas'].width, 1, context) < 0:
                return -1


            text = train['arr_t'] + ' min'
            text_length = 7 * (len(text))
            stop_x = int((text_length + 64) / 2)

            if self.blank_screen(0.5, context) < 0:
                return -1
            if self.flash_text(stop_x - text_length, text, 2, context) < 0:
                return -1

        return 0

    def show_weather(self, context):
        temp, info = web_h.get_weather()
        if not temp or not info:
            return -1

        text = temp #+ 'and ' + info.lower()
        text_length = 7 * (len(text))
        stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
        # print(stop_x)
        if self.blank_screen(0.5, context) < 0:
            return -1
        if self.flash_text(stop_x - text_length, text, 3, context) < 0:
            return -1


        text = info #+ 'and ' + info.lower()
        text_length = 7 * (len(text))
        stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
        # print(stop_x)
        if self.blank_screen(0.5, context) < 0:
            return -1
        if self.flash_text(stop_x - text_length, text, 3, context) < 0:
            return -1

        return 0


        # text = temp
        # text_length = 7 * (len(text))
        # stop_x = int((text_length + 64) / 2)
        #
        # if self.blank_screen(0.5, context) < 0:
        #     return -1
        # if self.flash_text(stop_x - text_length, text, 2, context) < 0:
        #     return -1

    def show_time(self, context):
        now = datetime.datetime.now()

        text = str((now.hour % 12) + 1) + ':' + str(now.minute) #+ 'and ' + info.lower()
        text_length = 7 * (len(text))
        stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2
        # print(stop_x)
        if self.blank_screen(0.5, context) < 0:
            return -1
        if self.flash_text(stop_x - text_length, text, 3, context) < 0:
            return -1

    # delay is hold time once text is done moving
    def scroll_text_to(self, text, speed, stop_location, start_location, hold_time, context):
        # text = 'A'


        RHS = start_location
        context['offset_y'] = 12

        while not context['remote_event'].is_set():

            context['offscreen_canvas'].Clear()

            # this is the length of the printed text
            l = graphics.DrawText(context['offscreen_canvas'], context['font'], RHS, context['offset_y'], context['textColor'], text)

            RHS -= 1
            if (RHS + l < stop_location):
                context['remote_event'].wait(hold_time)#.sleep(delay) # make this based on transition time
                print('end of text')
                return 0

            context['remote_event'].wait(speed) # this is speed in ticks per second
            context['offscreen_canvas'] = self.matrix.SwapOnVSync(context['offscreen_canvas'])

            self.loop_dispatch(context)

        return -1

    def scroll_text_to_end(self, text, speed, context):
        text_length = 7 * (len(text))

        return self.scroll_text_to(text, speed, 0, context['offscreen_canvas'].width , 0, context)


    def flash_text(self, RHS, text, dur, context):
        textColor =  context['textColor']
        offscreen_canvas = context['offscreen_canvas']
        font = context['font']

        offscreen_canvas.Clear()
        if context['remote_event'].is_set():
            return -1

        # this is the length of the printed text
        graphics.DrawText(offscreen_canvas, font, RHS, context['offset_y'], textColor, text)
        context['remote_event'].wait(dur)

        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

        return 0

    def blank_screen(self, dur, context):
        offscreen_canvas = context['offscreen_canvas']
        offscreen_canvas.Fill(0, 0, 0)
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
        context['remote_event'].wait(dur)

        # if()

        if context['remote_event'].is_set():
            return -1

        return 0
