"""
Sound System - DOS-style beep sounds for Melee at Sea using Pyglet
"""
import pyglet
import math
import array


def generate_sine_wave(frequency, duration, sample_rate=22050, volume=0.3):
    """Generate a sine wave tone."""
    num_samples = int(sample_rate * duration)
    data = array.array('h')  # signed short
    
    for i in range(num_samples):
        t = i / sample_rate
        # Apply envelope for cleaner sound
        envelope = 1.0
        attack = 0.01
        release = 0.05
        if t < attack:
            envelope = t / attack
        elif t > duration - release:
            envelope = (duration - t) / release
        
        sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * t))
        data.append(sample)
    
    return bytes(data)


def generate_noise_burst(duration, sample_rate=22050, volume=0.2):
    """Generate white noise burst (for cannon fire)."""
    import random
    num_samples = int(sample_rate * duration)
    data = array.array('h')
    
    for i in range(num_samples):
        t = i / sample_rate
        # Decay envelope
        envelope = max(0, 1 - (t / duration) * 2)
        sample = int(32767 * volume * envelope * (random.random() * 2 - 1))
        data.append(sample)
    
    return bytes(data)


class SoundSystem:
    """DOS-style sound effect generator."""
    
    def __init__(self):
        """Initialize the sound system."""
        self.sounds = {}
        self._generate_sounds()
    
    def _create_source(self, audio_data, sample_rate=22050):
        """Create a pyglet audio source from raw data."""
        return pyglet.media.StaticSource(
            pyglet.media.codecs.base.AudioData(
                audio_data,
                len(audio_data),
                0.0,
                len(audio_data) / (sample_rate * 2),
                (len(audio_data) // 2, sample_rate * 2)
            )
        )
    
    def _generate_sounds(self):
        """Generate all game sounds."""
        sample_rate = 22050
        
        # Movement beep - short low tone
        move_data = generate_sine_wave(220, 0.05, sample_rate, 0.2)
        
        # Rotation beep - two quick tones
        rot1 = generate_sine_wave(330, 0.03, sample_rate, 0.2)
        rot2 = generate_sine_wave(440, 0.03, sample_rate, 0.2)
        rotate_data = rot1 + rot2
        
        # Fire sound - noise burst (louder and longer)
        fire_data = generate_noise_burst(0.4, sample_rate, 0.6)
        
        # Hit sound - descending tone (louder)
        hit_data = b''
        for freq in [600, 500, 400, 300]:
            hit_data += generate_sine_wave(freq, 0.1, sample_rate, 0.4)
        
        # Miss sound - low buzz
        miss_data = generate_sine_wave(150, 0.2, sample_rate, 0.3)
        
        # Destroy sound - explosion-like (much louder)
        destroy_data = generate_noise_burst(0.6, sample_rate, 0.7)
        for freq in [200, 150, 100]:
            destroy_data += generate_sine_wave(freq, 0.2, sample_rate, 0.5)
        
        # Select sound - quick high beep
        select_data = generate_sine_wave(880, 0.04, sample_rate, 0.2)
        
        # Place ship sound - confirmation tone
        place_data = generate_sine_wave(440, 0.05, sample_rate, 0.2)
        place_data += generate_sine_wave(660, 0.08, sample_rate, 0.25)
        
        # Victory fanfare
        victory_data = b''
        victory_notes = [
            (523, 0.15),  # C5
            (523, 0.15),  # C5
            (523, 0.15),  # C5
            (523, 0.4),   # C5 (long)
            (415, 0.4),   # Ab4
            (466, 0.4),   # Bb4
            (523, 0.15),  # C5
            (466, 0.15),  # Bb4
            (523, 0.6),   # C5 (long)
        ]
        for freq, dur in victory_notes:
            victory_data += generate_sine_wave(freq, dur, sample_rate, 0.3)
        
        # Defeat sound - sad descending
        defeat_data = b''
        defeat_notes = [(400, 0.3), (350, 0.3), (300, 0.3), (250, 0.5)]
        for freq, dur in defeat_notes:
            defeat_data += generate_sine_wave(freq, dur, sample_rate, 0.25)
        
        # Store the raw audio data and create sources on-demand
        self.audio_data = {
            'move': move_data,
            'rotate': rotate_data,
            'fire': fire_data,
            'hit': hit_data,
            'miss': miss_data,
            'destroy': destroy_data,
            'select': select_data,
            'place': place_data,
            'victory': victory_data,
            'defeat': defeat_data
        }
        
        # Generate theme song separately (it's longer)
        self._generate_theme_song()
    
    def _generate_theme_song(self):
        """Generate an 8-bit sea shanty theme song."""
        sample_rate = 22050
        
        # Sea shanty style melody in minor key - nautical 8-bit feel
        # Using square waves for authentic chiptune sound
        theme_data = b''
        
        # Theme melody notes (frequency, duration) - "Sailors' Voyage" 
        # A minor / D minor sea shanty progression
        melody = [
            # Intro - rising arpeggio
            (220, 0.15), (262, 0.15), (330, 0.15), (440, 0.3),
            (0, 0.1),  # rest
            
            # Main theme - Part A (call)
            (440, 0.25), (392, 0.25), (349, 0.25), (330, 0.5),
            (0, 0.1),
            (330, 0.25), (349, 0.25), (392, 0.25), (440, 0.5),
            (0, 0.1),
            
            # Main theme - Part B (response)
            (440, 0.2), (440, 0.2), (392, 0.3), (349, 0.3),
            (330, 0.2), (294, 0.2), (262, 0.6),
            (0, 0.2),
            
            # Bridge - dramatic rise
            (262, 0.15), (294, 0.15), (330, 0.15), (349, 0.15),
            (392, 0.15), (440, 0.15), (494, 0.15), (523, 0.4),
            (0, 0.1),
            
            # Climax
            (523, 0.3), (494, 0.2), (440, 0.3), (392, 0.2),
            (349, 0.4), (330, 0.4),
            (0, 0.1),
            
            # Resolution - descending
            (440, 0.25), (392, 0.25), (349, 0.25), (330, 0.25),
            (294, 0.25), (262, 0.25), (220, 0.6),
            (0, 0.3),
            
            # Tag ending
            (330, 0.2), (392, 0.2), (440, 0.6),
            (0, 0.5),
        ]
        
        for freq, dur in melody:
            if freq == 0:
                # Rest - silence
                num_samples = int(sample_rate * dur)
                theme_data += bytes(num_samples * 2)
            else:
                # Square wave for 8-bit chiptune sound
                theme_data += self._generate_square_wave(freq, dur, sample_rate, 0.2)
        
        self.audio_data['theme'] = theme_data
        self.theme_player = None
    
    def _generate_square_wave(self, frequency, duration, sample_rate=22050, volume=0.2):
        """Generate a square wave for authentic 8-bit chiptune sound."""
        num_samples = int(sample_rate * duration)
        data = array.array('h')
        
        for i in range(num_samples):
            t = i / sample_rate
            # Apply envelope
            envelope = 1.0
            attack = 0.01
            release = 0.03
            if t < attack:
                envelope = t / attack
            elif t > duration - release:
                envelope = max(0, (duration - t) / release)
            
            # Square wave: positive or negative based on sine phase
            phase = (frequency * t) % 1.0
            if phase < 0.5:
                sample = int(32767 * volume * envelope)
            else:
                sample = int(-32767 * volume * envelope)
            data.append(sample)
        
        return bytes(data)
    
    def play_theme(self):
        """Start playing the theme song (loops)."""
        self.stop_theme()
        try:
            data = self.audio_data.get('theme')
            if not data:
                print("No theme data found")
                return
            
            # Create audio source from raw PCM data
            # Use SourceGroup for looping
            import io
            import wave
            
            # Create a WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)
                wav_file.writeframes(data)
            
            wav_buffer.seek(0)
            source = pyglet.media.load('theme.wav', file=wav_buffer)
            
            self.theme_player = pyglet.media.Player()
            self.theme_player.loop = True
            self.theme_player.queue(source)
            self.theme_player.volume = 0.5
            self.theme_player.play()
        except Exception as e:
            print(f"Error playing theme: {e}")
    
    def stop_theme(self):
        """Stop the theme song."""
        if self.theme_player:
            try:
                self.theme_player.pause()
                self.theme_player = None
            except Exception:
                pass
    
    def play(self, sound_name):
        """Play a sound effect using in-memory WAV format."""
        if sound_name not in self.audio_data:
            return
        
        try:
            import io
            import struct
            import wave
            
            data = self.audio_data[sound_name]
            sample_rate = 22050
            
            # Create in-memory WAV file
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)  # 16-bit
                wav.setframerate(sample_rate)
                wav.writeframes(data)
            
            buffer.seek(0)
            source = pyglet.media.load('sound.wav', file=buffer)
            player = pyglet.media.Player()
            player.queue(source)
            player.play()
        except Exception:
            pass
