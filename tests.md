## **Testing Documentation**

<!--date_created: sat-21-june-2025-->
<!--date_updated: thurs-26-june-2025-->

`DrumScript` is a `Python package` that **converts drum audio recordings into sheet music (drum notation) in PDF format**. 

It leverages **advanced audio signal processing** and **machine learning** to detect individual drum hits (kick, snare, hi-hat, etc.) and translate them into a musical score.

**[Package Structure](repository_structure.md)** **[~ README](README.md)**

---
### Modules

#### **`audio_processor/`**

#####  `audio_loader.py`


```
python3 audio_processor/audio_loader.py
```


**expected output:**

    Running audio_loader.py example with actual MP3/WAV...
    Attempting to load: ~DrumScript/tests/test.mp3
    Loaded audio: Shape=(324288,), Sample Rate=22050, Duration=14.71 seconds
    Original max amplitude: 0.9660
    Normalised max amplitude: 1.0000
        
    Playing loaded (and normalised) audio...
        
    # test.mp3 will play


    Audio playback finished.
    audio_loader.py example finished.



##### `feature_extractor.py` 

```
python3 audio_processor/feature_extractor.py
```

**expected output:**

```
    Running feature_extractor.py example...
    Install 'soundfile' (pip install soundfile) to run this example fully.
    Skipping dummy file creation/deletion.
    feature_extractor.py example finished.
    DrumScript %
```
or, to run `feature_extractor.py` as a **module**

```
python -m audio_processor.feature_extractor
```

**expected output:**

```
DrumScript % python -m audio_processor.feature_extractor 
Running feature_extractor.py example with test.mp3...
Attempting to load: DrumScript/tests/test.mp3
Loaded audio: Shape=(324288,), Sample Rate=22050, Duration=14.71 seconds

Detecting onsets...
Detected 68 onsets.

--- Features for Onset 1 (at 0.07s) ---
  mfccs: shape=(180,), mean=8.2517
  spectral_centroid: shape=(9,), mean=2826.1621
  spectral_rolloff: shape=(9,), mean=6810.4736
  zero_crossing_rate: shape=(9,), mean=0.1527
  rms: shape=(9,), mean=0.2310

--- Features for Onset 2 (at 0.28s) ---
  mfccs: shape=(180,), mean=7.4435
  spectral_centroid: shape=(9,), mean=2350.6134
  spectral_rolloff: shape=(9,), mean=6206.3477
  zero_crossing_rate: shape=(9,), mean=0.0832
  rms: shape=(9,), mean=0.2055

--- Features for Onset 3 (at 0.49s) ---
  mfccs: shape=(180,), mean=4.0245
  spectral_centroid: shape=(9,), mean=3365.3937
  spectral_rolloff: shape=(9,), mean=7028.1982
  zero_crossing_rate: shape=(9,), mean=0.1779
  rms: shape=(9,), mean=0.1064

--- Features for Onset 4 (at 0.70s) ---
  mfccs: shape=(180,), mean=4.8659
  spectral_centroid: shape=(9,), mean=2100.4735
  spectral_rolloff: shape=(9,), mean=5347.4121
  zero_crossing_rate: shape=(9,), mean=0.0668
  rms: shape=(9,), mean=0.2111

--- Features for Onset 5 (at 0.79s) ---
  mfccs: shape=(180,), mean=1.0935
  spectral_centroid: shape=(9,), mean=2497.4780
  spectral_rolloff: shape=(9,), mean=5926.4160
  zero_crossing_rate: shape=(9,), mean=0.0850
  rms: shape=(9,), mean=0.1392

feature_extractor.py example finished.
DrumScript % 
```

##### `onset_detector.py`
```
python3 audio_processor/onset_detector.py
```

**expected output:**

    Running onset_detector.py example...
    Created dummy audio file with hits: dummy_audio_with_hits.wav
    Original hit times: [0.5, 1.2, 1.8, 2.5, 3.1, 3.8, 4.4]
    Detected onsets (seconds): ['0.51', '1.21', '1.81', '2.51', '3.11', '3.81', '4.41']
    Cleaned up dummy audio file: dummy_audio_with_hits.wav
    onset_detector.py example finished.

or, to run `onset_detector.py` as a **module**


