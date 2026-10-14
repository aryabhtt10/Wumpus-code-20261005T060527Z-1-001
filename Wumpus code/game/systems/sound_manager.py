"""
Sound Manager Module

Handles loading and playing of all game sounds with proper error handling.
Uses lazy loading and caching to efficiently manage sound resources.
"""

import os
import random
import pygame
import logging
from systems.asset_loader import load_sound

logger = logging.getLogger(__name__)


class SoundManager:
    """Manages all game sound effects and playback."""
    
    def __init__(self):
        self.sounds = {}
        self.bat_sounds = []
        self.spider_sounds = []
        self.footstep_sounds = []
        self._load_sounds()
    
    def _load_sounds(self):
        """Load all sound files with proper error handling."""
        
        # Map of logical sound names to filenames
        sound_files = {
            'arrow_whoosh': 'arrow whoosh.wav',
            'coin_collect': 'coin collect.wav',
            'correct_answer': 'correct answer.wav',
            'death': 'death.wav',
            'explosion': 'explosion.wav',
            'menu_change': 'menu change.wav',
            'menu_move_cursor': 'menu move cursor.wav',
            'menu_select': 'menu select.wav',
            'portal_woosh': 'portal woosh.wav',
            'spawn': 'spawn.wav',
            'wrong_answer': 'wrong answer.wav',
            'hurt': 'hurt.wav',
        }
        
        # Load individual sounds
        for sound_name, filename in sound_files.items():
            sound = load_sound(filename)
            if sound is not None:
                self.sounds[sound_name] = sound
                logger.debug(f"Loaded sound: {sound_name}")
            else:
                logger.warning(f"Could not load sound: {sound_name} ({filename})")
        
        # Load footstep sounds (multiple variations)
        for i in range(1, 4):
            filename = f"footstep {i}.wav"
            sound = load_sound(filename)
            if sound is not None:
                self.footstep_sounds.append(sound)
            else:
                logger.warning(f"Could not load footstep sound: {filename}")
        
        # Load bat sounds (multiple variations)
        for i in range(1, 4):
            filename = f"bat sounds {i}.wav"
            sound = load_sound(filename)
            if sound is not None:
                self.bat_sounds.append(sound)
            else:
                logger.warning(f"Could not load bat sound: {filename}")
        
        # Load spider sounds (multiple variations)
        for i in range(1, 4):
            filename = f"spider sounds {i}.wav"
            sound = load_sound(filename)
            if sound is not None:
                self.spider_sounds.append(sound)
            else:
                logger.warning(f"Could not load spider sound: {filename}")
        
        logger.info(f"Sound loading complete. Loaded: {len(self.sounds)} sounds, "
                   f"{len(self.footstep_sounds)} footsteps, "
                   f"{len(self.bat_sounds)} bat sounds, "
                   f"{len(self.spider_sounds)} spider sounds")
    
    def play(self, sound_name, volume=1.0, play_twice=False):
        """
        Play a sound by its logical name.
        
        Args:
            sound_name: Logical name of the sound (e.g., 'arrow_whoosh')
            volume: Volume level (0.0 to 1.0)
            play_twice: If True, play the sound twice for amplification
        """
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
            
            # Play a second time for amplified effect (e.g., arrow whoosh)
            if play_twice:
                sound.play()
        else:
            logger.debug(f"Sound '{sound_name}' not found or not loaded")
    
    def play_footstep(self):
        """Play a random footstep sound."""
        if self.footstep_sounds:
            random.choice(self.footstep_sounds).play()
        else:
            logger.debug("No footstep sounds available")
    
    def play_bat_sound(self):
        """Play a random bat sound."""
        if self.bat_sounds:
            random.choice(self.bat_sounds).play()
        else:
            logger.debug("No bat sounds available")
    
    def play_spider_sound(self):
        """Play a random spider sound."""
        if self.spider_sounds:
            random.choice(self.spider_sounds).play()
        else:
            logger.debug("No spider sounds available")
    
    def stop_all(self):
        """Stop all currently playing sounds."""
        pygame.mixer.stop()
        logger.debug("All sounds stopped")
    
    def set_master_volume(self, volume):
        """
        Set the master volume for all sounds.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        pygame.mixer.music.set_volume(volume)
        for sound in self.sounds.values():
            sound.set_volume(volume)
        for sound in self.footstep_sounds:
            sound.set_volume(volume)
        for sound in self.bat_sounds:
            sound.set_volume(volume)
        for sound in self.spider_sounds:
            sound.set_volume(volume)
        logger.info(f"Master volume set to {volume}")