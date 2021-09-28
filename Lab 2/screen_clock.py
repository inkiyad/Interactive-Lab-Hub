import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import adafruit_rgb_display.st7789 as st7789
from adafruit_rgb_display.rgb import color565
from time import strftime, sleep
from datetime import datetime

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# these setup the code for our buttons and the backlight and tell the pi to treat the GPIO pins as digitalIO vs analogIO
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90


# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Add a background image
image2 = Image.open("red.jpg")
enhancer = ImageEnhance.Brightness(image2)
image2 = enhancer.enhance(0.1)
# Scale the image2 to the smaller screen dimension
image2_ratio = image2.width / image2.height
screen_ratio = width / height
if screen_ratio < image2_ratio:
    scaled_width = image2.width * height // image2.height
    scaled_height = height
else:
    scaled_width = width
    scaled_height = image2.height * width // image2.width
image2 = image2.resize((scaled_width, scaled_height), Image.BICUBIC)
print(image2.width, image2.height)

# Crop and center the image2
x = scaled_width // 2 - width // 2
y = scaled_height // 2 - height // 2
image2 = image2.crop((x, y, x + width, y + height))

# Get drawing object to draw on image.
draw2 = ImageDraw.Draw(image2)

# Add season calendar
def season(date):

    date = date[:-6]
    month = date.split(' ')[0]
    day = int(date.split(' ')[1])

    if month in ('January', 'February', 'March'):
        season = 'Winter'
    elif month in ('April', 'May', 'June'):
        season = 'Spring'
    elif month in ('July', 'August', 'September'):
        season = 'Summer'
    else:
        season = 'Autumn'

    if (month == 'March') and (day > 19):
        season = 'Spring'
    elif (month == 'June') and (day > 20):
        season = 'Summer'
    elif (month == 'September') and (day > 21):
        season = 'Autumn'
    elif (month == 'December') and (day > 20):
        season = 'Winter'

    if season == 'Spring':
        season_day = str(abs(
            datetime.strptime('March 19', "%B %d") - datetime.strptime(date, "%B %d")
        ))
    elif season == 'Summer':
        season_day = str(abs(
            datetime.strptime('June 20', "%B %d") - datetime.strptime(date, "%B %d")
        ))
    elif season == 'Autumn':
        season_day = str(abs(
            datetime.strptime('September 21', "%B %d") - datetime.strptime(date, "%B %d")
        ))
    elif season == 'Winter':
        season_day = str(abs(
            datetime.strptime('December 20', "%B %d") - datetime.strptime(date, "%B %d")
        ))
    
    return ' '.join([season, 'Day', season_day.replace(' days, 0:00:00', '')])

k = 0
while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py
    day = strftime("%B %d, %Y")
    season_date = season(day)
    t = strftime("%I:%M:%S %p")
    if k == 0:
        T = "/" * int(t.split(':')[0])
    elif k == 1:
        T = "-" * int(t.split(':')[0])
    elif k == 2:
        T = "\\" * int(t.split(':')[0])
    elif k == 3:
        T = "|" * int(t.split(':')[0])
    elif k == 4:
        T = "/" * int(t.split(':')[0])
    elif k == 5:
        T = "-" * int(t.split(':')[0])
    elif k == 6:
        T = "\\" * int(t.split(':')[0])
    elif k == 7:
        T = "|" * int(t.split(':')[0])
    cmd = 'curl -s  wttr.in/?T | head -n7 | tail -n6'
    wttr = subprocess.check_output(cmd, shell=True).decode("utf-8")
    to_do1 = '[√] - Finish IDD Lab 2'
    to_do2 = '[] - Finish MLE assignment'
    to_do3 = '[] - Finish AML assignment'
    print(day, t, end="", flush=True)
    print("\r", end="", flush=True)

    # Write display time.

    if buttonA.value and buttonB.value:
        backlight.value = False  # turn off backlight
    else:
        backlight.value = True  # turn on backlight
    if buttonA.value and not buttonB.value:  # just button B pressed
        y = top
        draw2.text((x, y), to_do1, font=font1, fill="#00FF00")
        y += font1.getsize(to_do1)[1]
        draw2.text((x, y), to_do2, font=font1, fill="#FF0000")
        y += font1.getsize(to_do2)[1]
        draw2.text((x, y), to_do3, font=font1, fill="#FF0000")
        y += font1.getsize(to_do3)[1]
        disp.image(image2, rotation)  # show background image
    if buttonB.value and not buttonA.value:  # just button A pressed
        y = top
        draw.text((x, y), season_date, font=font1, fill="#00FF00")
        y += font1.getsize(season_date)[1]
        draw.text((x, y), T, font=font1, fill="#DFFF00")
        y += font1.getsize(T)[1]
        draw.text((x, y), wttr, font=font2, fill="#FFC300")
        y += font2.getsize(wttr)[1]
        disp.image(image, rotation)
        


    # Display image.
    k += 1
    if k > 7:
        k = 0
    time.sleep(1)
