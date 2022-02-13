import src.fx_lab.replay as replay
import mido
import logging


replay_logger = replay.logger
# replay_logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

bpm = 120
fs = 44100
test_file = './tests/test_data/midi/byzantineBlip_chorus.mid'

mid = mido.MidiFile(test_file, clip=True)

midi_bus = replay.load_midi_file(test_file, bpm, fs)
midi_track = midi_bus.get_track(0)
# midi = replay.FxlMidiTrack(bpm, fs)
# midi.load_midi_file(test_file)

# Note: The implementation of this test is a bit close to what is being tested,
#       might not catch concept problems
seconds_per_tick = 60/(mid.ticks_per_beat * bpm)
ticks = 0
for msg in mid.tracks[0]:
    ticks += msg.time
    t = ticks * seconds_per_tick
    sample = int(t * fs)
    assert msg.type in [x['type'] for x in midi_track[sample]]

# TODO: Perform more meaningful tests of slice operation
# TODO: Add a test to show that doing stuff to a returned value from slice will not affect the original track
track_slice = midi_track[992249:992255]
track_slice[992251] = None
# TODO: Add test for raised exception from the following line
# track_slice['asdf'] = None
print(f'track_slice: {track_slice}')
print(type(midi_track[992249:992255]))
print(midi_track[992249:992255])

print(f'midi_track[992250]: {midi_track[992250]}')
print(f'midi_track[992251]: {midi_track[992251]}')
# print(midi_track[0:1000000])
# print(midi_track.name)
