from datetime import datetime as DateTime, time as Time
import threading
import time

class TimeControl():
    def __init__(self, time_list, callback_func):
        self.time_list = time_list
        self.on_event = callback_func
        self.state = [False for _ in range(len(time_list))]

    def timestr_to_min(self, string):
        values = string.split(':')
        min = 60*int(values[0])+int(values[1])

        return min
    
    def diff_in_min(self, t_1, t_2):
        diff = t_2 - t_1
        if diff < 0:
            diff = 60*24 + diff
        return diff

    def get_time_data(self):

        time_data = [
            (name, pins, self.timestr_to_min(start), self.timestr_to_min(end))
            for name, pins, (start, end) in self.time_list
        ]

        return time_data

    def check_time_threshold(self, time_now, begin_time, end_time):
        on_time = False
        if (self.diff_in_min(time_now, end_time) <= self.diff_in_min(begin_time, end_time))and (self.diff_in_min(time_now, end_time) != 0):
            on_time = True
        
        return on_time

    def check_time(self):
        while True:
            time.sleep(0.1)
            for i, (name, pin, begin_time, end_time) in enumerate(self.get_time_data()):
                state_change = self.check_time_threshold(self.timestr_to_min(str(DateTime.now().time())),begin_time, end_time)
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

    time_list = [('led_1', [0, 1, 2, 3], ('23:00', '01:00'))]
    t_control = TimeControl(time_list=time_list, callback_func=callback)
    t_control.start_timer()
    while True:
        time.sleep(0.1)

