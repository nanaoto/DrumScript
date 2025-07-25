# DrumScript/notation_generator/pdf_exporter.py

import os
import music21

def generate_pdf(music21_score: music21.stream.Score, output_filepath: str):
    """
    Generates a PDF document of the drum sheet music from a music21 Score object
    by using music21's internal LilyPond integration.

    Args:
        music21_score (music21.stream.Score): The music21 Score object containing the drum notation.
        output_filepath (str): The full path where the PDF file should be saved.
    """
    if not music21_score:
        print("No music21 score provided to generate PDF.")
        return

    print(f"Generating PDF for '{music21_score.metadata.title}' to {output_filepath} using music21 and LilyPond...")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_filepath)
    os.makedirs(output_dir, exist_ok=True)

    try:
        # --- Configure music21 for LilyPond with the CORRECT path ---
        # This path was found using 'which lilypond' and confirmed by you.
        music21.environment.set('lilypondPath', '/opt/homebrew/bin/lilypond')
        music21.environment.set('pdfPath', '/opt/homebrew/bin/lilypond') # Often the same as lilypondPath

        # --- Direct PDF writing using music21's LilyPond integration ---
        music21_score.write('pdf', fp=output_filepath)
        print(f"PDF successfully saved to: {output_filepath}")

    except music21.converter.ConverterException as e:
        print(f"Error during music21 PDF export (LilyPond related): {e}")
        print("Please ensure LilyPond is installed and its path is correctly configured in music21.")
        print("You can configure music21 by running 'music21.configure.run()' in a Python interpreter.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred during PDF generation: {e}")
        import traceback
        traceback.print_exc()
        raise