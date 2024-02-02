import pulsectl
import time

with pulsectl.Pulse('my-client') as pulse:
    print("List sinks")
    for sink in pulse.sink_list():
        print(sink)
    print("List inputs")
    for input in pulse.sink_input_list():
        print(input)
        print("mute input")
        input.volume_change_all_chans(input, 0)
        time.sleep(2)
        print("unmute input")
        input.volume_change_all_chans(input, 1)


