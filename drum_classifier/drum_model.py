# DrumScript/drum_classifier/drum_model.py

import os
import numpy as np
import joblib  # For loading StandardScaler
import json    # For loading label map
import tensorflow as tf
from tensorflow.keras.models import load_model # For loading Keras H5 model

class DrumClassifier:
    """
    A class to encapsulate the drum classification model for CNNs.
    Loads a pre-trained Keras model, a StandardScaler, and a label map for prediction.
    """
    def __init__(self, model_path: str, scaler_path: str, label_map_path: str):
        """
        Initialises the DrumClassifier with paths to the pre-trained Keras model,
        StandardScaler, and label map.

        Args:
            model_path (str): Path to the saved Keras model (.h5 file).
            scaler_path (str): Path to the saved StandardScaler (.joblib file).
            label_map_path (str): Path to the saved label map (.json file).
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Keras model file not found: {model_path}")
        if not os.path.exists(scaler_path):
            raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
        if not os.path.exists(label_map_path):
            raise FileNotFoundError(f"Label map file not found: {label_map_path}")

        print(f"Loading Keras model from: {model_path}")
        self.model = load_model(model_path)
        print(f"Loading scaler from: {scaler_path}")
        self.scaler = joblib.load(scaler_path)
        
        print(f"Loading label map from: {label_map_path}")
        with open(label_map_path, 'r') as f:
            self.label_map = json.load(f)
        
        # Invert label map for easy lookup from model output index to drum type
        # The labels should be sorted consistently with how they were sorted during training
        # (e.g., from ALL_DRUM_TYPES in model_trainer.py)
        self.idx_to_label = {idx: label for label, idx in self.label_map.items()}
        self.sorted_labels = sorted(self.label_map.keys(), key=lambda x: self.label_map[x])
        self.num_classes = len(self.label_map)

        print("Model Components Loaded Successfully.")

    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Predicts drum types for given input features using the loaded CNN model.

        The input features are expected to be in the format (n_samples, n_timesteps, n_features_per_timestep).
        The StandardScaler expects 2D input (n_samples * n_timesteps, n_features_per_timestep),
        so reshaping is performed before and after scaling.

        Args:
            features (np.ndarray): Input features for prediction.
                                   Expected shape: (n_samples, n_timesteps, n_features_per_timestep).

        Returns:
            np.ndarray: Predicted binary labels (0 or 1) for each drum type for each sample.
                        Shape: (n_samples, num_classes).
        """
        # Ensure features are float32 for TensorFlow model compatibility
        features = features.astype(np.float32)

        # Store original shape for reshaping back after scaling
        original_shape = features.shape
        n_samples = original_shape[0]
        # n_timesteps = original_shape[1] # Not directly used for the reshape, but good for context
        n_features_per_timestep = original_shape[2]

        # Reshape for StandardScaler: (n_samples * n_timesteps, n_features_per_timestep)
        # This flattens the time steps for each sample into a continuous stream for scaling
        reshaped_features_for_scaling = features.reshape(-1, n_features_per_timestep)
        
        # Apply the scaler transformation
        scaled_features = self.scaler.transform(reshaped_features_for_scaling)

        # Reshape back for the CNN: (n_samples, n_timesteps, n_features_per_timestep)
        # The number of timesteps must be preserved for the CNN input layer
        scaled_features_for_cnn = scaled_features.reshape(original_shape)

        # Make predictions (probabilities for multi-label classification)
        predictions_proba = self.model.predict(scaled_features_for_cnn)

        # Convert probabilities to binary labels (0 or 1) based on a threshold
        # A threshold of 0.5 is common for multi-label binary classification
        predictions_binary = (predictions_proba > 0.5).astype(int)

        return predictions_binary

    def get_drum_types_from_predictions(self, binary_predictions: np.ndarray) -> list[list[str]]:
        """
        Converts binary predictions (0s and 1s) into human-readable drum type labels.

        Args:
            binary_predictions (np.ndarray): A 2D array of binary predictions (n_samples, num_classes).

        Returns:
            list[list[str]]: A list where each inner list contains the drum types predicted for that sample.
                             For example: [['kick'], ['snare', 'hi-hat'], []].
        """
        results = []
        for sample_prediction in binary_predictions:
            active_drums = []
            for i, is_active in enumerate(sample_prediction):
                if is_active == 1:
                    # Use the sorted_labels list to map index back to drum type
                    active_drums.append(self.sorted_labels[i])
            results.append(active_drums)
        return results

    # The 'train', 'save_model', and 'load_model' (static) methods from the RandomForest version
    # are not needed here, as training and model saving are handled by model_trainer.py
    # and loading is done in the __init__ method.