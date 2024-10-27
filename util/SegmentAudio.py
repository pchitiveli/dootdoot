import librosa
import numpy as np
import os

def segment_audio(audio_path):
    test_path = audio_path
    output_path = "tmp_out.wav"
    
    audio_clean(test_path, output_path)
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

    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    chromas = []
    NOTE_DETECTION_THRESHOLD = 0.8 # chromagram confidence threshold for note detection

    chroma = None
    for i in range(len(bounds) - 1):
        lower_bound = bounds[i]
        upper_bound = bounds[i + 1]
        chroma = librosa.feature.chroma_stft(y=y_smooth[lower_bound:upper_bound], sr=sr)

        # plt.figure()
        # librosa.display.specshow(chroma, y_axis='chroma', x_axis='time')
        # plt.vlines([(60 / tempo) * i, (60 / tempo) * (i + 1)] - ((60 / tempo) * i), 0, 5, color='r', linestyle='--')
        # plt.colorbar()

        chromas.append([chroma])
        note_sequence = []
        for j in range(chroma.shape[0]):
            if np.mean(chroma[j]) > NOTE_DETECTION_THRESHOLD:
                note_sequence.append(notes[j])
                chromas[i].append(note_sequence[-1])
                break

    # Filter out beats with clear quarter notes and focus on beats with potential multiple notes
    # filtered_chromas = []
    # for chroma in chromas:
    #     chroma_rows = chroma[0]
    #     i = 0
    #     for row in chroma_rows:
    #         if (1 in row):
    #             i += 1
    #         if i > 1:
    #             filtered_chromas.append(chroma)
    #             break
    # for k in range(len(filtered_chromas)):

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
            closeness_to_zero = abs((int(note_counts[note]) / np.sum(np.array(list(note_counts.values())))))
            if min(closeness_to_zero, closeness_to_sixteenth, closeness_to_triplet, closeness_to_eighth, closeness_to_quarter) == closeness_to_sixteenth:
                note_counts[note] = 16
            elif min(closeness_to_zero, closeness_to_sixteenth, closeness_to_triplet, closeness_to_eighth, closeness_to_quarter) == closeness_to_triplet:
                note_counts[note] = 12
            elif min(closeness_to_zero, closeness_to_sixteenth, closeness_to_triplet, closeness_to_eighth, closeness_to_quarter) == closeness_to_eighth:
                note_counts[note] = 8
            elif min(closeness_to_zero, closeness_to_sixteenth, closeness_to_triplet, closeness_to_eighth, closeness_to_quarter) == closeness_to_quarter:
                note_counts[note] = 4
            else:
                note_counts[note] = 0

        note_counts = {k: v for k, v in note_counts.items() if v != 0}
        if 1 / np.sum(np.array(list(note_counts.values()))) != 0.25:
            if len(note_counts) == 1:
                note_counts[list(note_counts.keys())[0]] = 4
            elif len(note_counts) == 2:
                note_counts[list(note_counts.keys())[0]] = 8
                note_counts[list(note_counts.keys())[1]] = 8
            elif len(note_counts) == 3:
                note_counts[list(note_counts.keys())[0]] = 12
                note_counts[list(note_counts.keys())[1]] = 12
                note_counts[list(note_counts.keys())[2]] = 12
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

    if (os.exists(output_path)):
        os.remove(output_path)

    return [chromas[i][2] for i in range(len(chromas))]