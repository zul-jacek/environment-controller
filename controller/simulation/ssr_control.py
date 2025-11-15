class SsrControlSim:
    def __init__(self):
        self.actual_val = 0
    
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

    def get_relais_state_as_int(self):

        return self.actual_val

    def set_relais(self, command):
        self.actual_val = self.get_relais_state_as_int()
        int_val = self.crt_str_to_int(command, self.actual_val)
        self.actual_val = int_val

    def get_relais_state(self):
        state = self.int_to_crt_str(self.get_relais_state_as_int())

        return state

if __name__ == '__main__':
    ssr_control = SsrControlSim()
    print(ssr_control.get_relais_state())
    ssr_control.set_relais("010")
    print(ssr_control.get_relais_state())
    ssr_control.set_relais("xtx")
    print(ssr_control.get_relais_state())