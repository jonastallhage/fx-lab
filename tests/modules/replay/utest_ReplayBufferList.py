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


midi = replay.FxlMidiTrack(bpm, fs)
# midi.load_midi_file(test_file)


dummy_event = {'type': 'note_on', 'note': 100, 'velocity': 100}
events_list = []
for k in range(10):
    ref_sample = randrange(buffer_size)
    events_list.append(ref_sample)
    midi.add_event(k * buffer_size + ref_sample, dummy_event)
    





class RenderClass:
    def __init__(self):
        self.buffer_number = 0
    
    def render_callback(self, buffer_data):
        print(self.buffer_number, events_list[self.buffer_number], buffer_data)
        assert events_list[self.buffer_number] == list(buffer_data['midi'].keys())[0], "Misplaced event"
        self.buffer_number += 1
    

render_object = RenderClass()


replay = replay.ReplayBufferList(buffer_size=buffer_size, callback=render_object.render_callback, midi=midi)
# replay = replay.ReplayBufferList(buffer_size=100, midi=midi)
# replay = replay.ReplayBufferList()
replay.replay()



