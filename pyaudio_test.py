import pyaudio

screen_height = 16
screen_width = 64
delta_t = 0.1
clk = 0

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = int(RATE / (1 / delta_t))# 2048 # RATE / number of updates per second
RECORD_SECONDS = 20

pa = pyaudio.PyAudio()

	
print('opening stream')
stream = pa.open(
	format=pyaudio.paInt16,
	channels=1,
	input_device_index = 4,
	rate=RATE,
	input=True,
	frames_per_buffer=CHUNK)
#stream = pa.open(
#        format = pyaudio.paInt16,
#        channels = 1,
#        rate = 44100,
#        input_device_index = 4, # this needs to be tested
#        input = True,
#	frames_per_buffer=CHUNK)
print('stream opened')
