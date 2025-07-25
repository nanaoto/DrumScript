# DrumScript/main.py

import argparse
import os
import sys
import numpy as np

# No need for sys.path manipulation here.
# When main.py is run directly from the package root (DrumScript/),
# Python's import system will correctly resolve sub-package imports.

try:
    # --- CORRECTED IMPORTS ---
    # These imports are now relative to the 'DrumScript' package root
    # where main.py itself resides.
    from audio_processor import audio_loader, onset_detector, feature_extractor
    from drum_classifier import drum_model # Assuming you'll load a pre-trained model
    from notation_generator import score_builder, pdf_exporter
except ImportError as e:
    print(f"Error importing DrumScript modules: {e}")
    print("Please ensure your project structure is correct and that main.py can access its sub-packages.")
    print("If running with 'uv', ensure you've run 'uv pip install -e .' from the DrumScript project root.")
    sys.exit(1)


def transcribe_audio_to_sheet_music(input_audio_path: str, output_pdf_path: str):
    """
    Orchestrates the entire process from an input drum audio file
    to an output PDF of the sheet music.
    """
    if not os.path.exists(input_audio_path):
        print(f"Error: Input audio file not found at '{input_audio_path}'")
        sys.exit(1)

    print(f"--- Starting DrumScript Transcription ---")
    print(f"Input Audio: {input_audio_path}")

    # Define a segment length for feature extraction (e.g., 200ms)
    # This should match how your model was trained if feature extraction for individual hits
    segment_length_seconds = 0.2 

    try:
        # 1. Load and Process Audio
        print("Step 1/3: Loading and processing audio and detecting onsets...")
        audio_data, sr = audio_loader.load_audio(input_audio_path)
        
        onsets = onset_detector.detect_onsets(audio_data, sr)
        print(f"Detected {len(onsets)} onsets.")

        # 2. Extract Features and Classify Drum Sounds
        print("Step 2/3: Extracting features and classifying drum sounds...")
        
        all_drum_events = [] # To store (onset_time, predicted_drum_type) tuples
        
        # Load your trained model and any necessary scalers/label maps here once
        # Example (uncomment and adjust paths when your model is ready):
        # # Assuming models are in a 'models' directory at the DrumScript root
        # models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        # model_path = os.path.join(models_dir, "multi_label_drum_classifier_model.h5")
        # label_map_path = os.path.join(models_dir, "multi_label_label_map.json")
        # scaler_path = os.path.join(models_dir, "multi_label_scaler.joblib")
        # trained_model = drum_model.load_model(model_path)
        # label_map = drum_model.load_label_map(label_map_path)
        # scaler = drum_model.load_scaler(scaler_path)


        if not onsets:
            print("No onsets detected. Cannot proceed with feature extraction and classification.")
            print(f"--- Transcription Complete (No Drums Found)! ---")
            # Ensure pdf_exporter.export_to_pdf can handle an empty list for an empty score
            pdf_exporter.generate_pdf([], output_pdf_path) # Changed to generate_pdf based on score_builder
            return


        for i, onset_time in enumerate(onsets):
            onset_sample = int(onset_time * sr)
            segment_length_samples = int(segment_length_seconds * sr)

            segment_start = onset_sample
            segment_end = min(onset_sample + segment_length_samples, len(audio_data))
            
            audio_segment = audio_data[segment_start:segment_end]

            if audio_segment.size == 0:
                print(f"  Warning: Onset {i+1} at {onset_time:.2f}s has an empty audio segment. Skipping.")
                continue

            features_for_segment = feature_extractor.extract_features(audio_segment, sr)
            
            # --- Placeholder for your ML Model Prediction ---
            # Replace this with your actual drum classification model integration
            
            dummy_drum_types = ["Kick", "Snare", "Hi-Hat", "Open-Hat", "Closed-Hat", "Tom"]
            predicted_drum_type = dummy_drum_types[i % len(dummy_drum_types)]
            
            all_drum_events.append({"time": onset_time, "drums": [predicted_drum_type]})
            print(f"  Onset at {onset_time:.2f}s classified as: {predicted_drum_type}")

        print(f"Classified {len(all_drum_events)} drum events in total.")

        # 3. Generate Musical Notation and PDF
        print("Step 3/3: Generating musical notation and PDF...")
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        score_builder.build_and_export_drum_score(
            detected_events=all_drum_events,
            tempo=120, # Can be made configurable
            output_filepath=output_pdf_path,
            quantization_subdivision=16 # Can be made configurable
        )

        print(f"--- Transcription Complete! ---")
        print(f"Sheet music saved to: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """
    Main entry point for the DrumScript command-line application.
    Parses arguments and calls the transcription function.
    """
    parser = argparse.ArgumentParser(
        description="Convert drum audio into musical sheet music (PDF).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_audio_path",
        type=str,
        help="Path to the input drum audio file (e.g., .wav, .mp3, .flac)."
    )
    parser.add_argument(
        "output_pdf_path",
        type=str,
        help="Path where the generated sheet music PDF will be saved.\n"
             "Example: my_drum_song.pdf or output/my_sheet.pdf"
    )

    args = parser.parse_args()
    
    transcribe_audio_to_sheet_music(args.input_audio_path, args.output_pdf_path)

if __name__ == "__main__":
    main()