```
python3 -m audio_processor.onset_detector
```
**expected output:**

```zsh
DrumScript % python3 -m audio_processor.onset_detector
Running onset_detector.py example with test.mp3...
Attempting to load: ~/DrumScript/tests/test.mp3
Loaded audio: Shape=(324288,), Sample Rate=22050, Duration=14.71 seconds

Detecting onsets from test.mp3...
Detected 68 onsets.

First 10 detected onsets (seconds):
  Onset 1: 0.07s
  Onset 2: 0.28s
  Onset 3: 0.49s
  Onset 4: 0.70s
  Onset 5: 0.79s
  Onset 6: 0.88s
  Onset 7: 1.32s
  Onset 8: 1.51s
  Onset 9: 1.74s
  Onset 10: 1.90s
  ...and 58 more onsets.

onset_detector.py example finished.
DrumScript %  -
```

#### **`drum_classifier/`**

#####  `data_preparer.py`

```
python3 drum_classifier/model_trainer.py
```

...or, to run `data_preparer.py` as a **module**:

```
python3 -m drum_classifier.model_trainer
```

**expected output:**

```
(DrumScript) DrumScript % python3 -m drum_classifier.data.preparer.py
Preparing dataset from: DrumScript/training_data
  Processing 'bass_drum' sounds...
  Processing 'closed_hi_hat' sounds..

Finished data preparation.
Total samples: 2519
Feature dimension: 24
Labels processed: {'bass_drum': 0, 'closed_hi_hat': 1, 'crash': 2, 'dbl_bass_drum': 3, 'kick': 4, 'open_hi_hat': 5, 'ride': 6, 'snare': 7}
Features scaled using StandardScaler.

Data preparation successful!
Feature matrix shape (X): (2519, 24)
Labels vector shape (y): (2519,)
Label mapping: {'bass_drum': 0, 'closed_hi_hat': 1, 'crash': 2, 'dbl_bass_drum': 3, 'kick': 4, 'open_hi_hat': 5, 'ride': 6, 'snare': 7}
Scaler saved to: ~~DrumScript/models/scaler.joblib
Label map saved to: ~DrumScript/models/label_map.json
```

> **NOTE:** 
> 
> While running `data_preparer.py` you may currently get an error (or errors) like this:
> ```
> DrumScript/.venv/lib/python3.12/site-packages/librosa/core/spectrum.> py:266: UserWarning: n_fft=2048 is too large for input signal of length=1274
> ```
> This warning message tells you the following:
> * **`n_fft=2048`**: This is the **`Fast Fourier Transform (FFT)` window size** that `librosa` is trying to use for its frequency analysis. It means `librosa` is trying to analyse a segment of sound that is 2048 samples long.
> * **`input signal of length=1274`**: This indicates that the specific  >  audio segment `librosa` received for processing *at that moment* was only **1274 samples long**, ie. the labelled audio sample was *too short*
> * **`n_fft is too large for input signal`**: This is the core of the warning. It means the window size (`n_fft`) chosen for the frequency > analysis is larger than the actual piece of sound it's trying to analyze (the `input signal of length`).
> 
> **Solution:** 
> 
>Re-run `feature_extractor.py` with **a smaller value** for `n_fft`

<!--In simple terms, your `feature_extractor.py` (which uses `librosa`) is trying to put a *listening window* of 2048 samples over a sound clip that is only 1274 samples long. While `librosa` will still try to perform the calculation (often by padding the shorter signal with zeros), this warning signals that the chosen `n_fft` might be too large for some of the very short drum hits or segments your `onset_detector` is extracting, potentially leading to less ideal feature extraction for those specific short sounds.--->

Once you run `data_preparer.py`, you will have a new folder in the root called `models` and, in that folder, two files: 
 - `/label_map.json`:
>

  ```json
  {"bass_drum": 0, "closed_hi_hat": 1, "crash": 2, "dbl_bass_drum": 3, "kick": 4, "open_hi_hat": 5, "ride": 6, "snare": 7}
  ```
  `label_map.json`  stores a **mapping between the human-readable drum labels** (like *snare*, *kick*, *closed_hi_hat*) and the **integer (*numerical*) representations** that a machine learning model can understand.

