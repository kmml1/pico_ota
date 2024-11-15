import network
import socket
import time
import random
from machine import Pin


class Server:
    def __init__(self):
        # Set up socket and start listening
        self.addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(self.addr)
        self.s.listen()
        self.led = Pin('LED', Pin.OUT)
        self.state = "OFF"
        self.random_value = 0

    def webpage(self, random_value, state):
        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Zwieraczka</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Zwieraczka v0.1</h1>
                
                <h2>Led Control</h2>
                <form action="./lighton">
                    <input type="submit" value="Light on" />
                </form>
                <br>
                <form action="./lightoff">
                    <input type="submit" value="Light off" />
                </form>
                
                
                <form action="./start_pwm" method="get">
                    <label for="number">Frequency in kHz:</label>
                    <input type="number" id="freq" name="freq" required>
                    <br>
                    <label for="number">Duty <0,1>:</label>
                    <input type="number" id="duty" name="duty" required>
                    <br>
                    <label for="number">Time (0 is infinity):</label>
                    <input type="number" id="time" name="time" required>
                    <br>
                    <input type="submit" value="Start PWM">
                </form>
                
                <form action="./stop_pwm" method="get">
                    <input type="submit" value="Stop PWM" />
                </form>
                
                <p>LED state: {state}</p>
            </body>
            </html>
            """
        return str(html)

    def start(self):
        print('Listening on', self.addr)
        global set_pwm
        global pwm2
        while True:
            try:
                conn, addr = self.s.accept()
                print('Got a connection from', addr)

                # Receive and parse the request
                request = conn.recv(1024)
                request = str(request)
                print('Request content = %s' % request)

                try:
                    request = request.split()[1]
                    print('Request:', request)
                except IndexError:
                    pass

                # Process the request and update variables
                if request == '/lighton?':
                    print("LED on")
                    self.led.value(1)
                    self.state = "ON"
                elif request == '/lightoff?':
                    self.led.value(0)
                    self.state = 'OFF'
                elif request == '/start_pwm?':
                    print(set_pwm(pwm2, 30000, 0.5))
                elif request == '/stop_pwm?':
                    print(set_pwm(pwm2, 30000, 0))

                # Generate HTML response
                response = self.webpage(self.random_value, self.state)

                # Send the HTTP response and close the connection
                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                conn.send(response)
                conn.close()

            except OSError as e:
                conn.close()
                print('Connection closed')
