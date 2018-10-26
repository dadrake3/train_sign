#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import random
import numpy as np
from numpy import array
from matplotlib import pyplot as plt
from noise import snoise3, snoise2
import math
import queue

screen_height = 16
screen_width = 64
delta_t = 0.1
norm = plt.Normalize()
clk = 0


class LEDContext(object):
    def __init__(self, param_event, remote_event, pipe):

        self.param_event = param_event
        self.remote_event = remote_event
        self.pipe = pipe

        self.background = Background()
        self.foreground = Foreground()
        self.image = None

        self.task_queue = queue.Queue()

        # self.image =
        # update frequency

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.__brightness = 1


    def param_dispatch(self):
        # if self.remote_event.is_set():
        #     print('here', 'remote_event')
        if self.param_event.is_set():
            cmd = self.pipe.recv()
            # print(cmd, 'param_event')

            if cmd == 'up':
                self.change_brightness(0.05)

            elif cmd == 'down':
                self.change_brightness(-0.05)

            elif cmd == 'right':
                self.background.change_background(1)

            elif cmd == 'left':
                self.background.change_background(-1)

            elif cmd == 'vol_up':
                self.background.change_speed(1)

            elif cmd == 'vol_down':
                self.background.change_speed(-1)
            elif cmd == 'back':
                self.background.modifier()


            self.param_event.clear()
                # context.remote_event.clear()

    def main_loop(self, led_matrix):
        global clk

        while not self.task_queue.empty():

            task = self.task_queue.get()
            # print(task[0])
            while not self.remote_event.is_set():
                self.foreground = task[0]
                self.background = task[1]

                if self.update(clk):
                    # print('broke')
                    break

                img_array = np.asarray(self.image)


                led_matrix.Clear()
                led_matrix.SetImage(self.image, 0, 0)


                self.remote_event.wait(delta_t)
                self.param_dispatch()

                clk = (clk + 1) % (2 ** 32)

    def update(self, clk):
        img = self.background.get_background(clk)
        # print(img)

        img, flag = self.foreground.get_foreground(img, clk)

        if flag:
            # print(clk, 'broke')
            return True

        img = ImageEnhance.Brightness(img)
        img = img.enhance(self.__brightness)
        self.image = img.convert('RGB')

        return False

    def change_brightness(self, delta):
        self.__brightness = max(min(self.__brightness + delta, 1), 0)

    def change_background(self, delta):
        self.background.change_background(delta)


class Background(object):
    def __init__(self, static=False, background_brightness=1.0):
        # print('here 1')
        # this is only used when displaying text over the background
        self.background_brightness = background_brightness
        self.static = static
        self.screen_width = screen_width
        self.screen_height = screen_height

    def __str__(self):
     return 'Background Super Object'


    # default to returning a blank image
    def get_background(self, clk):
        return Image.new('RGB', (self.screen_width, self.screen_height))

    def change_background(self, delta):
        pass

    def change_speed(self, delta):
        pass

    def modifier(self):
        pass


