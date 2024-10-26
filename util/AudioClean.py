import numpy as np
from pedalboard.io import AudioFile
from pedalboard import *
import os

class AudioClean:
    def __init__(self):
        pass

    @staticmethod
    def clean_audio(audio_path, output_path):
        # Define chunk size
        chunk_size = 2048

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

        # Check if any frame has audio (greater than 0)
        for i in range(total_frames):
            if np.any(np.abs(audio[i]) > 0):  # Check if either channel has audio
                found_first_hz = True
                start_index = i
                break
            
        for i in range(total_frames - 1, -1, -1):
            print(i)
            if np.any(np.abs(audio[i]) > 0.1):
                found_last_hz = True
                end_index = i
                break
            
        # Trim the audio array to only include audio after the first Hz > 0
        trimmed_audio = audio[start_index:end_index] if found_first_hz and found_last_hz else audio

        # Process the audio with pedalboard
        board = Pedalboard([
            NoiseGate(threshold_db=13, ratio=3.5, release_ms=0),
            Compressor(threshold_db=-16, ratio=2.5),
            Gain(gain_db=66)
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

        print(f'Trimmed audio length: {len(trimmed_audio)} frames')

