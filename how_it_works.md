# **`DrumScript`: How it works**


<!--date_created: tues-24-june-2025-->
<!--date_updated: weds-25-june2025-->
**Description:** This document serves dual purpose:

1) It outlines the purpose of **specific modules** in `DrumScript`, object-wise.
2) It outlines key definitions to **clarify the methodology used**.

---
## `DrumScript`: How it works
## `audio_processor/`

**Module overview** 

 - Find where the **drum hits actually occur** (ie. `onset_events`)
 - Extract **numerical features** from these *events*

---

## `drum_classifier/`

**Module overview** 

- Prepares the audio features imported using `audio_processor` module **into a format that a machine-learning model** can recognise.
- Uses the **transformed, structured training data** to **train** a chosen machine-learning model.
- Compiles an **entirely new** model based on model training (`model_trainer.py`) that can make **predictive** judgements on **new audio inputs**

### `data_preparer.py`

This is the **raw material processor**. It's main job is to take your **raw audio files** (like `.mp3`) and turn them into a **structured dataset ready for machine-learning**. Specifically, `data_preparer.py`:

-  Organise these **features**  - and their corresponding drum labels **per the training data** (e.g. *snare*, *hi-hat*) - into a **format that a machine-learning model can understand**)
  >
 - Scales these features and **saves the scaling information and label mapping** for later use, ie in the **[`model_trainer.py`](#model_trainerpy) and [`drum_model.py`](#drum_modelpy)** modules.

<!--**Depends on:**--maybe add in later :)-->

### `model_trainer.py`

This is where we **train the machine-learning model** using the **transformed training data** from `data_preparer.py` . It uses this data **teach a machine-learning model** how to **recognise different drum sounds**. Specifically, `model_trainer.py`:

- Feeds the **features and labels** into a **chosen machine-learning model** (for now, this is standard **RandomForestClassifier**, but could equally be a **Support Vector** or **Neural Network** (aka. *Deep Learning*) models.
>
- During training, the model learns patterns that distinguish one **drum sound from another**.
>
- Once **model training is complete**, it saves the trained mo**del, ready for use in **identifying new drum sounds.

### `drum_model.py`

This is the **trained model** applied to new audio recordings. It uses the outputs from `model_trainer.py` to make statistical inference-based judgment on new audio recordings or uploads. Specifically, `drum_model.py`:

 - Loads the **chosen machine learning model**, created by `model_trainer.py`
 - Takes new audio (imported using the `audio_processor` module) to **predict which part of the drums is being played**
> 
---
---
>
# **`DrumScript`: Glossary of Terms**

## [`librosa`](#librosa)
   - [`librosa`](https://librosa.org/doc/latest/advanced.html) is a popular open-source Python library for **audio and music analysis**. It is a **powerful toolkit** that helps you **process, analyse**, and understand **sound**.
   - `librosa` provides a wide **range of Python functions** for common tasks in **music information retrieval (MIR)** and **audio processing**, such as:
     - **Loading audio files:** Reading various audio formats (`.wav`, `.MP3`, etc.) into a format Python can easily work with.
     - **Feature extraction:** Converting raw audio into meaningful numerical descriptions (features) that machine learning models can understand, like **MFCCs (Mel-frequency cepstral coefficients)**, **spectral centroid**, **rhythm features**, etc.
     - **Time-frequency analysis**: Analysing how the **frequency content of sound** changes over time (e.g., creating **spectrograms**).
     - **Beat and tempo detection:** Identifying the pulse or speed of music.
     - **Pitch tracking:** Estimating the **fundamental frequency** of a **sound**.
     - **Onset detection:** Finding the **precise moments where sounds begin** (like a *snare hit*).

  In `DrumScript`, `librosa` is crucial because it's the underlying library that `audio_loader.py`, `feature_extractor.py`, and `onset_detector.py` use to actually perform the **low-level audio processing** and extract the characteristics of your **drum sound** and **audio recordings**

## `sample_rate` (`sr`)
  * **Meaning:** How many *snapshots* of the sound wave are taken per second when audio is digitised. A higher number means more detail.
>
  * **Example:** 
  >
    > If **`sr = 22050 (Hz)`**, it means **`22,050`** sound measurements are recorded **every second**.
>
  * **Example:** 
>
    > If **`sr=22050 (Hz),`** and the **`input_signal`** of **one of your drum notes** is *`1744 milliseconds`* in length, then your **`sample_rate = ~38450 samples`**

## `audio_segment`
  * **Meaning:** A specific, short clip or piece of sound extracted from a larger audio file. This is the part you're currently analysing.
>
  * **Example:**
> 
>   A **`200-millisecond`** (or, `0.2 second`)-long clip of a snare drum hit.

## `n_fft`
  * **Meaning:** `n_fft` = **Number of Fast Fourier Transform** points. The size of the *listening window* (in number of samples) that is used to analyse the frequency content of an `audio_segment`.
>
  * **Example:** 
  > If **`n_fft= 2048`**, the analysis looks at **2048 samples** **at a time** to determine frequencies. If your `audio_segment` is **shorter than 2048 samples**, you get a warning.

## `hop_length`
  * **Meaning:** How far the *listening window* (`n_fft`) slides forward (in number of samples) to take the next frequency snapshot.
>
  * **Example:** 
> If `hop_length=512`, the window (or `object_event`) moves **512 samples to the right** for the next analysis, overlapping with the previous window (`object_event`).

  * Playing around with the `hop_length` is often crucial for finding the right split of intervals in a given audio sample. 
---
<!--END--->