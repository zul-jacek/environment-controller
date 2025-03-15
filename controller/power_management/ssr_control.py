import sys
import smbus
import time

DEVICE_ADDRESS = 0x27
IODIRA = 0x00 # Pin Register for direction
IODIRB = 0x01 # Pin Register for direction
GPIOA = 0x12 # Register for Input (GPA)
GPIOB = 0x13 # Register for Input (GPB)
GPPUA = 0x0C # Register for Internal Pull-up-Resistors GPA
GPPUB = 0x0D # Register for Internal Pull-up-Resistors GPB

class SsrControl():
    def __init__(self, port=None):
        self.bus = smbus.SMBus(1)    # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
        self.bus.write_byte_data(DEVICE_ADDRESS,IODIRB,0x00)
    
    def crt_str_to_int(self, control_str, int_val=0):
        for i, state in enumerate(control_str):
            if state not in ["1", "0", "x", "t"] or len(control_str) != 3:
                raise ValueError("not valid command")
            if state == "1":
                int_val = (int_val | 1 << i)
            if state == "0":
                int_val = (int_val & ~(1 << i))
            if state == "x":
                pass
            if state == "t":
                int_val = (int_val ^ 1 << i)
        return int_val

    def int_to_crt_str(self, int_val, digit_len=3):
        bin_val = bin(int_val)
        str_val = ""
        for i in range(digit_len):
            if bin_val[-(i+1)] == "1":
                str_val += "1"
            else:
                str_val += "0"

        return str_val

    def set_relais_by_int(self, int_val):
        self.bus.write_byte_data(DEVICE_ADDRESS,GPIOB,int_val)

    def get_relais_state_as_int(self):

        return self.bus.read_byte_data(DEVICE_ADDRESS,GPIOB)

    def set_relais(self, command):
        not_execute = True
        count = 0
        while (count < 3) and not_execute:
            try:
                count += 1
                actual_val = self.get_relais_state_as_int()
                int_val = self.crt_str_to_int(command, actual_val)
                self.set_relais_by_int(int_val)
                not_execute = False
            except Exception as e:
                print(f"retry set relays \n {e}")
                time.sleep(1.1)
        if not_execute:
            raise SystemError("relay can not set!")

    def get_relais_state(self):
        not_execute = True
        count = 0
        while (count < 3) and not_execute:
            try:
                count += 1
                state = self.int_to_crt_str(self.get_relais_state_as_int())
                not_execute = False
            except Exception as e:
                print(f"retry read dat \n {e}")
                time.sleep(1.1)
        if not_execute:
            raise SystemError("can not read relay data!")
        
        return state

if __name__ == '__main__':
    cmd_arg = sys.argv
    if (len(cmd_arg) ==2) and (len(cmd_arg[1]) == 3):
        ssr_control = SsrControl()
        if cmd_arg[1] == "get":
            print(ssr_control.get_relais_state())
        else:
            ssr_control.set_relais(cmd_arg[1])
    else:
        print("to many agrs!")