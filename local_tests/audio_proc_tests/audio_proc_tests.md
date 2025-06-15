#### `audio_processor/audio_loader.py`

```python 
python3 audio_processor/audio_loader.py
```

**expected output:**



    Running audio_loader.py example...
    Created dummy audio file: dummy_audio.wav
    Loaded audio: Shape=(66150,), Sample Rate=22050
    Original max amplitude: 0.5000
    Normalized max amplitude: 1.0000
    Cleaned up dummy audio file: dummy_audio.wav
    audio_loader.py example finished.


```python
python3 audio_processor/feature_extractor.py
```

#### `audio_processor/feature_extractor.py`
**expected output:**

    Running feature_extractor.py example...
    Install 'soundfile' (pip install soundfile) to run this example fully.
    Skipping dummy file creation/deletion.
    feature_extractor.py example finished.

#### `audio_processor/onset_detector.py`
```python
python3 audio_processor/onset_detector.py
````

**expected output:**

    Running onset_detector.py example...
    Created dummy audio file with hits: dummy_audio_with_hits.wav
    Original hit times: [0.5, 1.2, 1.8, 2.5, 3.1, 3.8, 4.4]
    Detected onsets (seconds): ['0.51', '1.21', '1.81', '2.51', '3.11', '3.81', '4.41']
    Cleaned up dummy audio file: dummy_audio_with_hits.wav
    onset_detector.py example finished.