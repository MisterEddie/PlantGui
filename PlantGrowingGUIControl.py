#! /usr/bin/env python
from Tkinter import Tk, Scale, Label, Button, Entry, IntVar, END, W, E, Frame, HORIZONTAL
#change to Tkinter and run python2 for pi

import datetime
import time
start_time = datetime.datetime.now()

import csv

import LM75
sensor = LM75.LM75()

#brown-ground
#orange - bcm 18
#striped orange bcm 23
#blue - bcm 25
#striped blue - bcm 8
#striped brown - bcm 1
import RPi.GPIO as GPIO
freq_LDD = 800 #100-1khz
freq_LDH = 2000 #1khz-10khz
pin_ir = 18
pin_uv = 23
pin_b = 25
pin_w = 8
pin_r = 1
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_ir, GPIO.OUT)
GPIO.setup(pin_uv, GPIO.OUT)
GPIO.setup(pin_b, GPIO.OUT)
GPIO.setup(pin_w, GPIO.OUT)
GPIO.setup(pin_r, GPIO.OUT)
pwm_ir = GPIO.PWM(pin_ir, freq_LDD)
pwm_uv = GPIO.PWM(pin_uv, freq_LDD)
pwm_b = GPIO.PWM(pin_b, freq_LDH)
pwm_w = GPIO.PWM(pin_w, freq_LDH)
pwm_r = GPIO.PWM(pin_r, freq_LDH)
pwm_ir.start(0)
pwm_uv.start(0)
pwm_b.start(0)
pwm_w.start(0)
pwm_r.start(0)

