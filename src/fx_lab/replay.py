import mido
import logging
import typing
import numpy as np
import copy
import os


logger = logging.getLogger(__name__)


class MissingCallbackError(Exception):
    """ Raise on missing an expected callback function """


# TODO: Consider an event track base class adding replay capability
# TODO: Consider storing length info, generating dynamically could potentially be costly,
#       should performance test this method for something with lots of tracks, events etc.
# TODO: Better name for time_type: signal_type? resolution_type?


def load_midi_file(filename, bpm, fs):
    # TODO: Enable using all tracks in file
    # TODO: Create an class for midi events (possibly subclassed from an event class)
    print(filename)
    mid = mido.MidiFile(filename, clip=True)
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_sample = ticks_per_beat * bpm / (60 * fs)
    samples_per_tick = 60*fs / (bpm*ticks_per_beat)
    input_track = mid.tracks[0]
    ticks = 0
    track_name = os.path.splitext(os.path.basename(filename))[0]
    midi_track = FxlMidiTrack(track_name, bpm, fs)
    for msg in input_track:
        logger.debug(msg)
        ticks += msg.time
        sample = int(samples_per_tick * ticks)
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
            midi_track.add_event(sample, event)
    midi_bus = FxlMidiBus()
    midi_bus.add_track(midi_track)  
    return midi_bus


# TODO: Maybe add a set_events function to set the entire events dict?
class FxlMidiTrack:
    def __init__(self, track_name: str, bpm: typing.Union[int, float], fs: int):
        self.bpm = bpm
        self.fs = fs
        self.name = track_name
        self.events = {}
        self.slice_ref_to_start = True

    def __getitem__(self, sample):
        if isinstance(sample, slice):
            # TODO: Implement stride?
            # TODO: Check negative slice indices
            events_dict = {}
            for sample_pos in range(sample.start, sample.stop):
                if self.events.get(sample_pos):
                    pos_adjust = sample.start if self.slice_ref_to_start else 0
                    events_dict[sample_pos - pos_adjust] = self.events[sample_pos]
            ret = FxlMidiTrack(self.name, self.bpm, self.fs)
            ret.events = events_dict
            return ret
        if isinstance(sample, int):
            return copy.copy(self.events.get(sample))
        raise KeyError("key (sample) should be int or slice")

    def __setitem__(self, sample: int, event):
        if isinstance(sample, int):
            self.add_event(sample, event)
        else:
            raise KeyError("sample should be an int")

    def __repr__(self):
        return repr(self.events)

    def keys(self):
        return self.events.keys()

    @property
    def length(self):
        return max(self.events.keys())

    def add_event(self, sample, event):
        # TODO: Some check if event is a list, in that case merge lists if list exists
        # self.length = max(self.length, sample)
        if self.events.get(sample):
            self.events[sample].append(event)
        else:
            self.events[sample] = [event]


class FxlMidiBus:
    def __init__(self):
        self.tracks = []
        self.track_name_map = {}
        self.n_tracks = 0
        self.time_type = 'event'
        # self.length = 0

    def __getitem__(self, sample: typing.Union[slice, int, str]):
        # TODO: Change var name: sample -> key
        ret = FxlMidiBus()
        if isinstance(sample, slice):
            for track in self.tracks:
                ret_track = track[sample.start:sample.stop]
                ret.add_track(ret_track)
                return ret
        if isinstance(sample, int):
            # Old code to return sample values, consider adding a setting for doing this
            # for track in self.tracks:
            #     # TODO: Consider adding some copy method to FxlMidiTrack class, is there a dunder for this?
            #     ret_track = FxlMidiTrack(track.name, track.bpm, track.fs)
            #     ret_track.events[sample] = track[sample]
            #     ret.add_track(ret_track)
            #     return ret
            if sample < self.n_tracks:
                return self.tracks[sample]
            else:
                raise KeyError("Tried to get nonexistent track")
        # TODO: Code for getting based on track name
        # if isinstance(sample, str):
        #     return self.

    @property
    def length(self):
        return max((track.length for track in self.tracks))

    def __repr__(self):
        return repr(self.tracks)

    def add_track(self, track):
        # TODO: Test that track is an allowed type
        self.tracks.append(track)
        self.track_name_map[track.name] = self.n_tracks
        self.n_tracks += 1

    def get_track(self, key: typing.Union[int, str]):
        # TODO: Check input type
        if isinstance(key, int):
            if key in range(self.n_tracks):
                return self.tracks[key]
            else:
                raise KeyError("Tried to get non-existent track")
        if isinstance(key, str):
            if key in self.track_name_map.keys():
                track_number = self.track_name_map[key]
                return self.tracks[track_number]
            else:
                raise KeyError("Tried to get non-existent track")



class FxlAudioBus:
    def __init__(self):
        pass


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



class FxlBufferData:
    def __init__(self):
        self.busses = []
        self.bus_names = {}
        self.n_busses = 0

    def add_bus(self, bus_name: str, bus: typing.Union[FxlMidiBus, FxlAudioBus]):
        # TODO: Should probably use ordered dicts for this instead of a list + a dict
        self.busses.append(bus)
        self.bus_names[bus_name] = self.n_busses
        # self.busses[bus_name] = bus
        self.n_busses += 1

    # TODO: Could be clearer that this referes to length in samples
    @property
    def length(self):
        # return max((bus.length for bus in self.busses.values()))
        return max((bus.length for bus in self.busses))

    def __getitem__(self, key):
        # TODO: Change arg name to key
        ret_data = FxlBufferData()
        if isinstance(key, slice):
            # for bus_name, bus in self.busses.items():
            for bus_name, bus_nbr in self.bus_names.items():
                bus = self.busses[bus_nbr]
                ret_bus = bus[key.start:key.stop]
                ret_data.add_bus(bus_name, ret_bus)
                return ret_data
        if isinstance(key, int):
            # TODO: Return bus number key
            # for bus_name, bus in self.busses.items():
            #     ret_bus = bus[key]
            #     ret_data.add_bus(bus_name, ret_bus)
            #     return ret_data
            return None
        if isinstance(key, str):
            # if key in self.busses.keys():
            if key in self.bus_names.keys():
                return self.busses[self.bus_names[key]]
            else:
                raise KeyError(f"No item {key} in FxlBufferData object")


    def __repr__(self):
        # return "\n".join([repr(bus) for bus_name, bus in self.busses.items()])
        return "\n".join([repr(bus) for bus in self.busses])



class ReplayBufferList:
    def __init__(self, buffer_size: int=None, callback: typing.Callable=None, buffer_data: FxlBufferData=None):
        assert callable(callback) or type(callback) in [type(None)], "callback should be function or None"
        assert type(buffer_size) in [int, type(None)], "buffer_size should be int or None"
        assert type(buffer_data) in [FxlBufferData, type(None)], "buffer_data should be FxlBufferData or None"
        self.buffer_size = buffer_size
        self.callback = callback
        self.buffer_data = buffer_data

    def replay(self):
        # TODO: Better testing of which input data is present
        assert isinstance(self.callback, typing.Callable), "Replay not possible without a callback function"
        assert isinstance(self.buffer_data, FxlBufferData), "Replay not possible without buffer data"
        replay_length = self.buffer_data.length
        start_sample = 0
        while start_sample < replay_length:
            end_sample = start_sample + self.buffer_size
            buffer_data_slice = self.buffer_data[start_sample:end_sample]
            self.callback(buffer_data_slice)
            start_sample += self.buffer_size
