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

midi = replay.FxlMidiTrack(bpm, fs)
midi.load_midi_file(test_file)

# Note: The implementation of this test is a bit close to what is being tested,
#       might not catch concept problems
seconds_per_tick = 60/(mid.ticks_per_beat * bpm)
ticks = 0
for msg in mid.tracks[0]:
    ticks += msg.time
    t = ticks * seconds_per_tick
    sample = int(t * fs)
    assert msg.type in [x['type'] for x in midi[sample]]

# TODO: Perform more meaningful tests of slice operation
print(midi[992249:992255])
print(midi[0:1000000])
