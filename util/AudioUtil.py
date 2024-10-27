import numpy as np
from pedalboard.io import AudioFile
from pedalboard import *
import os
import librosa
# import librosa

def clean_audio(audio_path, output_path):
        # Define chunk size
        chunk_size = 2048
    
        # y is time series - values of waveform at indices indicating the sample number (time * sample rate)
        # y, sr = librosa.load(output_path)
    
        # # preprocessing - make sure y is to scale 1
        # gain_factor = np.mean(abs(y))
        # gain_factor = 1 / gain_factor
    
        # y = y * gain_factor # amplify the audio
    
        # librosa.output.write_wav("tmp.wav", y, sr) # write the audio to a temporary file
        # audio_path = "tmp.wav" # set the audio path to the temporary file
    
        # Load audio file
        sr = 44100
        with AudioFile(audio_path).resampled_to(sr) as f:
            total_frames = f.frames
            audio = np.empty((total_frames, 2))  # Initialize a 2D array to store stereo audio
            frame_index = 0
            found_first_hz = False  # Flag to indicate if we found the first Hz > 0
            found_last_hz = False
            start_index = 0  # To store the index to start writing audio
            end_index = 0
            # Read audio in chunks
            while frame_index < total_frames:
                frames_to_read = min(chunk_size, total_frames - frame_index)
                audio_chunk = f.read(frames_to_read)
                # Ensure audio_chunk is in the right shape for stereo
                if audio_chunk.ndim == 1:  # Check if it's mono
                    audio_chunk = np.column_stack((audio_chunk, audio_chunk))  # Convert to stereo by duplicating the mono channel
                elif audio_chunk.ndim == 2 and audio_chunk.shape[0] == 1:  # Check if it's a single-channel 2D array
                    audio_chunk = np.repeat(audio_chunk, 2, axis=0)  # Convert to stereo
                # Write the audio chunk to the audio array
                audio[frame_index:frame_index + frames_to_read, :] = audio_chunk.T  # Transpose to match shapes
                frame_index += frames_to_read
        # might be a very good idea to utilize threads to do all 3 of these at same time
        maxHz = -1000000
        minHz = 100000000
                
        # Check if any frame has audio (greater than 0)
        for i in range(total_frames):
            if np.any(np.abs(audio[i]) > 0) and not found_first_hz:  # Check if either channel has audio
                found_first_hz = True
                start_index = i
    
            if audio[i,0] > maxHz:
                maxHz = audio[i,0]
    
            if audio[i,0] < minHz:
                minHz = audio[i,0]
    
        for i in range(total_frames - 1, -1, -1):
            if np.any(np.abs(audio[i]) > maxHz/8):
                found_last_hz = True
                end_index = i
                break
            
        # Trim the audio array to only include audio after the first Hz > 0
        if found_first_hz and found_last_hz:
            trimmed_audio = audio[start_index:end_index]
        elif found_first_hz and not found_last_hz:
            trimmed_audio = audio[start_index:]
        elif found_last_hz and not found_first_hz:
            trimmed_audio = audio[0:end_index]
        else:
            trimmed_audio = audio
        # Process the audio with pedalboard
        board = Pedalboard([
            NoiseGate(threshold_db=maxHz-5, ratio=2.5, release_ms=5),
            Compressor(threshold_db=-16, ratio=2.5),
        ])
        effected = board(trimmed_audio, sr)
    
        # Save the trimmed audio
        with AudioFile(
            output_path, 
            'w', 
            sr, 
            num_channels=2  # Ensure this is specified correctly
        ) as f:
            f.write(effected)
    
        # Remove the temporary file
        if os.path.exists("tmp.wav"):
            os.remove("tmp.wav")

def segment_audio(audio_path):
    test_path = audio_path
    output_path = "tmp_trimmed.wav"
    
    clean_audio(test_path, output_path)
    # y is time series - values of waveform at indices indicating the sample number (time * sample rate)
    y, sr = librosa.load(output_path)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # define search intervals for exact beat locations
    search_intervals = []
    bounds = []
    beats = int(np.round((librosa.get_duration(y=y, sr=sr) / (60 / tempo))[0]))

    # convolution
    window_size = 130
    window = np.ones(window_size) / window_size
    y_smooth = np.convolve(abs(y), window, mode='full')
    for i in range(beats):
        samples_per_beat = (60 / tempo) * sr
        baseline = (60 / tempo) * i

        if (i > 0):
            baseline = (60 / tempo) + (bounds[i - 1] / sr)

        search_interval = (baseline * sr) + [-samples_per_beat * 0.1, samples_per_beat * 0.1]
        search_intervals.append(search_interval)

        lower_bound = int(search_interval[0][0])
        upper_bound = int(search_interval[1][0])

        y_slice1 = y_smooth[lower_bound:upper_bound]
        y_slice = y[lower_bound:upper_bound]
        
        if len(y_slice) > 0:
            index = np.where(abs(y_slice1) == min(abs(y_slice1)))[0][0]
            bounds.append(lower_bound + index)
        else:
            bounds.append(0)

    if (os.path.exists(output_path)):
        os.remove(output_path)

    return bounds, y_smooth, sr

