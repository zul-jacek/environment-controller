from datetime import datetime as DateTime, time as Time
import threading
import time

class TimeControl():
    def __init__(self, callback_func):
        self.time_list = []
        self.on_event = callback_func

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
        state = {}
        while True:
            time.sleep(0.1)
            for (name, pin, begin_time, end_time) in self.get_time_data():
                time_check = self.check_time_threshold(self.timestr_to_min(str(DateTime.now().time())),begin_time, end_time)
                if name not in state.keys():
                    state.update([(name, None)])
                if (time_check == True) and ((state[name] == False) or (state[name] == None)):
                    state[name] = True
                    self.on_event(name, pin, True)
                if (time_check == False) and ((state[name] == True) or (state[name] == None)):
                    state[name] = False
                    self.on_event(name, pin, False)

    def add_new_time(self, name, pin, time):
        self.time_list.append((name, pin, time))
    
    def remove_time_by_name(self, remove_name):
        self.time_list = [(name, pin, time_set) for name, pin, time_set in self.time_list if name != remove_name]

    def start_timer(self):
        check_time_thread = threading.Thread(target=self.check_time, daemon=True)
        check_time_thread.start()

if __name__ == '__main__':
    def callback(name, pin, state):
        print(name, pin, state)

    time_list = [('led_1', [0, 1, 2, 3], ('23:55', '01:00')),
                 ('led_2', [0, 1, 2, 3], ('23:47', '23:48')),
                 ('led_3', [0, 1, 2, 3], ('23:46', '23:49'))]

    t_control = TimeControl(callback_func=callback)
    for i in time_list:
        t_control.add_new_time(*i)
    t_control.remove_time_by_name("led_2")
    print(t_control.time_list)
    t_control.start_timer()
    while True:
        time.sleep(0.1)