class PerlinBackground(Background):

    def __init__(self, start_gradient=0, background_speed=2, octaves=4, freq=32.0, static=False, background_brightness=1.0, dim=2):
            super(PerlinBackground,self).__init__(static=static, background_brightness=background_brightness)
            self.__bw = np.zeros(shape=(16, 64)) # used for perlin gradients
            self.__gradients = [plt.cm.gist_rainbow,
                                    plt.cm.jet,
                                    plt.cm.plasma,
                                    plt.cm.inferno,
                                    plt.cm.flag,
                                    plt.cm.prism,
                                    plt.cm.gist_ncar,
                                    plt.cm.hot,
                                    plt.cm.cool,
                                    plt.cm.rainbow,
                                    plt.cm.Blues]
            self.__curr_gradient = start_gradient
            self.__background_speed = background_speed
            self.__octaves = octaves # have this changed by remote input
            self.__freq = freq * self.__octaves # have this changed by remote input
            self.__z_offset = np.random.randint(2 ** 8)
            self.__dim = dim

    def __str__(self):
     return 'Perlin Background Object'

    def get_background(self, clk):
        z = clk * self.__background_speed + self.__z_offset

        for y in range(self.screen_height):
            for x in range(self.screen_width):
                if self.__dim == 0:
                    self.__bw[y][x] = int(snoise2(y / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

                elif self.__dim == 1:
                    self.__bw[y][x] = int(snoise2(z / self.__freq, x / self.__freq, self.__octaves) * 127.0 + 128.0)

                elif self.__dim == 2:
                    self.__bw[y][x] = int(snoise3(x / self.__freq, y / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

        rgb = self.__gradients[self.__curr_gradient](norm(self.__bw))
        img = Image.fromarray(np.uint8(rgb * 255 * self.background_brightness)).convert('RGB')
        return img

    def change_background(self, delta):
        if not self.static:
            self.__curr_gradient = max(min(self.__curr_gradient + delta, len(self.__gradients) - 1), 0)

    def change_speed(self, delta):
        if not self.static:
            self.__background_speed = max(min(self.__background_speed + delta, 10), 0)

    def modifier(self):
        print(self.__dim)
        self.__dim = (self.__dim + 1) % 3
        print(self.__dim)


class FillBackground(Background):
    def __init__(self, color_idx=0, static=False, background_brightness=1.0):
            super(FillBackground, self).__init__(static=static,background_brightness=background_brightness)
            self.__color_idx = color_idx
            self.background_color = 0
            self.__fade = False
            self.change_background(color_idx)

    def __str__(self):
     return 'Fill Background Object'

    def get_background(self, clk):
        img = Image.new('RGB', (self.screen_width, self.screen_height))
        img.paste(self.background_color, [0,0, self.screen_width,self.screen_height])
        # print(img)
        return img

    def change_background(self, delta):
        if not self.static:
            # self.__color_idx = max(min(self.__color_idx + delta, 0), 1)
            self.__color_idx = (self.__color_idx + delta) % 1

            a = np.array([1]) * delta
            c = np.uint8((plt.cm.gist_ncar(a) * 255 * self.background_brightness))
            self.background_color = c[0][1], c[0][1], c[0][2]

    def modifier(self):
        self.__fade = not self.__fade


#.1 .2 .3 .4 .5
#1  2  3  4  5
#0  1  0  1  0

class StrobeBackground(FillBackground):
    def __init__(self, strobe_delay=5):
        super(StrobeBackground, self).__init__()

        self.__strobe_speed = strobe_delay #clk pulses per strobe
        self.__color_strobe = False
        super(StrobeBackground, self).change_background(0.5)

    def __str__(self):
     return 'Strobe Background Object'

    # fix this
    def get_background(self, clk):
        img = Image.new('RGB', (self.screen_width, self.screen_height))

        # print(math.floor(clk / self.__strobe_speed) % 2, clk)
        if math.floor(clk / self.__strobe_speed) % 2:
            img.paste(self.background_color, [0,0, self.screen_width,self.screen_height])
            return img
        else:
            # img = img.paste((0,0,0), [0,0, self.screen_width,self.screen_height])
            # print(img, 'here')
            return img

    def change_speed(self, delta):
        if not self.static:
            self.__strobe_speed = max(min(self.__strobe_speed + delta, 10), 1) #min 1 bc divide by zero error

    def modifier(self):
        self.__color_strobe = not self.__color_strobe


class Foreground(object):
    def __init__(self):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def __str__(self):
     return 'Super Foreground Object'

    def get_foreground(self, img, clk):
        return img, False


# one time use only. Cannot be reused unless reset is called
class TextForeground(Foreground):
    def __init__(self, text, scroll_off=False, text_color=(255, 255, 255), hold_time=3, text_speed=1.5, flash_text=False):
        super(TextForeground, self).__init__()
        self.__font = ImageFont.load('/usr/share/fonts/bitmap/cherry/cherry_b_13.pil')
        # self.__font = ImageFont.load_default()
        self.__hold_time_temp = hold_time
        self.__reset = True
        self.__hold_time = hold_time
        self.__text_speed = text_speed
        self.__text_color = text_color
        self.__text = text
        self.__y = 2
        # self.__x = -1 * float('inf')
        self.__scroll_off = scroll_off
        self.__text_length = self.__font.getsize(text)[0]
        self.__x = 2 * self.__text_length - 1

        self.used = False

        if scroll_off:
            self.__stop = -1 * self.__text_length
        else:
            self.__stop = (self.screen_width - self.__text_length) / 2

        if flash_text:
            self.__x = self.__stop

    def __str__(self):
        return 'Text Foreground Object' + self.__text



    def get_foreground(self, img, clk):
        if self.used:
            raise OneUseObjectError

        text = self.__text
        ret_flag = False

        # print(self.__x, self.__stop, self.__hold_time, self.__text_length)

        if self.__x <= self.__stop:
            self.__x = self.__stop
            self.__hold_time -= delta_t
        else:
            # self.__x = ((-self.__text_speed * clk) % (64 + self.__text_length)) - self.__text_length - 1
            self.__x -= self.__text_speed

        # print(self.hold_time)
        if self.__hold_time <= 0:
            self.used = True
            ret_flag = True

        draw = ImageDraw.Draw(img)
        draw.text((self.__x, self.__y), text, self.__text_color, font=self.__font)

        return img, ret_flag


class OneUseObjectError(Exception):
    pass
