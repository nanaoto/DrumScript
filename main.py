import argparse
import os
import sys
import numpy as np # <-- Added this import

# Add the parent directory of main.py to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from DrumScript.audio_processor import audio_loader, onset_detector, feature_extractor
    from DrumScript.drum_classifier import drum_model # Assuming you'll load a pre-trained model
    from DrumScript.notation_generator import score_builder, pdf_exporter
except ImportError as e:
    print(f"Error importing DrumScript modules: {e}")
    print("Please ensure your project structure is correct and that main.py can access the DrumScript package.")
    print("If running with 'uv', ensure you've run 'uv pip install -e .' from the project root.")
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
        # Assuming audio_loader also handles normalization or you add a separate normalize step
        audio_data, sr = audio_loader.load_audio(input_audio_path)
        # You might want a normalise_audio step here if audio_loader doesn't handle it
        # normalised_audio = audio_loader.normalise_audio(audio_data) # If you have this function
        
        onsets = onset_detector.detect_onsets(audio_data, sr) # Pass the original audio data
        print(f"Detected {len(onsets)} onsets.")

        # 2. Extract Features for Each Onset and Classify Drum Sounds
        print("Step 2/3: Extracting features and classifying drum sounds...")
        
        all_drum_events = [] # To store (onset_time, predicted_drum_type) tuples
        
        # Load your trained model and any necessary scalers/label maps here once
        # Example:
        # model_path = os.path.join(current_dir, "models", "multi_label_drum_classifier_model.h5")
        # label_map_path = os.path.join(current_dir, "models", "multi_label_label_map.json")
        # scaler_path = os.path.join(current_dir, "models", "multi_label_scaler.joblib")
        # trained_model = drum_model.load_model(model_path)
        # label_map = drum_model.load_label_map(label_map_path)
        # scaler = drum_model.load_scaler(scaler_path)


        if not onsets:
            print("No onsets detected. Cannot proceed with feature extraction and classification.")
            print(f"--- Transcription Complete (No Drums Found)! ---")
            pdf_exporter.export_to_pdf([], output_pdf_path) # Export empty score
            return


        for i, onset_time in enumerate(onsets):
            onset_sample = int(onset_time * sr)
            segment_length_samples = int(segment_length_seconds * sr)

            # Define the segment: from onset_sample to onset_sample + segment_length_samples
            segment_start = onset_sample
            segment_end = min(onset_sample + segment_length_samples, len(audio_data))
            
            audio_segment = audio_data[segment_start:segment_end] # Extract the segment

            if audio_segment.size == 0:
                print(f"  Warning: Onset {i+1} at {onset_time:.2f}s has an empty audio segment. Skipping.")
                continue # Skip to the next onset

            # Extract features for this *single* audio segment
            features_for_segment = feature_extractor.extract_features(audio_segment, sr)
            
            # --- Placeholder for your ML Model Prediction ---
            # Your classification model will take `features_for_segment`
            # and output a predicted drum type (e.g., "Kick", "Snare", "Hi-Hat").
            
            # Example using dummy classification:
            # In a real scenario, you'd feed features_for_segment into your trained_model
            # processed_features = scaler.transform(features_for_segment_reshaped) # if your model expects scaled data
            # prediction_probabilities = trained_model.predict(processed_features)
            # predicted_label_index = np.argmax(prediction_probabilities)
            # predicted_drum_type = label_map[predicted_label_index]
            
            # For demonstration, let's just cycle through some types
            dummy_drum_types = ["Kick", "Snare", "Hi-Hat", "Open-Hat", "Closed-Hat", "Tom"]
            predicted_drum_type = dummy_drum_types[i % len(dummy_drum_types)]
            
            #all_drum_events.append({"time": onset_time, "type": 
            # predicted_drum_type})
            all_drum_events.append({"time": onset_time, "drums": [predicted_drum_type]})
            print(f"  Onset at {onset_time:.2f}s classified as: {predicted_drum_type}")

        print(f"Classified {len(all_drum_events)} drum events in total.")

        # 3. Generate Musical Notation and PDF
        print("Step 3/3: Generating musical notation and PDF...")
        # Ensure the output directory exists
        output_dir = os.path.dirname(output_pdf_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created output directory: {output_dir}")

        #score = score_builder.build_score(all_drum_events) # Pass the list of classified events
        # The build_and_export_drum_score function in score_builder.py
        # already handles building the score AND exporting the PDF.
        # So, we call it directly here.
        score_builder.build_and_export_drum_score(
        detected_events=all_drum_events,
        tempo=120, # You can make this configurable via command line args later if needed
        output_filepath=output_pdf_path,
        quantization_subdivision=16 # You can make this configurable too
        )

        print(f"--- Transcription Complete! ---")
        print(f"Sheet music saved to: {output_pdf_path}")

    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
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