- `/scaler.joblib`:
>
   `scaler.joblib` stores the **parameters (*mean* and *standard deviation (s.d)*) of the `StandardScaler`** that was used to **normalise your features during data preparation**.


> **IMPORTANT NOTE:**
>
>It is absolutely critical that any new audio data you feed into your trained `drum_model.py` for prediction is scaled using the **exact same scaling parameters** as the `Data the model was trained on`. 
>
>`drum_model.py` will load this `scaler.joblib` file to apply the identical scaling transformation to new drum sound features, ensuring the model receives data in the expected range. 
>
>Without **consistent scaling, the model's predictions would be inaccurate**.
>
#####  `model_trainer.py`

```
python3 drum_classifier/model_trainer.py
```


...or, to run `model_trainer.py` as a **module**:

```
python3 -m drum_classifier.model_trainer
```

**expected output:**

```
Preparing dataset from: ~~DrumScript/training_data
  Processing 'bass_drum' sounds...
  Processing 'closed_hi_hat' sounds...
  Processing 'crash' sounds...
  Processing 'dbl_bass_drum' sounds...
  Processing 'kick' sounds...
  Processing 'open_hi_hat' sounds...
  Processing 'ride' sounds...
  Processing 'snare' sounds...

  Finished data preparation.
  Total samples: 2519
  Feature dimension: 24
  Labels processed: {'bass_drum': 0, 'closed_hi_hat': 1, 'crash': 2, 'dbl_bass_drum': 3, 'kick': 4, 'open_hi_hat': 5, 'ride': 6, 'snare': 7}
  Features scaled using StandardScaler.

  Training set size: 2015 samples
  Test set size: 504 samples
  Initialized DrumClassifier with model type: random_forest
  Training random_forest model...
  Model training complete.

  Model Evaluation (random_forest):
  Accuracy: 0.9782

  Classification Report:
  ~/DrumScript/.venv/lib/python3.12/site-packages/sklearn/metrics/_classification.py:2939: UserWarning: labels size, 4, does not match size of target_names, 8
    warnings.warn(
                precision    recall  f1-score   support

      bass_drum       0.94      0.92      0.93        48
  closed_hi_hat       0.99      0.98      0.99       150
          crash       0.95      0.86      0.90        22
  dbl_bass_drum       0.98      1.00      0.99       284

      accuracy                           0.98       504
      macro avg       0.96      0.94      0.95       504
  weighted avg       0.98      0.98      0.98       504


  Saving model assets...
  Model saved to: ~DrumScript/models/drum_classifier_model.joblib
  Scaler saved to: ~DrumScript/models/scaler.joblib
  Label map saved to: ~DrumScript/models/label_map.json

  Model training and evaluation finished.
```

<!---Once `model_trainer.py` has run to completion, here is an overview of what it will have done:

  * **Data preparation:**
    *  The script successfully loaded and processed your drum sound samples from `/training_data`, extracting 24 features for each.
    *  It will have identified all drum labels and applied `StandardScaler` to your features.
* **Model training:**
    * Your dataset was split into a training set of n samples and a test set of x samples.
    * A `random_forest` model was initialised and trained successfully.
    * The model achieved a very high **Accuracy of 0.9782** on the test set.
* **Classification report:**
    * The `UserWarning: labels size, 4, does not match size of target_names, 8` is expected and indicates that your current *test split* happened to only contain 4 of your 8 drum classes. This is common with random splits, especially if some classes have fewer samples.
    * Despite this, the report successfully shows detailed metrics (*precision*, *recall*, **f1-score**, and *support*) for the 4 classes present in your test set (ie.'bass_drum', 'closed_hi_hat', 'crash', and 'dbl_bass_drum'). The high scores for these categories confirm the model is performing well on the data it was tested against.
* **Model assets saved:**
    * Your trained model (`drum_classifier_model.joblib`), the scaler (`scaler.joblib`), and the label map (`label_map.json`) have all been successfully saved into your `models/` directory. These files are essential for using your model to classify new drum sounds in the future.
>-->
   You should now have a **trained model** for use! :) 

> **Please note:** The model **currently being used/tested** is a **`RandomClassifier` model**. This may change as package development progresses.

---
<!--END-->