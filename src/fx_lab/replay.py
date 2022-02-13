import mido
import logging
import typing
import numpy as np
import copy


logger = logging.getLogger(__name__)


class MissingCallbackError(Exception):
    """ Raise on missing an expected callback function """


# TODO: Consider an event track base class adding replay capability


# TODO: Break out load function
# TODO: Split into MidiTrack and Bus (possibly MidiBus inheriting from Bus)
class FxlMidiTrack:
    def __init__(self, bpm, fs):
        self.bpm = bpm
        self.fs = fs
        self.events = {}

    def load_midi_file(self, filename):
        mid = mido.MidiFile(filename, clip=True)
        self.ticks_per_beat = mid.ticks_per_beat
        self.calculate_samples_per_tick()
        self.midi_track = mid.tracks[0]
        self.build_event_array()

    def calculate_samples_per_tick(self):
        # We have BPM beats/minute -> bpm beats/(60 seconds)
        # There are ticks_per_beat ticks in every beat
        # Hence we have ticks_per_beat * bpm / (60 seconds) ticks per second
        # There are fs samples per seconds -> 60*fs samples per minute
        # Hence we have
        self.ticks_per_sample = self.ticks_per_beat * self.bpm / (60 * self.fs)
        self.samples_per_tick = 60*self.fs / (self.bpm*self.ticks_per_beat)

    def build_event_array(self):
        ticks = 0
        for msg in self.midi_track:
            logger.debug(msg)
            ticks += msg.time
            sample = int(self.samples_per_tick * ticks)
            if msg.type in ['note_on', 'note_off']:              
                event = {'type': msg.type, 'note': msg.note, 'velocity': msg.velocity}
            elif msg.type == 'end_of_track':
                event = {'type': msg.type}
            elif msg.type == 'control_change':
                event = {'type': 'CC',  'CC_nbr': msg.control, 'CC_value': msg.value}
            else:
                logger.warning(f'{msg.type} messages not handled')
                event = None
            if event:
                # TODO: Create a class for FxlMidiEvent, possibly as subclass of FxlEvent
                if self.events.get(sample):
                    self.events[sample].append(event)
                else:
                    self.events[sample] = [event]

    def __getitem__(self, sample):
        if isinstance(sample, slice):
            # TODO: Implement stride?
            # TODO: Check negative slice indices
            ret = {}
            for sample_pos in range(sample.start, sample.stop):
                if self.events.get(sample_pos):
                    ret[sample_pos] = self.events[sample_pos]
            return copy.copy(ret)
        return copy.copy(self.events.get(sample))

    def __repr__(self):
        return repr(self.events)

    def keys(self):
        return self.events.keys()

    @property
    def length(self):
        return max(self.events.keys())

    def add_event(self, sample, event):
        if self.events.get(sample):
            self.events[sample].append(event)
        else:
            self.events[sample] = [event]


class FxlAudioTrack:
    def __init__(self):
        self.audio = {}
        self.length = 0
        self.channels = 0

    def set_audio(self, channel: int, audio: np.array):
        # TODO: Improve
        # TODO: Add length checks, all channels should be same length
        self.audio[channel] = audio
        self.length = length(audio)
        self.channels = channel + 1


# TODO: Add buffer data class
class ReplayBufferList:
    def __init__(self, buffer_size: int=None, callback: typing.Callable=None,
                       midi: FxlMidiTrack=None, audio: FxlAudioTrack=None):
        assert callable(callback) or type(callback) in [type(None)], "callback should be function or None"
        assert type(buffer_size) in [int, type(None)], "buffer_size should be int or None"
        assert type(midi) in [FxlMidiTrack, type(None)], "midi should be FxlMidi or None"
        assert type(audio) in [FxlAudioTrack, type(None)], "audio should be FxlAudio or None"        
        self.buffer_size = buffer_size
        self.callback = callback
        self.midi = midi
        self.audio = audio

    def replay(self):
        # Should probably be a loop through multiple midi objects, each having multiple tracks
        # TODO: Better testing of which input data is present
        if self.midi:
            midi_end = self.midi.length
            # TODO: Add audio endpoints
            endpoints = [midi_end]
            end = max(endpoints)
            end = end + (self.buffer_size - 1) - (end % self.buffer_size)
        if self.callback == None:
            raise MissingCallbackError('ReplayBufferList.replay() requires a callback function to be set')
        start_sample = 0
        while start_sample < end:           
            end_sample = start_sample + self.buffer_size
            midi_slice_ = self.midi[start_sample:end_sample]
            midi_slice = {}
            # Recalculate sample numbers to reference to buffer start
            # TODO: Decide if this should this be done here or in the midi class
            for key in midi_slice_:
                midi_slice[key % self.buffer_size] = midi_slice_[key]
            # TODO: Create a class for buffer data
            buffer_data = {'midi': midi_slice}
            self.callback(buffer_data)
            start_sample += self.buffer_size
