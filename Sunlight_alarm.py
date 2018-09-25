import RPi.GPIO as GPIO
import threading
import time
from flask import Flask, render_template, request

NUMBER_OF_ALARMS = 5
TIME_ON = 3600 #seconds

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32,GPIO.OUT) ### USED TO BE 24
GPIO.setup(38,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18,GPIO.IN, pull_up_down=GPIO.PUD_UP)

app = Flask(__name__)

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   32 : {'name' : 'LED Strip', 'state' : GPIO.LOW}, ### USED TO BE 24
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)



@app.route("/")
def main():
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'pins' : pins
      }
   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)


# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
   if action == "off":
      print("Web Turning off")
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'pins' : pins
   }

   return render_template('main.html', **templateData)

#Alarm class, each individual alaram will be an instance of this
class Alarm():
    #It didnt seem to like it when the days array was initally empty
    days = ['lol','holder']
    hours = None
    minutes = None
    dailyFlag = False
    hourFlag = False
    minuteFlag = False

#Main function for alarm functionality
def LED_control():
    while True:
        dailyFlag = False
        hourFlag = False
        minuteFlag = False

        #Gets current time from system and breaks it into single chunks
        currTime = time.ctime()
        clock = currTime[11:19]
        current_hours = int(clock[0:2])
        current_minutes = int(clock[3:5])
        current_day = currTime[0:3]

        #Alarm checking logic
        for alarm in alarm_list:
            #Checking if the current day is in the alarm days
            if current_day in alarm.days:
                print("Day good")
                alarm.dailyFlag = True
            else:
                alarm.dailyFlag = False

            #Checking if the current hour is the alarm hour
            if alarm.hours == current_hours:
                print("Hour good")
                alarm.hourFlag = True
            else:
                alarm.hourFlag = False

            #Checking if the current minute is the alarm minute
            if alarm.minutes == current_minutes:
                print("Minute Good")
                alarm.minuteFlag = True
            else:
                alarm.minuteFlag = False

            #Checking if all three flags are set and activating alarm if they are
            if alarm.minuteFlag == True and alarm.hourFlag == True and alarm.dailyFlag == True:
                print("Alarm going off")

                #Actually powers the relay to turn on LED strip
                GPIO.output(32,1)

                alarm.dailyFlag = False
                alarm.hourFlag = False
                alarm.minuteFlag = False

                #This sets how long the alarm will be on for until turning off automatically
                time.sleep(TIME_ON)

            else:
                alarm.dailyFlag = False
                alarm.hourFlag = False
                alarm.minuteFlag = False

            #Added a physical on button
            if GPIO.input(38) == 0:
                GPIO.output(32,1)

            #Added a physical off button
            if GPIO.input(18) == 0:
                GPIO.output(32,0)

        time.sleep(.1)

#Creates a list of alarms
alarm_list = [Alarm() for i in range(NUMBER_OF_ALARMS)]

#Sets alarm 0 to 7:43am on weekdays
alarm_list[0].days = ["Mon", "Tue", "Wed", "Thr", "Fri"]
alarm_list[0].minutes = 43
alarm_list[0].hours = 7

#Sets alarm 1 to 9:01am on weekends
alarm_list[1].days = ["Sat", "Sun"]
alarm_list[1].minutes = 1
alarm_list[1].hours = 9

LED_instance = threading.Thread(target=LED_control, args=())
LED_instance.daemon = True
LED_instance.start()

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80, debug=True)
