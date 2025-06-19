# DrumScript/__init__.py

"""
DrumScript: A Python package to convert drum audio recordings into sheet music.
"""

# Import the install_ffmpeg function to make it directly accessible via drumscript.install_ffmpeg()
from .utils.ffmpeg_installer import install_ffmpeg

# You might also want to expose other main functions/classes here later
# For example:
# from .audio_processor.audio_loader import load_audio
# from .main import process_drum_track # If main.py becomes the primary entry point function