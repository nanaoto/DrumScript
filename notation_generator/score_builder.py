# DrumScript/notation_generator/score_builder.py

import music21
from typing import List, Dict, Any
from collections import defaultdict
from . import constants # Assuming constants.py defines DRUM_NOTATION_MAP
from .helpers import round_to_nearest_subdivision, get_note_duration_name # Assuming these are useful
from .pdf_exporter import generate_pdf # To actually export the PDF

def get_drum_music21_note_info(drum_type: str) -> Dict[str, Any]:
    """
    Retrieves music21-specific notation info for a given drum type from constants.DRUM_NOTATION_MAP.
    """
    drum_map = constants.DRUM_NOTATION_MAP.get(drum_type)
    if not drum_map:
        print(f"Warning: No notation mapping found for drum type: {drum_type}. Using default kick.")
        drum_map = constants.DRUM_NOTATION_MAP['kick'] # Fallback
    
    # music21.pitch.Pitch needs a nameWithOctave (e.g., 'F2', 'C3')
    # music21.note.Unpitched needs a displayStep and displayOctave or a MIDI number
    # The constants.py currently uses 'F2', 'C3' directly for staff_position, which is good.
    
    # We can use music21.pitch.Pitch to parse these string representations
    # and get the MIDI number or display pitch properties for Unpitched notes.
    
    # Use the 'staff_position' string for visual placement and the 'midi_program' for sound.
    # music21's Unpitched objects use displayStep and displayOctave for rendering.
    
    pitch_obj = music21.pitch.Pitch(drum_map['staff_position'])
    
    return {
        'midi_pitch': pitch_obj.midi, 
        'note_head': drum_map['note_head'],
        'staff_position': drum_map['staff_position'] # ADDED THIS LINE
    }

def build_and_export_drum_score(
    detected_events: List[Dict[str, Any]],
    tempo: int,
    output_filepath: str,
    quantization_subdivision: int = 16 # Default to 16th notes for quantization
):
    """
    Builds a music21 Score object for drum sheet music from detected events
    and exports it to a PDF file using LilyPond via MusicXML.

    Args:
        detected_events (List[Dict[str, Any]]): A list of dictionaries,
            each containing 'onset_time' (float) and 'drum_type' (str).
        tempo (int): The tempo of the piece in BPM.
        output_filepath (str): The full path where the PDF file should be saved.
        quantization_subdivision (int): The subdivision level for quantization
                                        (e.g., 4 for quarter, 8 for eighth, 16 for sixteenth).
    """
    print(f"Building music21 score with tempo {tempo} BPM...")

    # Create a new Score and Part
    score = music21.stream.Score()
    score.metadata = music21.metadata.Metadata()
    score.metadata.title = "Drum Transcription"
    score.metadata.composer = "DrumScript AI"

    drum_part = music21.stream.Part()
    drum_part.partName = 'Drum Kit'
    drum_part.partAbbreviation = 'Dms.'
    
    # Add a percussion instrument to the part
    percussion_instrument = music21.instrument.Percussion()
    # music21.instrument.DrumKit() can also be used, but Percussion is more general.
    drum_part.insert(0, percussion_instrument) # Insert at offset 0

    # Set initial tempo
    metronome_mark = music21.tempo.MetronomeMark(number=tempo)
    drum_part.insert(0, metronome_mark)
    
    # Add time signature (assuming 4/4 for now, can be made dynamic later)
    ts = music21.meter.TimeSignature('4/4')
    drum_part.insert(0, ts)

    # Group events by quantized time for chords
    quantized_events = defaultdict(list)
    for event in detected_events:
        onset_time = event['onset_time']
        drum_type = event['drum_type']
        
        # Quantize the onset time to the nearest subdivision
        quantized_time = round_to_nearest_subdivision(onset_time, tempo, quantization_subdivision)
        quantized_events[quantized_time].append(drum_type)

    # Sort quantized times to process chronologically
    sorted_quantized_times = sorted(quantized_events.keys())

    last_offset = 0.0
    for current_offset in sorted_quantized_times:
        # Add rests if there's a gap between the last event and the current one
        if current_offset > last_offset:
            rest_duration = current_offset - last_offset
            if rest_duration > 0:
                rest = music21.note.Rest()
                rest.duration.quarterLength = rest_duration
                drum_part.append(rest)
        
        # Create a chord for all drums hitting at this quantized time
        drums_at_this_time = quantized_events[current_offset]
        notes_in_chord = []

        # Create individual Unpitched notes for each drum type
        for drum_type in drums_at_this_time:
            note_info = get_drum_music21_note_info(drum_type)
            
            # Create an Unpitched note for each drum type in the chord
            up = music21.note.Unpitched()
            up.storedInstrument = music21.instrument.Percussion()
            
            # For unpitched notes, use displayStep and displayOctave for visual placement.
            # The 'staff_position' from your constants.py is already a string like 'F2', 'C3'.
            # We can parse this into a pitch object to extract its step and octave for display.
            pitch_for_display = music21.pitch.Pitch(note_info['staff_position'])
            up.displayStep = pitch_for_display.step
            up.displayOctave = pitch_for_display.octave
            
            # If you still want the MIDI pitch associated with the unpitched note
            # for internal music21 use or potential MIDI export, you can set it directly on the Unpitched object:
            up.midi = note_info['midi_pitch'] # Set MIDI directly on Unpitched object

            up.notehead = note_info['note_head']
            notes_in_chord.append(up)
        
        # Create a PercussionChord from the list of Unpitched notes
        p_chord = music21.percussion.PercussionChord(notes_in_chord)
        # Assuming all notes in a chord have the same duration, which is one subdivision
        p_chord.duration.quarterLength = (4.0 / quantization_subdivision) 
        drum_part.append(p_chord)
        
        last_offset = current_offset + (4.0 / quantization_subdivision) # Update last offset for rest calculation


    score.append(drum_part)

    # --- Export to PDF ---\
    # The generate_pdf function in pdf_exporter.py already handles music21 Stream to PDF conversion
    # It takes a score-like object and an output filepath.
    generate_pdf(score, output_filepath) # Pass the music21 score directly

    print(f"Music21 score built and ready for export to {output_filepath}")


# You might also want a separate function to just build the score object
# if you want to inspect it before exporting, but for now, this combined
# function is straightforward for the main workflow.