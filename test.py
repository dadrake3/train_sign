# DriverAdaMatrix provides a driver plugin for use with BiblioPixel: https://github.com/ManiacalLabs/BiblioPixel
# BiblioPixel is a write once, run on anything interface for LED animations on just about any hardware
# Install with "pip install bibliopixel" or download from GitHub
# Due to the Adafruit_RGBmatrix requirement, this code will only run on the Raspberry Pi

import time
# from rgbmatrix import Adafruit_RGBmatrix
import argparse
from bibliopixel.drivers.driver_base import *
from rgbmatrix import RGBMatrix, RGBMatrixOptions



class DriverAdaMatrix(DriverBase):
    # rows: height of the matrix, same as led-matrix example
    # chain: number of LEDMatrix panels, same as led-matrix example
    def __init__(self, rows = 16, chain = 2):
        super(DriverAdaMatrix, self).__init__(rows*32*chain)

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 1..100. Default: 1", choices=range(3), type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels", default=0, type=int, choices=[0,1])
        self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral (Default: 0)", default=0, type=int, choices=[0,1,2,3])


        self.args = self.parser.parse_args()

        self.options = RGBMatrixOptions()

        if self.args.led_gpio_mapping != None:
          self.options.hardware_mapping = self.args.led_gpio_mapping
        self.options.rows = self.args.led_rows
        self.options.cols = self.args.led_cols
        self.options.chain_length = self.args.led_chain
        self.options.parallel = self.args.led_parallel
        self.options.row_address_type = self.args.led_row_addr_type
        self.options.multiplexing = self.args.led_multiplexing
        self.options.pwm_bits = self.args.led_pwm_bits
        self.options.brightness = self.args.led_brightness
        self.options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        self.options.led_rgb_sequence = self.args.led_rgb_sequence
        if self.args.led_show_refresh:
            self.options.show_refresh_rate = 1

        if self.args.led_slowdown_gpio != None:
            self.options.gpio_slowdown = self.args.led_slowdown_gpio
        if self.args.led_no_hardware_pulse:
            self.options.disable_hardware_pulsing = True

        self._matrix = RGBMatrix(options = self.options)

        # self._matrix = Adafruit_RGBmatrix(rows, chain)

    #Push new data to strand
    def update(self, data):
        # self._matrix.SetBuffer(data)
        print(data)
        self._matrix.SetImage(data, 0, 0)

    #Matrix supports between 2^1 and 2^11 levels of PWM
    #which translates to the total color bit-depth possible
    #A lower value will take up less CPU cycles
    def SetPWMBits(self, bits):
        if bits < 1 or bits > 11:
            raise ValueError("PWM level must be between 1 and 11")
        # self._matrix.SetPWMBits(bits)

        self.options.pwm_bits = bits
        self._matrix = RGBMatrix(options = self.options)

        
        

from bibliopixel.layout import *
from bibliopixel.animation import MatrixCalibrationTest
from bibliopixel.drivers.SPI.LPD8806 import *
from bibliopixel.layout import Rotation


#create driver for a 12x12 grid, use the size of your display
driver = DriverAdaMatrix()
led = Matrix(driver)

anim = MatrixCalibrationTest(led)

anim.run()







