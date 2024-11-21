import network
import socket
import time
import random
import machine


class Server:
    def __init__(self, pwm):
        # Set up socket and start listening
        self.addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = socket.socket()
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(self.addr)
        self.s.listen()
        self.pwm2 = pwm

    def set_pwm(self, pwm: machine.PWM, freq: int, duty: float):
        if duty < 0 or duty > 1:
            return "Duty must be between 0 and 1"
        if freq < 8:
            return "Frequency must at least 8Hz"
        # all duty values in us
        OSCILATION_TIME = 3  # oscillation time is 3 us, doubled for better square signa;
        duty_cycle_us = 1_000_000.0 / freq
        duty_us = duty / 100 * duty_cycle_us
        if duty_us < OSCILATION_TIME or duty_cycle_us - duty_us < OSCILATION_TIME:
            return f"Either low or high pulse must be at least {OSCILATION_TIME}us long, requested duty {duty_us}us"
        try:
            pwm.duty_ns(0)
            pwm.freq(freq)
            pwm.duty_ns(int(1_000 * duty_us))
        except Exception as e:
            return e
        return ""

    def webpage(self, freq, duty, result):
        html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Zwieraczka</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                <h1>Zwieraczka v0.1</h1>
                
                <p>Frequency: {freq}Hz</p>
                <p>Duty: {duty}%</p>
                <form action="./start_pwm" method="get">
                        <input type="number" id="freq" name="freq" required>
                        <label for="number">Frequency in kHz:</label>
                    <br>
                        <input type="number" id="duty" name="duty" required>
                        <label for="number">Duty <0,1>:</label>
                    <br>
                        <input type="number" id="time" name="time">
                        <label for="number">PWM time in ms (0 or empty is infinity):</label>
                    <br>
                    <input type="submit" value="Start PWM">
                </form>
                <br>
                <form action="./stop_pwm" method="get">
                    <input type="submit" value="Stop PWM" />
                </form>
                
                <p>Result: {result}</p>
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
                request = conn.recv(1024)
                request = str(request)
                request = request.split()[1]
                print(f'Request: {request}')

                response = None

                if request.startswith('/start_pwm?'):
                    params = request.split('?')[1].split('&')
                    freq = 0
                    duty = 0
                    time = 0
                    for param in params:
                        if param.split('=')[0] == 'freq':
                            freq = int(param.split('=')[1])
                        elif param.split('=')[0] == 'duty':
                            duty = float(param.split('=')[1])
                        elif param.split('=')[0] == 'time' and len(param.split('=')) == 2:
                            time = float(param.split('=')[1])
                    response = self.webpage(freq, duty, self.set_pwm(self.pwm2, freq, duty))
                elif request.startswith('/stop_pwm'):
                    response = self.webpage(8, 0, self.set_pwm(self.pwm2, 8, 0))
                else:
                    response = self.webpage(None, None, None)

                # Send the HTTP response and close the connection
                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                conn.send(response)
                conn.close()

            except OSError as e:
                conn.close()
                print('Invalid request')
                print('Connection closed')
