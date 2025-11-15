import time
import threading
import math
from pathlib import Path
import json
from datetime import datetime
import matplotlib.pyplot as plt



TARGET_ABS_HUM = 10.0
CYCLE_TIME = 0.5
PARAM_FILE = Path("adaptive_params.json")

class PidController:
    """control base class"""

    def __init__(self, input, relays):
        self.input_data = input
        self.relays = relays
        self.stop_event = threading.Event()
        self.pid_controller_thread = threading.Thread(target=self.pid_control, daemon=True)
        self.autotune = False
        self.logging = False

    def start_thread(self):
        self.pid_controller_thread.start()

    def stop_thread(self):
        self.stop_event.set()
        self.pid_controller_thread.join()

    def load_params(self):
        if PARAM_FILE.exists():
            return json.loads(PARAM_FILE.read_text())
        else:
            params = {"kp": 150, "ki": 0, "kd": 0}

            return params

    def save_params(self, params):
        PARAM_FILE.write_text(json.dumps(params, indent=2))

    def adaptive_update(self, params, error, d_error):
        adapt_rate = 0.1
        overshoot_threshold = 1

        if abs(error) > 0.5:
            params["kp"] += adapt_rate * abs(error)
        if abs(d_error) > overshoot_threshold:
            params["kp"] *= (1 - adapt_rate)
            params["kd"] += adapt_rate * 0.5
        params["ki"] += 0.001 * (1 if abs(error) > 0.2 else -1)

        # Begrenzen
        params["kp"] = max(0.1, min(params["kp"], 180.0))
        params["ki"] = max(0.001, min(params["ki"], 2.0))
        params["kd"] = max(0.0, min(params["kd"], 5.0))
        print(params)
        return params

    def pid_control(self):
        params = self.load_params()
        integral = 0.0
        last_error = 0.0
        start_fan_time = time.time()
        start_sys_time = time.time()
        self.log_t, self.log_h, self.log_T, self.log_abs, self.log_fan, self.log_hum = [], [], [], [], [], []
        while not self.stop_event.is_set():

            error = TARGET_ABS_HUM - self.input_data.data_list[3]
            d_error = error - last_error
            integral += error * CYCLE_TIME

            # PID-Ausgang
            u = params["kp"] * error + params["ki"] * integral + params["kd"] * d_error

            now = time.time()
            fan_on_time = now - start_fan_time
            out = max(-1, min(u, 1))
            if out < 0:
                start_fan_time = now
                self.relays.set_relais("1xx")
                self.relays.set_relais("x0x")
            elif out > 0:
                self.relays.set_relais("x1x")
                if fan_on_time >= 10:
                    self.relays.set_relais("0xx")

            # Adaptive Parameteranpassung
            if self.autotune:
                params = self.adaptive_update(params, error, d_error)
                self.save_params(params)

            # Logging
            if self.logging:
                t = str(time.time() - start_sys_time)
                temp = self.input_data.data_list[1]
                humidity = self.input_data.data_list[2]
                abs_h =  self.input_data.data_list[3]
                fan_on =  int(self.input_data.data_list[4][0])
                humidifier_on = int(self.input_data.data_list[4][1])
                self.log_t.append(t)
                self.log_T.append(temp)
                self.log_h.append(humidity)
                self.log_abs.append(abs_h)
                self.log_fan.append(1 if fan_on else 0)
                self.log_hum.append(1 if humidifier_on else 0)

                print(
                    f"t={t} | T={temp:4.1f}°C | RH={humidity:5.1f}% | abs={abs_h:5.2f} g/m³ "
                    f"| err={error:+5.2f} | u={u:+.2f} | Fan={'ON' if fan_on else 'off'} | Hum={'ON' if humidifier_on else 'off'}"
                )

            last_error = error
            time.sleep(CYCLE_TIME)

    def __del__(self):
        pass




if __name__ == "__main__":
    from controller.simulation.ssr_control import SsrControlSim
    from controller.simulation.sensor_data_reader import DataReaderSim

    ssr_control = SsrControlSim()
    data_reader = DataReaderSim(ssr_control)
    controler = PidController(data_reader, ssr_control)
    controler.start_thread()
    controler.logging = True
    controler.autotune = True

    counter = 0
    while counter < 180:
        #error injection
        if counter == 120:
            print("error injection")
            data_reader.humidity += 2
        time.sleep(1)
        counter += 1

    controler.stop_thread()
    # --- Plot ---
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(controler.log_t, controler.log_abs, label="Absolute Feuchte [g/m³]", color="blue")
    ax1.axhline(TARGET_ABS_HUM, color="r", linestyle="--", label="Sollwert")
    ax1.set_xlabel("Zeit [s]")
    ax1.set_ylabel("Absolute Feuchte [g/m³]")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.step(controler.log_t, controler.log_fan, color="orange", alpha=0.3, label="Lüfter an")
    ax2.step(controler.log_t, controler.log_hum, color="green", alpha=0.3, label="Befeuchter an")
    ax2.set_ylabel("Aktorenstatus (0/1)")

    fig.suptitle("Adaptive PID-Regelung auf absolute Feuchte (binäre Aktoren)")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout()
    plt.show()