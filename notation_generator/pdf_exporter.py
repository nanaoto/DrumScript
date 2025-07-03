# DrumScript/notation_generator/pdf_exporter.py

from typing import Dict, Any
import os
import music21 # Import the music21 library

# Optional: You might want to import config for default settings
# from . import config 

def generate_pdf(score_data: Dict[str, Any], output_filepath: str):
    """
    Generates a PDF document of the drum sheet music from the structured score data
    using music21 and an external music engraving software (like MuseScore or LilyPond).

    Args:
        score_data (Dict[str, Any]): A dictionary containing the structured score information.
        output_filepath (str): The full path where the PDF file should be saved.
    """
    if not score_data or not score_data.get('parts', {}).get('drums'):
        print("No score data provided or no drum events to generate PDF.")
        return

    print(f"Generating PDF for '{score_data.get('title', 'Untitled')}' to {output_filepath} using music21...")

    try:
        # --- Music21 Environment Setup (Important for LilyPond) ---
        # music21 tries to auto-locate LilyPond. If it can't find it,
        # you might need to manually specify the path to your LilyPond executable.
        # Uncomment and adjust the line below if you get errors like "Couldn't find LilyPond"
        # after running the script.
        #
        # Example for macOS (adjust path based on where you installed LilyPond):
        # music21.environment.UserSettings()['lilypondPath'] = '/Applications/LilyPond.app/Contents/Resources/bin/lilypond' # Adjust this path to your LilyPond executable
        # music21.environment.UserSettings().write() # Save the setting

        # 1. Create a new Score object
        score = music21.stream.Score()

        # 2. Create a Part for drums
        part = music21.stream.Part()
        part.partName = 'Drums'
        part.clef = music21.clef.PercussionClef() # Set percussion clef

        # Add initial metadata (time signature, tempo)
        # Assume time signature is passed in score_data, e.g., '4/4'
        time_signature_str = score_data.get('time_signature', '4/4')
        ts = music21.meter.TimeSignature(time_signature_str)
        part.append(ts)

        # Set tempo if available
        tempo_bpm = score_data.get('tempo', 120) # Default to 120 BPM
        metronome = music21.tempo.MetronomeMark(number=tempo_bpm)
        part.append(metronome)

        # Sort events by time to ensure chronological order
        sorted_events = sorted(score_data['parts']['drums'], key=lambda x: x['time_beats'])

        # 3. Add notes to the part
        for event_idx, note_data in enumerate(sorted_events):
            beat_time = note_data['time_beats'] # This is the absolute beat time in quarter notes
            midi_pitch = note_data['midi_pitch']
            note_head_type = note_data['note_head_type']
            duration_beats = note_data['duration_beats'] # This is the quantized duration from score_builder

            # Create a music21 note object
            n = music21.note.Not
            n.pitch = music21.pitch.Pitch(midi=midi_pitch)
            n.quarterLength = duration_beats

            # Set notehead style for percussion (e.g., 'x' for cymbals/hi-hat)
            # 'normal' is music21's default, so only explicitly set if 'x'
            if note_head_type == 'x':
                n.notehead = note_head_type # Assign the string directly
            
            # Insert the note directly into the part at its absolute beat_time
            part.insert(beat_time, n) # This is the key change: insert directly into part

        # Let music21 automatically create and fill measures for the entire part
        # This handles measure breaks and rests automatically after all notes are inserted
        # part.makeMeasures(inPlace=True, finalBarline=True) # Changing/removing this temporarily while testing main.py
        part.makeMeasures(inPlace=True)
        
        # 4. Add the part to the score
        score.append(part)

        # 5. Export to PDF
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_filepath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)


        # --- START DIAGNOSTIC ---
        current_lilypond_path = music21.environment.UserSettings()['lilypondPath']
        print(f"DEBUG: music21's lilypondPath setting during PDF generation: {current_lilypond_path}")
        if not current_lilypond_path:
            print("DEBUG: WARNING: music21's lilypondPath is NOT set! This is likely why PDF generation is failing.")
    # --- END DIAGNOSTIC ---

        # The 'write' method will try to find LilyPond and convert MusicXML to PDF. Use block below if getting error with pdf
        score.write('pdf', fp=output_filepath)
        print(f"Successfully generated PDF to {output_filepath}")
        
        # Temporarily write to MusicXML to check if score creation is successful
        # Use 'musicxml' format # Change .pdf to .xml, uncomment to use for testing if .pdf raising errors
        #xml_filepath = output_filepath.replace('.pdf', '.xml') 
        #score.write('musicxml', fp=xml_filepath)
        # print(f"Successfully generated MusicXML to {xml_filepath}")

    except music21.converter.ConverterException as e:
        print(f"Error during music21 conversion/PDF generation. "
              f"This often means LilyPond (or MuseScore) is not installed or music21 can't find it. Error: {e}")
        print("Please ensure LilyPond is installed and its executable is in your system's PATH.")
        print("Alternatively, you might need to manually configure music21's environment path. For example, in a Python console (once):")
        print(f">>> import music21")
        print(f">>> music21.environment.UserSettings()['lilypondPath'] = '/Applications/LilyPond.app/Contents/Resources/bin/lilypond' # Adjust this path to your LilyPond executable")
        print(f">>> music21.environment.UserSettings().write() # Save the setting")
    except Exception as e:
        print(f"An unexpected error occurred during PDF generation: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging