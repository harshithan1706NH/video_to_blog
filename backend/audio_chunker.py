import os
import subprocess

CHUNK_DURATION = 5 * 60  # 5 minutes


def chunk_audio(audio_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    output_pattern = os.path.join(
        output_folder,
        "chunk_%03d.wav"
    )

    command = [
        "ffmpeg",
        "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(CHUNK_DURATION),
        "-ac", "1",
        "-ar", "16000",
        "-c:a", "pcm_s16le",
        output_pattern
    ]

    subprocess.run(command, check=True)

    chunks = sorted(
        os.path.join(output_folder, file)
        for file in os.listdir(output_folder)
        if file.endswith(".wav")
    )

    return chunks


if __name__ == "__main__":
    audio_path = "processing/audio.wav"
    output_folder = "processing/chunks"

    chunks = chunk_audio(
        audio_path,
        output_folder
    )

    print("\nChunks created:")

    for chunk in chunks:
        print(chunk)