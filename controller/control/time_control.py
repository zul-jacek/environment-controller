from datetime import datetime as DateTime, time as Time
import threading
import time

class TimeControl():
    def __init__(self, time_list, callback_func):
        self.time_list = time_list
        self.on_event = callback_func
        self.state = [False for _ in range(len(time_list))]

    def str_to_time(self, string):
        return Time(*map(int, string.split(':')))

    def get_time_data(self):

        time_data = [
            (name, pins, self.str_to_time(start), self.str_to_time(end))
            for name, pins, (start, end) in self.time_list
        ]

        return time_data

    def check_time_threshold(self, time_now, time_1, time_2):
        if time_1 > time_2:
            raise ValueError('begin must not be greater than end')
        return time_1 <= time_now < time_2

    def check_time(self):
        while True:
            time.sleep(0.1)
            # print("check")
            for i, (name, pin, begin_time, end_time) in enumerate(self.get_time_data()):
                state_change = t_control.check_time_threshold(DateTime.now().time(),begin_time, end_time)
                if (state_change == True) and (self.state[i] == False):
                    self.state[i] = True
                    self.on_event(name, pin, True)
                if (state_change == False) and (self.state[i] == True):
                    self.state[i] = False
                    self.on_event(name, pin, False)

    def start_timer(self):
        check_time_thread = threading.Thread(target=self.check_time, daemon=True)
        check_time_thread.start()

if __name__ == '__main__':
    def callback(name, pin, state):
        print(name, pin, state)

    time_list = [('led_1', [0, 1, 2, 3], ('23:50', '23:51'))]
    t_control = TimeControl(time_list=time_list, callback_func=callback)
    t_control.start_timer()
    while True:
        time.sleep(0.1)

