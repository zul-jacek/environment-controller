from controller.control.time_control import TimeControl
import time 
if __name__ == '__main__':
    # important current time must be overwritten with self.new_time_now
    def callback(name, pin, state):
        print(name, pin, state)

    time_list = [('led_1', 0, ('23:55', '01:00')),
                 ('led_2', 0, ('23:47', '23:48')),
                 ('led_3', 0, ('15:46', '23:49')),
                 ('led_4', 0, ('14:00', '11:00')),
                 ('led_5', 0, ('14:00', '23:59')),
                 ('led_6', 0, ('23:59', '00:00')),
                 ('led_7', 0, ('23:59', '00:01')),
                 ('led_8', 0, ('15:46', '01:49'))]

    t_control = TimeControl(callback_func=callback)
    for i in time_list:
        t_control.add_new_time(*i)
    t_control.remove_time_by_name("led_2")
    # current time is overwritten by self.new_time_now (check_time_threshold)
    start_time = "23:50"
    t_control.new_time_now = t_control.timestr_to_min(start_time)
    
    print(start_time)
    
    t_control.start_timer()
    
    for accuracy_s in [1, 30]:
        for _ in range(75):
            time.sleep(0.5)
            t_control.new_time_now += accuracy_s
            if t_control.new_time_now >= 1440:
                t_control.new_time_now -= 1440
            h, m = divmod(t_control.new_time_now, 60)
            print(f"{h}:{m}")
