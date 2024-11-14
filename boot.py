from ota import OTAUpdater
import network
import time

nic = None
ip = None

status_led = machine.PWM(machine.Pin(25))
status_led.freq(8)
status_led.duty_u16(25000)


def connect_lan():
    global nic
    global ip
    spi = machine.SPI(0, 2_000_000, mosi=machine.Pin(19), miso=machine.Pin(16), sck=machine.Pin(18))
    nic = network.WIZNET5K(spi, machine.Pin(17), machine.Pin(20))
    nic.active(True)
    start_time = time.time()
    while not nic.isconnected() and time.time() - start_time < 30:
        print('.', end="")
        time.sleep(0.25)
    ip = nic.ifconfig()[0]
    print(f'Connected to LAN, IP is: {ip}')


connect_lan()

ota_updater = OTAUpdater("https://raw.githubusercontent.com/kmml1/pico_ota/master/")
updated = 0
updated += int(ota_updater.update("ota.py"))
updated += int(ota_updater.update("main.py"))
if updated:
    status_led.duty_u16(0)
    print('Restarting device...')
    machine.reset()

status_led.duty_u16(70000)




