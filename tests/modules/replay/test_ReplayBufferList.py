from multiprocessing import dummy
import src.fx_lab.replay as replay
import mido
import logging
from random import randrange


replay_logger = replay.logger
# replay_logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

bpm = 120
fs = 44100
buffer_size = 10000
# test_file = './tests/test_data/midi/byzantineBlip_chorus.mid'
test_file = './tests/test_data/midi/byzantineBlip_verse.mid'


# midi_bus = replay.load_midi_file(test_file, bpm, fs)
midi_track = replay.FxlMidiTrack('dummy_track', bpm, fs)
dummy_event = {'type': 'note_on', 'note': 100, 'velocity': 100}
events_list = []
for k in range(10):
    ref_sample = randrange(buffer_size)
    events_list.append(ref_sample)
    midi_track.add_event(k * buffer_size + ref_sample, dummy_event)

midi_bus = replay.FxlMidiBus()
midi_bus.add_track(midi_track)
    
buffer_data = replay.FxlBufferData()
buffer_data.add_bus('midi', midi_bus)



class RenderClass:
    def __init__(self):
        self.buffer_number = 0
    
    def render_callback(self, buffer_data):
        print(self.buffer_number, events_list[self.buffer_number], buffer_data)
        midi_track_0 = buffer_data['midi'].get_track(0)
        assert events_list[self.buffer_number] == list(midi_track_0.keys())[0], "Misplaced event"
        self.buffer_number += 1
    

render_object = RenderClass()

replay = replay.ReplayBufferList(buffer_size=buffer_size, callback=render_object.render_callback, buffer_data=buffer_data)
replay.replay()
# replay = replay.ReplayBufferList(buffer_size=buffer_size, callback=render_object.render_callback, midi=midi)
# # replay = replay.ReplayBufferList(buffer_size=100, midi=midi)
# # replay = replay.ReplayBufferList()
# replay.replay()



