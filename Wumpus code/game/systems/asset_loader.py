"""
Asset Loader Module

Handles loading of all game assets (images, sounds, etc.) with proper
error handling and fallbacks. Searches for assets in multiple locations
to accommodate different project structures.
"""

import os
import pygame
import logging

# Configure logging for asset loading
logger = logging.getLogger(__name__)

# Get the project root (assuming this file is in game/systems/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSET_DIR = os.environ.get('ASSET_DIR', os.path.join(PROJECT_ROOT, 'assets'))

# Search order for images - prioritizes images subfolder
_IMAGE_SEARCH_PATHS = [
    os.path.join(ASSET_DIR, 'images'),
    os.path.join(ASSET_DIR, 'img'),
    ASSET_DIR,
]

# Search order for sounds
_SOUND_SEARCH_PATHS = [
    os.path.join(ASSET_DIR, 'sounds'),
    os.path.join(ASSET_DIR, 'audio'),
    ASSET_DIR,
]


def load_image(filename, size=None):
    """
    Load an image from the assets directory.
    
    Args:
        filename: Name of the image file (e.g., 'player.png')
        size: Optional tuple (width, height) to scale the image
    
    Returns:
        pygame.Surface or None if image could not be loaded
    """
    for search_path in _IMAGE_SEARCH_PATHS:
        filepath = os.path.join(search_path, filename)
        try:
            if os.path.exists(filepath):
                image = pygame.image.load(filepath).convert_alpha()
                if size is not None:
                    image = pygame.transform.scale(image, size)
                logger.debug(f"Loaded image: {filepath}")
                return image
        except (pygame.error, FileNotFoundError) as e:
            logger.debug(f"Failed to load {filepath}: {e}")
            continue
    
    logger.warning(f"Could not load image '{filename}' from any search path")
    return None


def load_sound(filename):
    """
    Load a sound file from the assets directory.
    
    Args:
        filename: Name of the sound file (e.g., 'explosion.wav')
    
    Returns:
        pygame.mixer.Sound or None if sound could not be loaded
    """
    for search_path in _SOUND_SEARCH_PATHS:
        filepath = os.path.join(search_path, filename)
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                logger.debug(f"Loaded sound: {filepath}")
                return sound
        except (pygame.error, FileNotFoundError) as e:
            logger.debug(f"Failed to load {filepath}: {e}")
            continue
    
    logger.warning(f"Could not load sound '{filename}' from any search path")
    return None


def get_asset_path(filename, asset_type='image'):
    """
    Get the full path to an asset if it exists.
    
    Args:
        filename: Name of the asset file
        asset_type: Either 'image' or 'sound'
    
    Returns:
        Full path string or None if not found
    """
    search_paths = _IMAGE_SEARCH_PATHS if asset_type == 'image' else _SOUND_SEARCH_PATHS
    
    for search_path in search_paths:
        filepath = os.path.join(search_path, filename)
        if os.path.exists(filepath):
            return filepath
    
    return None


def asset_exists(filename, asset_type='image'):
    """
    Check if an asset exists in any search path.
    
    Args:
        filename: Name of the asset file
        asset_type: Either 'image' or 'sound'
    
    Returns:
        True if the asset exists, False otherwise
    """
    return get_asset_path(filename, asset_type) is not None