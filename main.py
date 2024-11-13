from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

firmware_url = "https://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@raw.githubusercontent.com/kmml1/pico_ota/master/"

ota_updater = OTAUpdater(firmware_url, "main.py")

ota_updater.download_and_install_update_if_available()


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


print(set_pwm(pwm2, 8, 0.5))


