# Audio to Text - By Pej - 100% Local

import whisper
import os
from pydub import AudioSegment
from pydub.utils import make_chunks
import time

class AudioTranscriber:
    def __init__(self, model_size="base"):
        """
        Initialize the transcriber with a Whisper model.

        Args:
            model_size (str): Whisper model size - "tiny", "base", "small", "medium", "large"
        """
        print(f"Loading Whisper model: {model_size}")
        self.model = whisper.load_model(model_size)
        print("Model loaded successfully!")

    def split_audio(self, audio_path, chunk_length_ms=30000):
        """
        Split large audio file into smaller chunks.

        Args:
            audio_path (str): Path to the audio file
            chunk_length_ms (int): Length of each chunk in milliseconds (default: 30 seconds)

        Returns:
            list: List of audio chunks
        """
        print(f"Loading audio file: {audio_path}")
        audio = AudioSegment.from_file(audio_path)

        print(f"Audio duration: {len(audio) / 1000:.2f} seconds")
        print(f"Splitting into {chunk_length_ms/1000} second chunks...")

        chunks = make_chunks(audio, chunk_length_ms)
        return chunks

    def transcribe_chunk(self, chunk, chunk_index):
        """
        Transcribe a single audio chunk.

        Args:
            chunk (AudioSegment): Audio chunk to transcribe
            chunk_index (int): Index of the chunk

        Returns:
            str: Transcribed text
        """
        # Save chunk temporarily
        temp_file = f"temp_chunk_{chunk_index}.wav"
        chunk.export(temp_file, format="wav")

        try:
            # Transcribe the chunk
            result = self.model.transcribe(temp_file)
            text = result["text"].strip()

            # Clean up temporary file
            os.remove(temp_file)

            return text
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise e

    def transcribe_large_audio(self, audio_path, output_file=None, chunk_length_ms=30000):
        """
        Transcribe a large audio file by splitting it into chunks.

        Args:
            audio_path (str): Path to the audio file
            output_file (str): Path to save the transcription (optional)
            chunk_length_ms (int): Length of each chunk in milliseconds

        Returns:
            str: Complete transcription
        """
        start_time = time.time()

        # Split audio into chunks
        chunks = self.split_audio(audio_path, chunk_length_ms)

        print(f"Processing {len(chunks)} chunks...")

        full_transcription = []

        for i, chunk in enumerate(chunks):
            print(f"Transcribing chunk {i+1}/{len(chunks)}...")

            try:
                text = self.transcribe_chunk(chunk, i)
                if text:  # Only add non-empty transcriptions
                    full_transcription.append(text)
                    print(f"Chunk {i+1} completed: {text[:50]}...")
            except Exception as e:
                print(f"Error transcribing chunk {i+1}: {str(e)}")
                continue

        # Combine all transcriptions
        complete_text = " ".join(full_transcription)

        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(complete_text)
            print(f"Transcription saved to: {output_file}")

        end_time = time.time()
        print(f"\nTranscription completed in {end_time - start_time:.2f} seconds")
        print(f"Total text length: {len(complete_text)} characters")

        return complete_text

def main():
    # ===== CHANGE YOUR AUDIO FILE NAME HERE =====
    audio_file = "audio1.mp3"  # Please change this file name based on your files
    # =============================================

    # Configuration (you can modify these)
    model_size = "base"  # Optional: "tiny", "base", "small", "medium", "large"
    chunk_length_seconds = 30  # Chunk length in seconds - I think this is good

    # Check if audio file exists
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found!")
        print("Please make sure the file is in the same directory as this script.")
        return

    # Initialize transcriber
    transcriber = AudioTranscriber(model_size=model_size)

    # Set output file name
    base_name = os.path.splitext(audio_file)[0]
    output_file = f"{base_name}_transcription.txt"

    # Transcribe the audio
    try:
        transcription = transcriber.transcribe_large_audio(
            audio_file, 
            output_file, 
            chunk_length_ms=chunk_length_seconds * 1000
        )

        print(f"\nTranscription preview:")
        print("-" * 50)
        print(transcription[:500] + "..." if len(transcription) > 500 else transcription)

    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    main()
