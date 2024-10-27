import numpy as np
from pedalboard.io import AudioFile
from pedalboard import *
import os
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
        else:
            print("The file does not exist")