def get_notes(audio_path):
    bounds, y_smooth, sr = segment_audio(audio_path)

    notes = ["c", "cis", "d", "dis", "e", "f", "fis", "g", "gis", "a", "ais", "b"]
    chromas = []
    NOTE_DETECTION_THRESHOLD = 0.95 # chromagram confidence threshold for note detection

    chroma = None
    for i in range(len(bounds) - 1):
        lower_bound = bounds[i]
        upper_bound = bounds[i + 1]
        chroma = librosa.feature.chroma_stft(y=y_smooth[lower_bound:upper_bound], sr=sr)

        chromas.append([chroma])
        note_sequence = []
        for j in range(chroma.shape[0]):
            for z in chroma[j]:
                if (z > NOTE_DETECTION_THRESHOLD):
                    note_sequence.append(notes[j])
                    break
        chromas[i].append(note_sequence)

    for k in range(len(chromas)):
        # spec = filtered_chromas[k][0]
        spec = chromas[k][0]
        note_counts = {}

        for i in range(0, len(spec)):
            if 1 in spec[i]:
                note_counts[notes[i]] = 0
                for j in range(len(spec[i])):
                    if spec[i][j] == 1:
                        note_counts[notes[i]] += 1

        for note in note_counts:
            closeness_to_sixteenth = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (0.25))
            closeness_to_triplet = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (0.33))
            closeness_to_eighth = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (0.5))
            closeness_to_quarter = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (1))
            closeness_to_dotted_eight = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (0.75))
            closeness_to_dotted_sixteenth = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))) - (0.375))
            closeness_to_zero = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))))
            min_closeness = min(closeness_to_dotted_eight, closeness_to_dotted_sixteenth, closeness_to_zero, closeness_to_sixteenth, closeness_to_triplet, closeness_to_eighth, closeness_to_quarter)
            if min_closeness == closeness_to_sixteenth:
                note_counts[note] = 16
            elif min_closeness == closeness_to_triplet:
                note_counts[note] = 3
            elif min_closeness == closeness_to_eighth:
                note_counts[note] = 8
            elif min_closeness == closeness_to_quarter:
                note_counts[note] = 4
            elif min_closeness == closeness_to_dotted_eight:
                note_counts[note] = 8.5
            elif min_closeness == closeness_to_dotted_sixteenth:
                note_counts[note] = 16.5
            else:
                note_counts[note] = 0

        note_counts = {k: v for k, v in note_counts.items() if v != 0}
        if np.sum(np.array(list(note_counts.values()))) != 0 and 1 / np.sum(np.array(list(note_counts.values()))) != 0.25:
            if len(note_counts) == 1:
                note_counts[list(note_counts.keys())[0]] = 4
            elif len(note_counts) == 2:
                note_counts[list(note_counts.keys())[0]] = 8
                note_counts[list(note_counts.keys())[1]] = 8
            elif len(note_counts) == 3:
                note_counts[list(note_counts.keys())[0]] = 3
                note_counts[list(note_counts.keys())[1]] = 3
                note_counts[list(note_counts.keys())[2]] = 3
            elif len(note_counts) == 4:
                note_counts[list(note_counts.keys())[0]] = 16
                note_counts[list(note_counts.keys())[1]] = 16
                note_counts[list(note_counts.keys())[2]] = 16
                note_counts[list(note_counts.keys())[3]] = 16
            else:
                note_counts = {k: 16 for k in note_counts}
                del note_counts[list(note_counts.keys())[-1]]
            # display(note_counts)
        # else:
            # display(note_counts)

        # chromas[i] -> specific chroma datapoint
        # chromas[i][0] -> numpy array of confidence values for each note at each time in the slice
        # chromas[i][1] -> list of notes detected in the time slice
        # chromas[i][2] -> dictionary of notes and their corresponding note subdivisions
        chromas[k].append(note_counts)

    output = []
    for chroma in chromas:
        # print(str(chroma) + "\n")
        output.append(chroma[2])

    return output