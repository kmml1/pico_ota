from ota import OTAUpdater
import network
from time import sleep

nic = None
ip = None


def connect_wifi(ssid, password):
    global nic
    if ssid is None and password is None:
        print('No network credentials provided')
        return None
    nic = network.WLAN(network.STA_IF)
    nic.active(True)
    nic.connect(ssid, password)
    while not nic.isconnected():
        print('.', end="")
        sleep(0.25)
    ip = nic.ifconfig()[0]
    print(f'Connected to WiFi, IP is: {ip}')


def connect_lan():
    global nic
    global ip
    spi = machine.SPI(0, 2_000_000, mosi=machine.Pin(19), miso=machine.Pin(16), sck=machine.Pin(18))
    nic = network.WIZNET5K(spi, machine.Pin(17), machine.Pin(20))
    nic.active(True)
    while not nic.isconnected():
        print('.', end="")
        sleep(0.25)
    ip = nic.ifconfig()[0]
    print(f'Connected to LAN, IP is: {ip}')


firmware_url = "https://raw.githubusercontent.com/kmml1/pico_ota/master/"
ota_updater = OTAUpdater(firmware_url, "main.py")

# ota_updater.download_and_install_update_if_available()

pwm2 = machine.PWM(machine.Pin(9))

def set_pwm(pwm: machine.PWM, freq: int, duty: float):
    if duty < 0 or duty > 1:
        return "Duty must be between 0 and 1"
    if freq < 8:
        return "Frequency must at least 8Hz"
    # all duty values in us
    OSCILATION_TIME = 3 # oscillation time is 3 us, doubled for better square signa;
    duty_cycle_us = 1_000_000.0 / freq
    duty_us = duty * duty_cycle_us
    if duty_us < OSCILATION_TIME or duty_cycle_us - duty_us < OSCILATION_TIME:
        return f"Either low or high pulse must be at least {OSCILATION_TIME}us long, requested duty {duty_us}us"
    try:
        pwm.duty_ns(0)
        pwm.freq(freq)
        pwm.duty_ns(int(1_000 * duty_us))
    except Exception as e:
        return e


print(set_pwm(pwm2, 8, 0.9))
