import sys
import subprocess
import os


def compress_to_size(
    input_file,
    target_size_mb: float = 10.0,
    two_pass=True,
    audio_bitrate_k=128
):
    output_file = os.path.splitext(input_file)[0] + "_compressed.mp4"

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Deleted old file: {output_file}")

    # Calculate target bitrate
    target_size = target_size_mb * 1024 * 1024  # bytes
    probe = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_file
    ])
    duration = float(probe.strip())

    # target bitrate in kilobits/sec
    target_bitrate = ((target_size * 8) / duration) / 1000 * 1

    # print(f"### d: {duration}, target_bitrate: {target_bitrate}")

    # number of audio tracks
    num_audio_streams = 3

    # safety cap: at least 100 kbps
    video_bitrate = max(
        int(target_bitrate - (num_audio_streams * audio_bitrate_k)),
        100
    )

    # Run ffmpeg
    if two_pass:
        # pass 1 (no audio)
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-b:v", f"{video_bitrate}k",
            "-pass", "1", "-an", "-f", "mp4", "NUL"
        ], check=True)

        # pass 2 (with audio)
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-b:v", f"{video_bitrate}k",
            "-b:a", f"{audio_bitrate_k}k",
            "-ac", "2",   # stereo
            "-pass", "2", output_file
        ], check=True)
    else:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-b:v", str(int(target_bitrate)) + "k",
            "-bufsize", str(int(target_bitrate)) + "k",
            output_file
        ], check=True)

    print(f"Compressed file saved as: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: drag and drop an MP4 onto this script/exe.")
    elif len(sys.argv) == 3:
        compress_to_size(sys.argv[1], float(sys.argv[2]))
    else:
        compress_to_size(sys.argv[1])
