# DrumScript/drum_classifier/model_trainer.py
# __backup4__sat12jul2025__cnn

import os
import numpy as np
import joblib
import json
import pandas as pd
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score
import matplotlib.pyplot as plt # Added for plotting

# Import TensorFlow and Keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv1D, MaxPooling1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.metrics import BinaryAccuracy, Precision, Recall, AUC
from tqdm import tqdm # For progress bars during feature extraction


# --- Configuration ---
SAMPLE_RATE = 22050
SEGMENT_LENGTH_SECONDS = 0.2
# Define all UNIQUE drum types that we expect to classify.
# This must match the ALL_DRUM_TYPES list used in process_enst_dataset.py
ALL_DRUM_TYPES = sorted(['kick', 'snare', 'hi-hat', 'crash', 'ride', 'tom', 'open-hat', 'closed-hat', 'perc', 'tom-floor', 'hi-tom', 'mid-tom'])


# --- Feature Extraction Helper ---
def _extract_features(audio_path, sr, segment_length_seconds):
    """
    Extracts MFCC features from an audio segment.
    """
    try:
        audio, _ = librosa.load(audio_path, sr=sr, mono=True)
        # Ensure the segment has the expected length, pad if necessary
        target_length_samples = int(segment_length_seconds * sr)
        if len(audio) < target_length_samples:
            # Pad with zeros if the segment is too short
            audio = np.pad(audio, (0, target_length_samples - len(audio)), 'constant')
        elif len(audio) > target_length_samples:
            # Trim if the segment is too long
            audio = audio[:target_length_samples]

        if audio.size == 0:
            # Return an array of zeros with the expected feature shape if audio is empty
            # This shape needs to match the input shape of your CNN, e.g., (N_MFCC, N_FRAMES_PER_SEGMENT)
            # For 20 MFCCs and hop_length=512, sr=22050, segment_length_seconds=0.2,
            # n_frames = ceil(target_length_samples / hop_length) = ceil(0.2 * 22050 / 512) = ceil(4410 / 512) = ceil(8.6) = 9
            # So, expected shape is (20, 9)
            n_mfcc = 20 # As defined in your feature_extractor
            n_frames_per_segment = int(np.ceil(target_length_samples / 512)) # Assuming hop_length = 512 from feature_extractor
            return np.zeros((n_mfcc, n_frames_per_segment))


        # Extract MFCCs
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        
        # Normalize MFCCs to a common length for CNN input
        # This is crucial for fixed-size CNN input
        # We need to ensure that the number of frames matches the expected input shape
        n_frames_expected = int(np.ceil(target_length_samples / 512)) # Assuming hop_length = 512
        if mfccs.shape[1] < n_frames_expected:
            mfccs = np.pad(mfccs, ((0, 0), (0, n_frames_expected - mfccs.shape[1])), 'constant')
        elif mfccs.shape[1] > n_frames_expected:
            mfccs = mfccs[:, :n_frames_expected]


        return mfccs
    except Exception as e:
        print(f"Error extracting features from {audio_path}: {e}")
        return None

# --- CNN Model Definition ---
def build_cnn_model(input_shape, num_classes):
    """
    Builds a Convolutional Neural Network (CNN) model for multi-label classification.

    Args:
        input_shape (tuple): Shape of the input features (n_mfcc, n_frames).
        num_classes (int): Number of distinct drum classes.

    Returns:
        tf.keras.Model: Compiled Keras CNN model.
    """
    model = Sequential([
        # Add a Conv1D layer (e.g., 64 filters, kernel size 3)
        # Input shape should be (n_frames, n_mfcc) if data is transposed
        # or (n_mfcc, n_frames) if channels_last is used for Conv1D, often it's (timesteps, features)
        # Let's assume input_shape is (n_mfcc, n_frames) and we'll reshape X_train to (samples, n_frames, n_mfcc)
        # for Conv1D to operate on time-series of features.
        Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(input_shape[1], input_shape[0])), # (n_frames, n_mfcc)
        MaxPooling1D(pool_size=2),
        Dropout(0.3),

        Conv1D(filters=128, kernel_size=3, activation='relu'),
        MaxPooling1D(pool_size=2),
        Dropout(0.3),

        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        # Output layer for multi-label classification
        # 'sigmoid' activation for independent probabilities for each class
        # num_classes should be the total number of drum types (e.g., 6 for kick, snare, hi-hat, crash, ride, tom)
        Dense(num_classes, activation='sigmoid')
    ])

    # Compile the model
    # BinaryCrossentropy is suitable for multi-label classification
    # Metrics for multi-label: BinaryAccuracy, Precision, Recall, AUC
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss=BinaryCrossentropy(),
                  metrics=[BinaryAccuracy(), Precision(), Recall(), AUC(name='auc')])
    return model

