# coding: utf-8
import time
import socket
import RPi.GPIO as gpio
import atexit

servopin = 18
atexit.register(gpio.cleanup)  
gpio.setmode(gpio.BCM)
gpio.setup(servopin, gpio.OUT,initial=False)
p = gpio.PWM(servopin,50) 
p.start(0)
time.sleep(0.6)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 9999))
s.listen(5)

servo_down = 3.8
servo_up = 5

def press(tms):
	p.ChangeDutyCycle(servo_down)
	time.sleep(0.02)
	p.ChangeDutyCycle(0)
	time.sleep(tms)
	p.ChangeDutyCycle(servo_up)
	time.sleep(0.02)
	p.ChangeDutyCycle(0)
	time.sleep(1)
	


if __name__ == '__main__':
	while True:
		sock, addr = s.accept()
		t = sock.recv(1024)
		t = t.decode('utf-8')
		print("press:  "+t+"ms")
		press(float(t)/1000)