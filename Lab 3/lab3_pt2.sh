#https://elinux.org/RPi_Text_to_Speech_(Speech_Synthesis)

#!/bin/bash
say() { local IFS=+;/usr/bin/mplayer -ao alsa -really-quiet -noconsolecontrols "http://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q=$*&tl=en"; }
#say $*
say "Hello, what is your name?"

#arecord -f cd -r 16000 -d 5 -t wav recorded.wav && sox recorded.wav recorded_mono.wav remix 1,2

arecord -D hw:1,0 -f cd -c1 -r 48000 -d 5 -t wav Reply.wav
python3 lab3_pt2.py