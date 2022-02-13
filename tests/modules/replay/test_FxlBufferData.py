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



buffer_data = replay.FxlBufferData()
buffer_data.add_bus('midi', midi_bus)
print(f'buffer_data.length: {buffer_data.length}')

print(f'buffer_data[992250:992251]: {buffer_data[992250:992251]}')
# print(f'buffer_data[992250]: {buffer_data[992250]}')
print(f'buffer_data[0]: {buffer_data[0]}')

# print(f'midi_bus.length: {midi_bus.length}')

# print(midi_bus[992250])
# print(midi_bus[992250:992251])
# print(midi_bus[992250:992251].length)