class AVA:
    def __init__(self,master):
        self.master=master
        master.title("PWMAVA")

        frame=Frame(master)
        frame.grid(row=0, column=0)

        #current status
        self.time_label = Label(frame)
        self.temp_label = Label(frame)
        self.elapsed_label = Label(frame)

        #current pwm values
        self.white_pwm = 0
        self.blue_pwm = 0
        self.red_pwm = 0
        self.uv_pwm = 0
        self.ir_pwm = 0
        self.entered_pwm = 0

        self.white_pwm_label_text = IntVar()
        self.white_pwm_label_text.set(self.white_pwm)
        self.blue_pwm_label_text = IntVar()
        self.blue_pwm_label_text.set(self.blue_pwm)
        self.red_pwm_label_text = IntVar()
        self.red_pwm_label_text.set(self.red_pwm)
        self.uv_pwm_label_text = IntVar()
        self.uv_pwm_label_text.set(self.uv_pwm)
        self.ir_pwm_label_text = IntVar()
        self.ir_pwm_label_text.set(self.ir_pwm)

        #adjustable pwm labels
        self.white_pwm_label = Label(master, textvariable=self.white_pwm_label_text)
        self.blue_pwm_label = Label(master, textvariable=self.blue_pwm_label_text)
        self.red_pwm_label = Label(master, textvariable=self.red_pwm_label_text)
        self.uv_pwm_label = Label(master, textvariable=self.uv_pwm_label_text)
        self.ir_pwm_label = Label(master, textvariable=self.ir_pwm_label_text)

        #static labels
        self.white_label = Label(master, text = "Current White PWM:")
        self.blue_label = Label(master, text= "Current Blue PWM:")
        self.red_label = Label(master, text= "Current Red PWM:")
        self.uv_label = Label(master, text= "Current UV PWM:")
        self.ir_label = Label(master, text= "Current IR PWM:")

        #validation
        vcmd = master.register(self.validate)
        self.entry = Entry(master, validate="key", validatecommand=(vcmd, '%P'))

        #buttons
        self.enter_white_button = Button(master, text="Enter White PWM", command=lambda: self.update("white"))
        self.enter_blue_button = Button(master, text="Enter Blue PWM", command=lambda: self.update("blue"))
        self.enter_red_button = Button(master, text="Enter Red PWM", command=lambda: self.update("red"))
        self.enter_uv_button = Button(master, text="Enter UV PWM", command=lambda: self.update("uv"))
        self.enter_ir_button = Button(master, text="Enter IR PWM", command=lambda: self.update("ir"))
        self.reset_button = Button(master, text="Turn Off All", command=lambda: self.update("reset"))

        #layouts
        self.time_label.grid(row=0, column=0)
        self.elapsed_label.grid(row=0, column=1)
        self.temp_label.grid(row=0, column=2)

        self.white_label.grid(row=1, column=0, sticky=W)
        self.blue_label.grid(row=2, column=0, sticky=W)
        self.red_label.grid(row=3, column=0, sticky=W)
        self.uv_label.grid(row=4, column=0, sticky=W)
        self.ir_label.grid(row=5, column=0, sticky=W)
        self.white_pwm_label.grid(row=1, column =1, columnspan=1, sticky=E)
        self.blue_pwm_label.grid(row=2, column=1, columnspan=1, sticky=E)
        self.red_pwm_label.grid(row=3, column=1, columnspan=1, sticky=E)
        self.uv_pwm_label.grid(row=4, column=1, columnspan=1, sticky=E)
        self.ir_pwm_label.grid(row=5,column=1, columnspan=1, sticky=E)

        self.entry.grid(row=6, column=0,columnspan=3,sticky=W+E) #entry bar
        self.enter_white_button.grid(row=7, column=0, sticky=W+E)
        self.enter_blue_button.grid(row=8, column=0, sticky=W+E)
        self.enter_red_button.grid(row=9, column=0, sticky=W+E)
        self.enter_uv_button.grid(row=10, column=0, sticky=W+E)
        self.enter_ir_button.grid(row=11, column=0, sticky=W+E)
        self.reset_button.grid(row=12, column=0, sticky=W+E)

        self.timer_interval = 500 #500ms
        self.log_count = 2 #take log every second

        with open("LoggingData/log" + start_time.strftime("%m%d%Y-%H%M%S") + ".csv", mode = "w") as log_file:
            ava_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            ava_writer.writerow(["Date", "Time", "Temperature", "WHITEPWM", "BLUEPWM", "REDPWM", "UVPWM", "IRPWM"])

        self.stat_update()

    def validate(self, new_text):
        if not new_text:
            self.entered_pwm = 0
            return True
        try:
            if int(new_text) < 0:
                return False
            if int(new_text) > 100:
                return False
            self.entered_pwm = int(new_text)
            return True
        except ValueError:
            return False

    def update(self, method):
        if method == "white":
            self.white_pwm = self.entered_pwm
            print("Pwm will now change for white!")
        if method == "blue":
            self.blue_pwm = self.entered_pwm
            print("Pwm will now change for blue!")
        if method == "red":
            self.red_pwm = self.entered_pwm
            print("Pwm will now change for red!")
        if method == "uv":
            self.uv_pwm = self.entered_pwm
            print("Pwm will now change for uv!")
        if method == "ir":
            self.ir_pwm = self.entered_pwm
            print("Pwm will now change for ir!")
        elif method == "reset":
            self.blue_pwm = self.entered_pwm
            self.white_pwm = self.entered_pwm
            self.red_pwm = self.entered_pwm
            self.uv_pwm = self.entered_pwm
            self.ir_pwm = self.entered_pwm
            print("Turn off!")

        self.white_pwm_label_text.set(self.white_pwm)
        self.blue_pwm_label_text.set(self.blue_pwm)
        self.red_pwm_label_text.set(self.red_pwm)
        self.uv_pwm_label_text.set(self.uv_pwm)
        self.ir_pwm_label_text.set(self.ir_pwm)
        self.entry.delete(0, END)

    def log_data(self, date,time,temperature,white,blue,red,uv,ir):
        with open("LoggingData/log" + start_time.strftime("%m%d%Y-%H%M%S") + ".csv", mode = "a") as log_file:
            ava_writer = csv.writer(log_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            ava_writer.writerow([date, time, temperature, white, blue, red, uv, ir])

    def change_pwm(self, white_duty, blue_duty, red_duty, uv_duty, ir_duty, check_temp):
        if check_temp > 82:
            pwm_w.ChangeDutyCycle(0)
            pwm_b.ChangeDutyCycle(0)
            pwm_r.ChangeDutyCycle(0)
            pwm_uv.ChangeDutyCycle(0)
            pwm_ir.ChangeDutyCycle(0)

        else:
            pwm_w.ChangeDutyCycle(white_duty)
            pwm_b.ChangeDutyCycle(blue_duty)
            pwm_r.ChangeDutyCycle(red_duty)
            pwm_uv.ChangeDutyCycle(uv_duty)
            pwm_ir.ChangeDutyCycle(ir_duty)

    def stat_update(self):
        time = datetime.datetime.now()
        time_label = time.strftime("Time: %H:%M:%S")
        elapsed_time = str(time - start_time)
	temperature = (sensor.getTemp()-32.0)*5/9
        temperature_label = "Temperature: " +  str(temperature)

        self.time_label.config(text = time_label)
        self.elapsed_label.config(text = "Elapsed Time: " + elapsed_time[:10])
        self.temp_label.config(text = temperature_label)

        self.change_pwm(self.white_pwm, self.blue_pwm, self.red_pwm, self.uv_pwm, self.ir_pwm, temperature)

        if (self.log_count > 2) :
            self.log_data(time.strftime("%m-%d-%Y"),time.strftime("%H:%M:%S"),temperature,self.white_pwm, self.blue_pwm, self.red_pwm, self.uv_pwm, self.ir_pwm)
            self.log_count = 0
        self.log_count = self.log_count + 1

        self.master.after(self.timer_interval, self.stat_update)


root = Tk()
my_gui = AVA(root)
root.mainloop()
