# DrumScript/audio_processor/feature_extractor.py

import librosa
import numpy as np
import os

def extract_features(audio_segment: np.ndarray, sr: int) -> dict[str, np.ndarray]:
    """
    Extracts various audio features from a short audio segment.
    Returns the time-series of each feature (not the mean) for CNN input.
    Includes base MFCCs and their first derivatives (deltas).

    Args:
        audio_segment (np.ndarray): A short audio time series segment containing a drum hit.
        sr (int): The sample rate of the audio segment.

    Returns:
        dict[str, np.ndarray]: A dictionary containing various extracted features.
                              Each feature is returned as a NumPy array (feature_dim x n_frames).
    """
    features = {}

    # Define common FFT parameters for percussive sounds
    N_FFT = 1024 # A common choice for transient analysis
    HOP_LENGTH = 512 # Standard hop_length for N_FFT=1024

    # Handle empty segment case: Return arrays with appropriate dimensions, filled with zeros.
    if audio_segment.size == 0:
        # MFCCs and Delta MFCCs
        features["mfccs"] = np.empty((20, 0)) # n_mfcc x n_frames
        features["delta_mfccs"] = np.empty((20, 0)) # n_mfcc x n_frames
        # Other features (1 dimension per frame)
        features["spectral_centroid"] = np.empty((1, 0))
        features["spectral_rolloff"] = np.empty((1, 0))
        features["zero_crossing_rate"] = np.empty((1, 0))
        features["rms"] = np.empty((1, 0))
        return features
    
    # MFCCs (Mel-frequency cepstral coefficients)
    mfccs = librosa.feature.mfcc(y=audio_segment, sr=sr, n_mfcc=20, n_fft=N_FFT, hop_length=HOP_LENGTH)
    features["mfccs"] = mfccs

    # Delta MFCCs (first derivative of MFCCs)
    delta_mfccs = librosa.feature.delta(mfccs)
    features["delta_mfccs"] = delta_mfccs # Shape (n_mfcc, n_frames)

    # Spectral Centroid
    spectral_centroids = librosa.feature.spectral_centroid(y=audio_segment, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH)
    features["spectral_centroid"] = spectral_centroids

    # Spectral Rolloff
    spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_segment, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH)
    features["spectral_rolloff"] = spectral_rolloff

    # Zero-Crossing Rate
    zcr = librosa.feature.zero_crossing_rate(y=audio_segment, hop_length=HOP_LENGTH)
    features["zero_crossing_rate"] = zcr

    # RMS Energy
    rms = librosa.feature.rms(y=audio_segment, hop_length=HOP_LENGTH)
    features["rms"] = rms

    return features

# The __main__ block remains the same
if __name__ == "__main__":
    print("Running feature_extractor.py example with test.mp3...")
    try:
        from audio_processor.audio_loader import load_audio, normalise_audio
        from audio_processor.onset_detector import detect_onsets

        sr = 22050
        segment_length_seconds = 0.2

        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir, os.pardir))
        test_mp3_path = os.path.join(project_root, "DrumScript/tests", "test.mp3")

        print(f"Attempting to load: {test_mp3_path}")
        audio_data, sample_rate = load_audio(test_mp3_path, sr=sr)
        normalised_audio = normalise_audio(audio_data)
        print(f"Loaded audio: Shape={normalised_audio.shape}, Sample Rate={sample_rate}, Duration={len(normalised_audio)/sample_rate:.2f} seconds")

        print("\nDetecting onsets...")
        onsets = detect_onsets(normalised_audio, sample_rate)
        print(f"Detected {len(onsets)} onsets.")

        if onsets:
            num_onsets_to_process = min(len(onsets), 5)
            for i in range(num_onsets_to_process):
                onset_time = onsets[i]
                onset_sample = int(onset_time * sample_rate)
                segment_length_samples = int(segment_length_seconds * sample_rate)

                segment_start = onset_sample
                segment_end = min(onset_sample + segment_length_samples, len(normalised_audio))
                
                if segment_start >= len(normalised_audio) or segment_end <= segment_start:
                    print(f"  Skipping onset {i+1} at {onset_time:.2f}s: Segment out of bounds or too short.")
                    continue

                audio_segment = normalised_audio[segment_start:segment_end]

                print(f"\n--- Features for Onset {i+1} (at {onset_time:.2f}s) ---")
                if audio_segment.size > 0:
                    features = extract_features(audio_segment, sample_rate)

                    for key, value in features.items():
                        # Now print shape as (feature_dim, n_frames)
                        print(f"  {key}: shape={value.shape}")
                        if value.size > 0:
                            print(f"  {key} (first few values if 1D): {value.flatten()[:5]}") # Flatten to show values
                        else:
                            print(f"  {key}: (empty array with shape {value.shape})")
                    # Assertions should check for consistent number of frames as well, if needed.
                else:
                    print(f"  Onset {i+1} segment is empty, cannot extract features.")
        else:
            print("No onsets detected in the audio, cannot extract features.")

    except FileNotFoundError:
        print(f"\nERROR: The audio file '{test_mp3_path}' was not found.")
        print("Please ensure you have placed 'test.mp3' inside your 'DrumScript/tests/' directory, or updated the relative file_path.")
    except ImportError:
        print("\nERROR: Required modules/libraries might be missing.")
        print("Ensure 'soundfile', 'librosa', 'numpy', and your DrumScript modules are correctly installed and structured.")
        print("For MP3, 'ffmpeg' must also be installed on your system and accessible in PATH.")
    except Exception as e:
        print(f"\nAn unexpected error occurred during the example execution: {e}")
        import traceback
        traceback.print_exc()

    print("\nfeature_extractor.py example finished.")