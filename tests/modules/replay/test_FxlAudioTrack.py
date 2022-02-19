from distutils.util import change_root

from matplotlib.pyplot import isinteractive
import src.fx_lab.replay as replay
import mido
import logging
import numpy as np


replay_logger = replay.logger
# replay_logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

# bpm = 120
# fs = 44100
# test_file = './tests/test_data/midi/byzantineBlip_chorus.mid'

audio_track_name = 'test_track'
audio_track_length = 20
channel_0_values = 0.0
channel_1_values = 1.252345

audio_track = replay.FxlAudioTrack(audio_track_name)

audio_track.set_channel(0, channel_0_values * np.ones(audio_track_length))
assert audio_track.length == audio_track_length
assert audio_track.n_channels == 1

try:
    audio_track.add_channel([0, 1, 2])
except Exception as error:
    assert isinstance(error, replay.AudioDataTypeError)
    assert audio_track.n_channels == 1

try:
    audio_track.add_channel(np.zeros(audio_track_length + 1))
except Exception as error:
    assert isinstance(error, replay.AudioDataLengthError)
    assert audio_track.n_channels == 1

audio_track.add_channel(channel_1_values * np.ones(audio_track_length))
assert audio_track.n_channels == 2

assert audio_track[audio_track_length - 1][0] == channel_0_values
assert audio_track[audio_track_length - 1][1] == channel_1_values

try:
    audio_track[-1]
except Exception as error:
    assert isinstance(error, IndexError)

try:
    audio_track[audio_track_length + 1]
except Exception as error:
    assert isinstance(error, IndexError)


sample_values = audio_track[0]

channel_nbr_to_check = 1
assert audio_track.channels[channel_nbr_to_check][0] == sample_values[channel_nbr_to_check]

sample_values[channel_nbr_to_check] = 2.4574
# audio_track[0] should return copies, hence these should no longer be equal
assert not(audio_track.channels[channel_nbr_to_check][0] == sample_values[channel_nbr_to_check])

audio_track.channels[0][15] = 3.46747
audio_track_slice = audio_track[10:20]
assert isinstance(audio_track_slice, replay.FxlAudioTrack)
assert audio_track_slice.channels[0][5] == audio_track.channels[0][15]
# TODO: Make this an assert
print(str(audio_track_slice))
audio_track.channels[0][15] = 4.7546754
# audio_track[10:20] should return copies, hence these should no longer be equal
assert not(audio_track_slice.channels[0][5] == audio_track.channels[0][15])
