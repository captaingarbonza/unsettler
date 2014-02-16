#
# The Unsettler
#	Make your favorite song creepy!
#
# By Crystal Valente
#
#
# Powered by the Echo Nest http://www.echonest.com
#
# Sound effects by http://www.freesfx.co.uk
#

import echonest.remix.audio as audio
import echonest.remix.modify as modify

import random
import copy
import math

def linear(input, in1, in2, out1, out2):
    return ((input-in1) / (in2-in1)) * (out2-out1) + out1

class Unsettler:
	def __init__(self, input_file_name):
		self.audio_file = audio.LocalAudioFile(input_file_name)
		self.loadSoundClips()
		self.audio_file.data *= linear(self.audio_file.analysis.loudness, -2, -12, 0.5, 1.5) * 0.6

	def loadSoundClips(self):
		self.breathing = audio.AudioData("clips/breath.mp3", sampleRate=44100, numChannels=2)
		self.growl = audio.AudioData("clips/growl.mp3", sampleRate=44100, numChannels=2)

	def unsettle(self, output_file ):
		out_shape = (len(self.audio_file.data), 2)
		self.out_data = audio.AudioData(shape=out_shape, numChannels=2, sampleRate=44100)
		self.addPitchChanges()
		self.addSoundEffects()
		self.out_data.encode(output_file)

	def addPitchChanges(self):
		modifier = modify.Modify(numChannels=2)
		beats = self.audio_file.analysis.beats
		target_pitch_change = 0.0
		delta = 0.0
		pitch_multiplier = 1.0
		pitch_increment = 0.0
		for i, beat in enumerate(beats):

			if target_pitch_change == 0.0 and random.randrange(0,4) == 0:
				target_pitch_change = random.randrange(-100,100)/100.0
				if target_pitch_change > 0.9: target_pitch_change = 0.9
				if target_pitch_change < 0 : pitch_multiplier *= -1.0
				pitch_increment = random.randrange(1,100)/500.0
				if pitch_increment < 0.002: pitch_increment = 0.002

			delta += pitch_increment*pitch_multiplier

			if delta == 0.0 or (delta >= 0.0 and target_pitch_change <= 0.0) or (delta <= 0.0 and target_pitch_change >= 0.0):
				delta = 0.0
				target_pitch_change = 0.0
				pitch_multiplier = 1.0
				pitch_increment = 0.0
			if (target_pitch_change < 0.0 and delta <= target_pitch_change) or (target_pitch_change > 0.0 and delta >= target_pitch_change):
				pitch_multiplier *= -1.0

			new_beat = modifier.shiftPitch(self.audio_file[beat], 1 + delta / 4.0)
			self.out_data.append(new_beat)

	def addSoundEffects(self):
		beats = self.audio_file.analysis.tatums
		for i, beat in enumerate(beats):
			rand_num = random.randrange(0,50)
			if rand_num < 2:
				effect = copy.deepcopy(self.growl)
				volume = beat.mean_loudness()
				volume += 25.0
				volume_adjust = volume/20.0
				if volume_adjust < 0.2: volume_adjust = 0.2
				if volume_adjust > 0.6: volume_adjust = 0.6
				effect.data *= volume_adjust
				self.out_data.add_at(beat.start, effect)

		for section in self.audio_file.analysis.sections[1:]:
			effect = copy.deepcopy(self.breathing)
			volume = section.mean_loudness()
			volume += 25.0
			volume_adjust = volume/20.0
			if volume_adjust < 0.3: volume_adjust = 0.3
			if volume_adjust > 0.6: volume_adjust = 0.6
			effect.data *= volume_adjust
			self.out_data.add_at(section.start, effect)

def main(input_file, output_file) :
    u = Unsettler(input_file)
    print 'unsettling'
    u.unsettle(output_file)

if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
    except :
        print usage
        sys.exit(-1)

    main(inputFilename, outputFilename)