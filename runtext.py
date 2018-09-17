#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import requests
from datetime import datetime
import time


api_key = 'cc01eeec160945bb92713eacb27b7548'
fmt = '%Y-%m-%dT%H:%M:%S'
url = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?key=cc01eeec160945bb92713eacb27b7548&mapid=40660&outputType=JSON&max=2'


#get all stops near you, claculate closest L times by inclusind walking distance from google earth api
class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        font = graphics.Font()
        font.LoadFont("../../../fonts/7x13.bdf")
        textColor = graphics.Color(255, 128, 128)

        while True:
            curr_msg = 'here'

            # arrivals = self.get_trains()
            arrivals = [1,1,1,1]
            for train in arrivals:
                # pos = offscreen_canvas.width
                text = 'Kimball'#train['dest']
                text_length = 7 * (len(text))
                stop_x = int((text_length + 64) / 2) # 64 - (64 - text_length) / 2

                self.blank_screen(0.5, offscreen_canvas, font)
                self.scroll_text_to(text, 1 / 70, stop_x, offscreen_canvas.width, offscreen_canvas, font, textColor, 1)


                text = '10 min'
                text_length = 7 * (len(text))
                stop_x = int((text_length + 64) / 2)

                self.blank_screen(0.5, offscreen_canvas, font)
                self.flash_text(stop_x - text_length, text, textColor, 2, offscreen_canvas, font)






# TODO
# calculate walking distance via gps and make trains that are within walking distance be a special alert
#have this scroll in with the text for the arrival time be in the upper right corner when it is close by, or have a guy that is walking, like a walkable checkmark
# TODO main loop should look like



    #right side of screen is text.RHS_x = 64, left side is where text.RHS_x = 0
    #this is represented by pos for now

    def scroll_text_to(self, text, delta_t, stop_location, start_location, offscreen_canvas, font, textColor, delay):
        # text = 'A'

        RHS = 64#start_location

        while True:
            offscreen_canvas.Clear()

            # this is the length of the printed text
            l = graphics.DrawText(offscreen_canvas, font, RHS, 10, textColor, text)
            # print(len)
            # len = 32
            # print(pos, pos + len)
            # print(l)

            # 28 comes from some weird value l in drawtext
            RHS -= 1
            if (RHS + l < stop_location):
                print(RHS, RHS+l)
                time.sleep(delay) # make this based on transition time
                # print('BREAKING')
                # offscreen_canvas.Clear()
                break

            time.sleep(delta_t) # this is speed in ticks per second
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    def flash_text(self, RHS, text, textColor, dur, offscreen_canvas, font):
        offscreen_canvas.Clear()
        # print(RHS)
        # this is the length of the printed text
        graphics.DrawText(offscreen_canvas, font, RHS, 10, textColor, text)

        time.sleep(dur)
        offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)

    def blank_screen(self, dur, offscreen_canvas, font):
        self.flash_text(0, '', graphics.Color(0,0,0), dur, offscreen_canvas, font)



    def get_trains(self):
        r = requests.get(url).json()['ctatt']['eta']

        arrivals = []

        for eta in r:
            arr = {}
            if eta['trDr'] == '5':
                arr['dest'] = 'Loop'
            elif eta['trDr'] == '1':
                arr['dest'] = 'Kimball'
            else:
                pass

            d1 = datetime.strptime(eta['prdt'], fmt)
            d2 = datetime.strptime(eta['arrT'], fmt)

            # Convert to Unix timestamp
            d1_ts = time.mktime(d1.timetuple())
            d2_ts = time.mktime(d2.timetuple())

            # They are now in seconds, subtract and then divide by 60 to get minutes.
            if eta['isApp'] == '1':
                arr['is_app'] = True
            else:
                arr['is_app'] = False

            arr['arr_t'] = str(int((d2_ts - d1_ts) / 60))

            arrivals.append(arr)

        return arrivals







# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
