#!/bin/sh
sudo python3 main.py --led-slowdown-gpio=2 --led-pwm-lsb-nanoseconds=300  --led-pwm-bits=1 --led-rows=16 --led-col=32 --led-chain=2 
