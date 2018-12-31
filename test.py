# # DriverAdaMatrix provides a driver plugin for use with BiblioPixel: https://github.com/ManiacalLabs/BiblioPixel
# # BiblioPixel is a write once, run on anything interface for LED animations on just about any hardware
# # Install with "pip install bibliopixel" or download from GitHub
# # Due to the Adafruit_RGBmatrix requirement, this code will only run on the Raspberry Pi

import time
# from rgbmatrix import Adafruit_RGBmatrix
import rgbmatrix

from bibliopixel.drivers.driver_base import *
from RGBMatrixBase import RGBMatrixBase

class DriverAdaMatrix(DriverBase):
    # rows: height of the matrix, same as led-matrix example
    # chain: number of LEDMatrix panels, same as led-matrix example
    def __init__(self, rows = 32, chain = 1):
        super(DriverAdaMatrix, self).__init__(rows*32*chain)
        self.RGB_base = RGBMatrixBase()

        self._matrix = self.RGB_base.matrix #Adafruit_RGBmatrix(rows, chain)

    #Push new data to strand
    def update(self, data):
        self._matrix.SetBuffer(data)

    #Matrix supports between 2^1 and 2^11 levels of PWM
    #which translates to the total color bit-depth possible
    #A lower value will take up less CPU cycles
    # def SetPWMBits(self, bits):
    #     if bits < 1 or bits > 11:
    #         raise ValueError("PWM level must be between 1 and 11")
    #     self._matrix.SetPWMBits(bits)


# # #Usage is as follows:
# # #See the Wiki for more details: https://github.com/ManiacalLabs/BiblioPixel/wiki

# from bibliopixel import *
# import bibliopixel.colors as colors
# from bibliopixel.animation import *

driver = DriverAdaMatrix(rows=16, chain=2)
# # driver.SetPWMBits(6) #decrease bit-depth for better performance
# #MUST use serpentine=False because rgbmatrix handles the data that way
led = Matrix(driver, 16, 32, serpentine=False)

# #Must have code downloaded from GitHub for matrix_animations
# # from matrix_animations import *
# # import bibliopixel.log as log
# # log.setLogLevel(log.DEBUG)

# #load matrix calibration test animation
# from bibliopixel.animation import MatrixCalibrationTest
# anim = MatrixCalibrationTest(led)

# try:
#     #run the animation
#     anim.run()
# except KeyboardInterrupt:
#     #Ctrl+C will exit the animation and turn the LEDs offs
#     led.all_off()
#     led.update()

from bibliopixel.layout import *
from bibliopixel.animation import MatrixCalibrationTest
from bibliopixel.drivers.SPI.LPD8806 import *
from bibliopixel.layout import Rotation

#create driver for a 12x12 grid, use the size of your display
driver = LPD8806(12*12)
led = Matrix(driver)

anim = MatrixCalibrationTest(led)
anim.run()