# --- New Function to Save and Plot Training History ---
def save_and_plot_training_history(history, output_dir, model_name="drum_classifier"):
    """
    Saves the training history to a CSV and generates plots for loss and accuracy.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save history to CSV
    history_df = pd.DataFrame(history.history)
    history_csv_path = os.path.join(output_dir, f"{model_name}_training_history.csv")
    history_df.to_csv(history_csv_path, index=False)
    print(f"\nTraining history saved to: {history_csv_path}")

    # Plot training & validation accuracy values
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['binary_accuracy'])
    if 'val_binary_accuracy' in history.history:
        plt.plot(history.history['val_binary_accuracy'])
    plt.title(f'{model_name} Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    accuracy_plot_path = os.path.join(output_dir, f"{model_name}_accuracy_plot.png")
    plt.savefig(accuracy_plot_path)
    plt.close()
    print(f"Accuracy plot saved to: {accuracy_plot_path}")


    # Plot training & validation loss values
    plt.figure(figsize=(12, 6))
    plt.plot(history.history['loss'])
    if 'val_loss' in history.history:
        plt.plot(history.history['val_loss'])
    plt.title(f'{model_name} Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Train', 'Validation'], loc='upper left')
    loss_plot_path = os.path.join(output_dir, f"{model_name}_loss_plot.png")
    plt.savefig(loss_plot_path)
    plt.close()
    print(f"Loss plot saved to: {loss_plot_path}")

    # Plot AUC (Area Under Curve) if available
    if 'auc' in history.history:
        plt.figure(figsize=(12, 6))
        plt.plot(history.history['auc'])
        if 'val_auc' in history.history:
            plt.plot(history.history['val_auc'])
        plt.title(f'{model_name} Model AUC')
        plt.ylabel('AUC')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Validation'], loc='upper left')
        auc_plot_path = os.path.join(output_dir, f"{model_name}_auc_plot.png")
        plt.savefig(auc_plot_path)
        plt.close()
        print(f"AUC plot saved to: {auc_plot_path}")

    print("\nTraining plots generated. Examine them to assess overfitting/underfitting.")


# --- Main Training and Evaluation Function ---
def train_and_evaluate_model(data_dir: str, model_save_path: str, scaler_save_path: str, label_map_save_path: str):
    """
    Loads processed data, trains a multi-label CNN classifier, and evaluates it.
    """
    print("--- Starting Model Training and Evaluation ---")
    print(f"Data directory: {data_dir}")

    processed_data_path = os.path.join(data_dir, "ENST_processed", "multi_label_events.csv")
    audio_segments_dir = os.path.join(data_dir, "ENST_processed", "audio_segments")

    if not os.path.exists(processed_data_path):
        raise FileNotFoundError(f"Processed data CSV not found: {processed_data_path}\n"
                                f"Please run process_enst_dataset.py first to generate the data.")

    df = pd.read_csv(processed_data_path)

    # Prepare features and labels
    X = []
    y = [] # This will store multi-hot encoded labels

    # Create a mapping from drum type string to integer index
    label_map = {drum_type: i for i, drum_type in enumerate(ALL_DRUM_TYPES)}
    inverse_label_map = {i: drum_type for drum_type, i in label_map.items()}
    num_classes = len(ALL_DRUM_TYPES)

    print(f"Preparing dataset for {len(df)} samples...")
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Extracting features for training"):
        audio_file_name = row['audio_file']
        audio_path = os.path.join(audio_segments_dir, audio_file_name)

        features = _extract_features(audio_path, SAMPLE_RATE, SEGMENT_LENGTH_SECONDS)
        if features is None:
            continue
        
        # Ensure features have the correct shape (n_mfcc, n_frames)
        # The CNN expects (n_frames, n_mfcc) for Conv1D input_shape
        # So we will transpose it later after scaling.
        # For now, ensure features are consistent.
        # We need to know the expected n_frames based on SEGMENT_LENGTH_SECONDS and HOP_LENGTH (512)
        target_length_samples = int(SEGMENT_LENGTH_SECONDS * SAMPLE_RATE)
        n_frames_expected = int(np.ceil(target_length_samples / 512)) # Assuming hop_length = 512 from feature_extractor

        if features.shape[1] != n_frames_expected:
             # This should ideally not happen if _extract_features pads/trims correctly
             print(f"Warning: Feature shape mismatch for {audio_file_name}. Expected {n_frames_expected} frames, got {features.shape[1]}. Skipping.")
             continue
        
        X.append(features.flatten()) # Flatten for StandardScaler, will reshape for CNN later

        # Create multi-hot encoded label
        current_labels = row['drum_types'].split(',') # Assuming drum_types is a comma-separated string
        multi_hot_label = np.zeros(num_classes, dtype=int)
        for label in current_labels:
            label = label.strip()
            if label in label_map:
                multi_hot_label[label_map[label]] = 1
            else:
                print(f"Warning: Unknown drum type '{label}' found in data. Skipping.")
        y.append(multi_hot_label)

    X = np.array(X)
    y = np.array(y)

    if X.size == 0:
        print("No valid features extracted. Cannot proceed with training. Check data and feature extraction.")
        return

    print(f"Total samples for training: {len(X)}")
    print(f"Feature matrix shape (X): {X.shape}")
    print(f"Labels matrix shape (y): {y.shape}")

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Reshape X_scaled for CNN input: (samples, n_frames, n_mfcc)
    # Original X was (samples, n_mfcc * n_frames_expected) flattened
    # We need to reshape back to (samples, n_frames_expected, n_mfcc)
    # This assumes features[0] is (n_mfcc, n_frames_expected)
    n_mfcc = features.shape[0] if X.size > 0 else 20 # Get n_mfcc from an actual feature, fallback to 20
    X_reshaped = X_scaled.reshape(len(X_scaled), n_frames_expected, n_mfcc)
    print(f"Reshaped feature matrix for CNN (X_reshaped): {X_reshaped.shape}")


    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_reshaped, y, test_size=0.2, random_state=42)

    print(f"Training data shape: {X_train.shape}, {y_train.shape}")
    print(f"Test data shape: {X_test.shape}, {y_test.shape}")

    # Build and train the model
    model = build_cnn_model(input_shape=(n_mfcc, n_frames_expected), num_classes=num_classes)
    model.summary()

    print("\nTraining CNN model...")
    # Add validation_data for monitoring during training
    history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test), verbose=1)

    print("\n--- Training Complete ---")

    # Evaluate the model on the test set
    print("\n--- Evaluating Model ---")
    loss, binary_accuracy, precision, recall, auc = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss: {loss:.4f}")
    print(f"Test Binary Accuracy: {binary_accuracy:.4f}")
    print(f"Test Precision: {precision:.4f}")
    print(f"Test Recall: {recall:.4f}")
    print(f"Test AUC: {auc:.4f}")

    # Generate predictions for classification report
    y_pred_probs = model.predict(X_test)
    # Convert probabilities to binary predictions (multi-label)
    # A common threshold is 0.5, but this can be tuned
    y_pred_binary = (y_pred_probs > 0.5).astype(int)

    print("\n--- Classification Report (Threshold > 0.5) ---")
    # Use target_names for a more readable report
    report = classification_report(y_test, y_pred_binary, target_names=ALL_DRUM_TYPES, zero_division=0)
    print(report)

    # Save the trained model, scaler, and label map
    print("\n--- Saving Model Components ---")
    model.save(model_save_path) # Saves Keras model
    joblib.dump(scaler, scaler_save_path) # Saves StandardScaler
    with open(label_map_save_path, 'w') as f:
        json.dump(label_map, f) # Saves label mapping

    print(f"Model saved to: {model_save_path}")
    print(f"Scaler saved to: {scaler_save_path}")
    print(f"Label map saved to: {label_map_save_path}")

    # --- New: Save and Plot Training History ---
    # Determine the output directory for logs and plots
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))
    output_logs_dir = os.path.join(project_root, "outputs", "training_logs")
    save_and_plot_training_history(history, output_logs_dir, model_name="multi_label_drum_classifier")

    print("\n---------------------------------------------------")
    print("--- Model Training and Evaluation finished. ---")
    print("---------------------------------------------------\n")
    print("Interpretation of Results:")
    print("--------------------------")
    print("1.  **Test Metrics:**")
    print(f"    - **Binary Accuracy ({binary_accuracy:.4f}):** This is the proportion of correctly predicted labels (considering each drum type independently). A higher value is better.")
    print(f"    - **Precision ({precision:.4f}):** When the model predicts a drum type, how often is it correct? (True Positives / (True Positives + False Positives)). High precision means fewer false alarms.")
    print(f"    - **Recall ({recall:.4f}):** Of all the actual occurrences of a drum type, how many did the model correctly identify? (True Positives / (True Positives + False Negatives)). High recall means fewer missed drum hits.")
    print(f"    - **AUC ({auc:.4f}):** Area Under the Receiver Operating Characteristic (ROC) curve. It measures the ability of the model to distinguish between classes. Higher AUC (closer to 1.0) indicates better performance.")
    print(f"    - **Loss ({loss:.4f}):** A measure of how well the model is performing. Lower loss is better.")
    print("\n2.  **Classification Report:**")
    print("    - Provides precision, recall, f1-score, and support for each individual drum type.")
    print("    - **F1-score:** The harmonic mean of precision and recall. A balanced metric, good for imbalanced datasets.")
    print("    - **Support:** The number of actual occurrences of each drum type in the test set.")
    print("    - Look for consistent high F1-scores across all drum types. If some drum types have significantly lower scores, the model might struggle with them (e.g., due to less training data or similar sounds to other drums).")
    print("\n3.  **Training Plots (in 'outputs/training_logs/'):**")
    print("    - **Accuracy and Loss Curves:** Examine the 'multi_label_drum_classifier_accuracy_plot.png' and 'multi_label_drum_classifier_loss_plot.png'.")
    print("    - **Validation vs. Training:**")
    print("        - If the validation curve closely follows the training curve, the model is generalizing well.")
    print("        - If the training curve continues to improve but the validation curve plateaus or gets worse, it indicates **overfitting**. You might need to add more dropout, reduce model complexity, or get more diverse training data.")
    print("        - If both curves are flat and low, it indicates **underfitting**. The model might be too simple, or needs more training epochs or a higher learning rate.")
    print("    - **AUC Curve:** Provides insight into the model's overall discriminative power during training.")
    print("\nConsider adjusting hyperparameters (epochs, batch size, learning rate, CNN layers/filters) and model architecture if the performance is not satisfactory.")


if __name__ == "__main__":
    # Determine project root dynamically
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level from drum_classifier/ to DrumScript/
    project_root = os.path.abspath(os.path.join(current_script_dir, os.pardir))

    # Define paths for data and saved models
    data_directory = os.path.join(project_root, "training_data") # Points to 'training_data' which contains 'ENST_processed'
    model_save_directory = os.path.join(project_root, "models")
    
    # Ensure 'models' directory exists
    os.makedirs(model_save_directory, exist_ok=True)

    # File paths for saving
    model_file = os.path.join(model_save_directory, "multi_label_drum_classifier_model.h5") # Changed extension for Keras model
    scaler_file = os.path.join(model_save_directory, "multi_label_scaler.joblib")
    label_map_file = os.path.join(model_save_directory, "multi_label_label_map.json")

    try:
        train_and_evaluate_model(
            data_dir=data_directory,
            model_save_path=model_file,
            scaler_save_path=scaler_file,
            label_map_save_path=label_map_file
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please make sure you have run `process_enst_dataset.py` to prepare the data in `training_data/ENST_processed`.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()