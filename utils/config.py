# DrumScript/notation_generator/config.py

# Default tempo in BPM if not detected or provided by user
DEFAULT_TEMPO_BPM = 120

# Quantization subdivision (e.g., 4 for quarter notes, 8 for eighth notes, 16 for sixteenth notes)
# This defines the smallest rhythmic value to snap notes to.
QUANTIZATION_SUBDIVISION = 16

# PDF export settings
PDF_PAGE_SIZE = 'A4' # Other options: 'LETTER', 'LEGAL', etc.
PDF_MARGIN_TOP = 50
PDF_MARGIN_BOTTOM = 50
PDF_MARGIN_LEFT = 50
PDF_MARGIN_RIGHT = 50
PDF_FONT = 'Helvetica'
PDF_FONT_SIZE_TITLE = 24
PDF_FONT_SIZE_BODY = 12

# Staff and note rendering settings
STAFF_LINE_SPACING = 10 # Pixels or points between staff lines
NOTE_HEAD_SIZE = 8    # Size of the note head

# Drum part mapping (example, should align with your model's classification)
# This maps classified drum types to their visual representation (e.g., note head, staff position)
# More complex mappings might live in score_builder or constants.
DRUM_NOTATION_MAP = {
    'kick': {'note_head': 'x', 'staff_position': 'F2'}, # F2 often represents Kick
    'snare': {'note_head': 'normal', 'staff_position': 'C3'}, # C3 often represents Snare
    'hi-hat': {'note_head': 'x', 'staff_position': 'G3'}, # G3 often represents Hi-Hat
    'crash': {'note_head': 'x', 'staff_position': 'C4'}, # C4 often represents Crash
    'ride': {'note_head': 'x', 'staff_position': 'A3'}, # A3 often represents Ride
    # Add more drum types as classified by your model
}

# Example of how to get config values (similar to main.py's get_config but specific to notation)
def get_notation_config():
    """
    Returns a dictionary of notation generation configuration settings.
    """
    return {
        'default_tempo': DEFAULT_TEMPO_BPM,
        'quantization_subdivision': QUANTIZATION_SUBDIVISION,
        'pdf_settings': {
            'page_size': PDF_PAGE_SIZE,
            'margin_top': PDF_MARGIN_TOP,
            'margin_bottom': PDF_MARGIN_BOTTOM,
            'margin_left': PDF_MARGIN_LEFT,
            'margin_right': PDF_MARGIN_RIGHT,
            'font': PDF_FONT,
            'font_size_title': PDF_FONT_SIZE_TITLE,
            'font_size_body': PDF_FONT_SIZE_BODY,
        },
        'staff_line_spacing': STAFF_LINE_SPACING,
        'note_head_size': NOTE_HEAD_SIZE,
        'drum_notation_map': DRUM_NOTATION_MAP,
    }

# This could also be a simple dictionary if not using a function for dynamic config loading
# NOTATION_CONFIG = { ... }