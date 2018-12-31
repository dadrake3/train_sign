#!/usr/bin/env python
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import random
import numpy as np
from numpy import array
from matplotlib import pyplot as plt
from noise import snoise3, snoise2
import math
import queue
from datetime import *
import pyaudio
import wave

screen_height = 16
screen_width = 64
delta_t = 0.1
norm = plt.Normalize()
clk = 0

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = int(RATE / (1 / delta_t))# 2048 # RATE / number of updates per second
# CHUNK = 64
RECORD_SECONDS = 20




# use a Blackman window
window = np.blackman(CHUNK)

p = pyaudio.PyAudio()
            # self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
print('opening stream')
STREAM = p.open(
    format = pyaudio.paInt16,
    channels = 1,
    rate = 44100,
    input_device_index = 0, # this needs to be tested
    input = True,
    frames_per_buffer=CHUNK)
print('stream opened')

gradients = [plt.cm.gist_rainbow,
            plt.cm.jet,
            plt.cm.plasma,
            plt.cm.inferno,
            plt.cm.flag,
            plt.cm.prism,
            plt.cm.gist_ncar,
            plt.cm.summer,
            plt.cm.cool,
            plt.cm.Pastel1,
            plt.cm.rainbow,
            plt.cm.Blues,
            plt.cm.bone,
            plt.cm.hot,
            plt.cm.gist_earth,
            plt.cm.Greys,
            plt.cm.YlGnBu,
            plt.cm.twilight_shifted]




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

        self.__brightness = 0.5


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
                print('here')
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

            # add every single gradient. itl be sick
            # self.__gradients = [    plt.cm.gist_rainbow,
            #                         plt.cm.jet,
            #                         plt.cm.plasma,
            #                         plt.cm.inferno,
            #                         plt.cm.flag,
            #                         plt.cm.prism,
            #                         plt.cm.gist_ncar,
            #                         plt.cm.summer,
            #                         plt.cm.cool,
            #                         plt.cm.Pastel1,
            #                         plt.cm.rainbow,
            #                         plt.cm.Blues,
            #                         plt.cm.bone,
            #                         plt.cm.hot,
            #                         plt.cm.gist_earth,
            #                         plt.cm.Greys,
            #                         plt.cm.YlGnBu,
            #                         plt.cm.twilight_shifted]


            self.__curr_gradient = start_gradient
            self.__background_speed = background_speed
            self.__octaves = octaves # have this changed by remote input
            self.__freq = freq * self.__octaves # have this changed by remote input
            self.__z_offset = np.random.randint(2 ** 8)
            self.__dim = dim

            # audio equalizer shit
            # self.p = pyaudio.PyAudio()
            # # self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)
	
            # print('opening stream')
            # self.stream = self.p.open(
            #     format = pyaudio.paInt16,
            #     channels = 1,
            #     rate = 44100,
            #     input_device_index = 0, # this needs to be tested
            #     input = True,
            #     frames_per_buffer=CHUNK)
            # print('stream opened')


    def __str__(self):
     return 'Perlin Background Object'

    def get_background(self, clk):
        z = clk * self.__background_speed + self.__z_offset

        # if self.__dim == 3:
        if 1:
            data = STREAM.read(CHUNK, exception_on_overflow=False)
            # wave_data = wave.struct.unpack("%dh" % CHUNK, data)
            # np_array_data = np.array(wave_data)
            # audio_data = np.abs(np_array_data * window)
            # audio_data = audio_data[::int(CHUNK / 64)]
            # max_ = max(audio_data)

            # norm2 = plt.Normalize(0, max_)
            # audio_data = 16 * norm2(audio_data)
            print('here')

            img = Image.new('RGB', (self.screen_width, self.screen_height))
            # # print(max_)
            # # if max_ < 100:
            # # return img
            # pixels = img.load()
            # for x in range(64):  # for every pixel:
            #    for y in range(16):
            #        if 16 - y > audio_data[x]:
            #            pixels[x, y] = (0,0,0)
            #        else:
            #            c = int(snoise3((x + clk) / self.__freq, (x + clk) / self.__freq, z / self.__freq,
            #                                          self.__octaves) * 127.0 + 128.0)
            #            c = gradients[self.__curr_gradient](norm(c))
            #            pixels[x, y] = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)

            return img

        else:

            for y in range(self.screen_height):
                for x in range(self.screen_width):
                    if self.__dim == 0:
                        self.__bw[y][x] = int(snoise3(y / self.__freq, y / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

                    elif self.__dim == 1:
                        self.__bw[y][x] = int(snoise3(x / self.__freq, x / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

                    elif self.__dim == 2:
                        self.__bw[y][x] = int(snoise3(x / self.__freq, y / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

                    elif self.__dim == 3:
                        self.__bw[y][x] = int(snoise3((x + clk) / self.__freq, y / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

                    elif self.__dim == 4:
                        self.__bw[y][x] = int(snoise3(x / self.__freq, (y + clk) / self.__freq, z / self.__freq, self.__octaves) * 127.0 + 128.0)

            rgb = gradients[self.__curr_gradient](norm(self.__bw))
            img = Image.fromarray(np.uint8(rgb * 255 * self.background_brightness)).convert('RGB')
            return img

    def change_background(self, delta):
        if not self.static:
            self.__curr_gradient = (self.__curr_gradient + delta) % len(gradients)

            # max(min(self.__curr_gradient + delta, len(gradients) - 1), 0)

    def change_speed(self, delta):
        if not self.static:
            self.__background_speed = max(min(self.__background_speed + delta, 10), 0)

    def modifier(self):
        if not self.static:
            self.__dim = (self.__dim + 1) % 3



class FillBackground(Background):
    def __init__(self, color_idx=0.0, static=False, background_brightness=1.0, fade=False, color_strobe=False, strobe_speed=2, strobe=False):
            super(FillBackground, self).__init__(static=static,background_brightness=background_brightness)
            self.color_idx = 0
            self.fade = fade
            self.background_color = 0
            self.strobe = strobe
            self.__curr_gradient = 1
            self.__color_strobe = color_strobe
            self.__strobe_speed = strobe_speed  # MIN VALUE IS 1
            self.fade_speed = 0.02

            self.change_background(color_idx)

    def get_background(self, clk):
        # level = norm(self.__color_idx * 255.0 * self.background_brightness)
        # level = self.__color_idx
        # print(self.__curr_gradient, 'grad')


        if self.fade:
            c = gradients[self.__curr_gradient](self.color_idx)

            self.background_color = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
            self.color_idx = (-1 * abs(((clk * self.fade_speed) % 2) - 1)) + 1

            # print(self.color_idx)

        elif self.strobe:
            flag = clk % self.__strobe_speed
            # flag = flag % 20
            # print(flag)

            if flag < 0.5 * self.__strobe_speed:
                if self.__color_strobe:
                    self.change_background(2) #go up 5 colors
                return Image.new('RGB', (self.screen_width, self.screen_height))


            else:
                c = gradients[self.__curr_gradient](self.color_idx)

                self.background_color = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)
                img = Image.new('RGB', (self.screen_width, self.screen_height))
                img.paste(self.background_color, [0, 0, self.screen_width, self.screen_height])
                return img

        else:
            c = plt.cm.rainbow(self.color_idx)

            self.background_color = int(c[0] * 255), int(c[1] * 255), int(c[2] * 255)

        img = Image.new('RGB', (self.screen_width, self.screen_height))
        img.paste(self.background_color, [0, 0, self.screen_width, self.screen_height])
        # print(img)
        return img

    def change_background(self, delta):
        if not self.static:
            if self.fade:
                self.__curr_gradient = (self.__curr_gradient + 1) % len(gradients)
                print(self.__curr_gradient)
            else:
                self.color_idx = abs(self.color_idx + (delta / 40)) % 1

    def change_speed(self, delta):
        if not self.static:
            if self.strobe:
                self.__strobe_speed = max(min(self.__strobe_speed + delta, 10), 1) #min 1 bc
            elif self.fade:
                self.fade_speed = max(min(self.fade_speed + (delta / 100), 0.1), 0.001)
                print(self.fade_speed)


    def modifier(self):
        if not self.static:
            if self.strobe:
                self.__color_strobe = not self.__color_strobe



# class RandomBackground(Background):
#     def __init__(self):
#         Super(RandomBackground, self).__init__()
#         pass


class WeatherBackground(Background):
    def __init__(self, static=False, background_brightness=1.0, condition=-1):
        super(WeatherBackground, self).__init__(static=static, background_brightness=background_brightness)
        self.__condition = condition
        self.thunder = 0
        self.rain = 0
        self.snow = 0
        self.background_color = (0,0,0)

        # Thunderstorm, rain, drizzle

        if condition == 0:
            self.thunder = 1
            self.intensity = 4
            self.rain = 1
            self.background_color = (0,0,20)
        elif condition == 1:
            self.intensity = 2
            self.rain = 1
            self.background = (10, 10, 40)
        elif condition == 2:
            self.intensity = 1
            self.rain = 1
            self.background_color = (60, 60, 80)
        elif condition == 3:
            self.intensity = 2
            self.snow = 1
            self.background_color = (150,150,150)


        img = Image.new('RGB', (self.screen_width, self.screen_height))
        img.paste(self.background_color, [0, 0, self.screen_width, self.screen_height])



        if self.rain:
            # self.r = 1
            self.shift = 0
            # self.image = img
            for x in range(self.screen_width):
                p = random.randint(0, 100)
                if p < 2 * self.intensity:
                    draw = ImageDraw.Draw(img)

                    y1 = random.randint(0, 16)
                    y2 = random.randint(y1, 16)
                    if 4 < y2 - y1 or y2 - y1 <=1:
                        continue

                    draw.line((x, y1, x, y2), fill=(120, 120, 120))



        elif self.snow:
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    p = random.randint(0, 100)
                    if p < 2 * self.intensity:
                        img.putpixel((x,y), (255,255,255))

        self.image = img





    def get_background(self, clk):
        # img_array = np.asarray(self.image)

        # img_array = np.roll(img_array, self.shift, axis=0)
        # self.image = Image.fromarray(np.uint8(img_array)).convert('RGB')
        self.shift = 1
        img = ''

        p = random.randint(0, 100)
        if p < 10 and self.thunder:
            img = Image.new('RGB', (self.screen_width, self.screen_height))
            img.paste((255, 255, 255), [0, 0, self.screen_width, self.screen_height])
            return img
        elif self.rain:
            img_array = np.asarray(self.image)

            img = Image.fromarray(np.uint8(img_array)).convert('RGB')

            img_array = np.roll(img_array, int(self.shift * self.intensity), axis=0)
            img_array[self.screen_height - 1] = self.background_color

            # img_array = np.pad(img_array, ((0,15),(63,15)), mode='constant')
            self.image = Image.fromarray(np.uint8(img_array)).convert('RGB')

            for x in range(self.screen_width):
                p = random.randint(0, 100)
                if p < 1:
                    y2 = random.randint(1, 3)

                    draw = ImageDraw.Draw(self.image)
                    draw.line((x, 0, x, y2), fill=(120, 120, 120))
        elif self.snow:
            img = Image.new('RGB', (self.screen_width, self.screen_height))
            for x in range(self.screen_width):
                for y in range(self.screen_height):
                    p = random.randint(0, 100)
                    if p < 2 * self.intensity:
                        img.putpixel((x,y), (255,255,255))


        return img


# class StrobeBackground(FillBackground):
#     def __init__(self, strobe_delay=5, color_strobe=False):
#         super(StrobeBackground, self).__init__()
#
#         self.__strobe_speed = strobe_delay #clk pulses per strobe
#         self.__color_strobe = color_strobe
#         super(StrobeBackground, self).change_background(0.5)
#
#     def __str__(self):
#      return 'Strobe Background Object'
#
#     # fix this
#     def get_background(self, clk):
#         if self.__color_strobe:
#             super(StrobeBackground, self).change_background(1)
#
#
#         img = Image.new('RGB', (self.screen_width, self.screen_height))
#
#         # print(math.floor(clk / self.__strobe_speed) % 2, clk)
#         if math.floor(clk / self.__strobe_speed) % 2:
#             img.paste(self.background_color, [0,0, self.screen_width,self.screen_height])
#             return img
#         else:
#             # img = img.paste((0,0,0), [0,0, self.screen_width,self.screen_height])
#             # print(img, 'here')
#             return img
#
#     def change_speed(self, delta):
#         if not self.static:
#             self.__strobe_speed = max(min(self.__strobe_speed + delta, 10), 1) #min 1 bc divide by zero error
#
#     def modifier(self):
#         self.__color_strobe = not self.__color_strobe


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
        self.__font = ImageFont.load('/usr/share/fonts/bitmap/proggy/ProggyCleanSZ.pil')
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
