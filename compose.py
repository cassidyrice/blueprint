"""
Compose PNG frames + audio into a final MP4 using ffmpeg.
"""
import os
import subprocess
import config


def compose_video(
    frames_dir: str = config.FRAMES_DIR,
    audio_path: str = config.AUDIO_PATH,
    output_path: str = config.VIDEO_PATH,
) -> str:
    """
    Combine frame sequence and audio into an MP4.
    Returns the output file path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(config.FPS),
        "-i", f"{frames_dir}/%05d.png",
        "-i", audio_path,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17", # Nearly lossless for high-fidelity gold/black contrast
        "-pix_fmt", "yuv420p",
        "-colorspace", "bt709", # Explicit color space for consistent web viewing
        "-color_trc", "bt709",
        "-color_primaries", "bt709",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
    ]

    print(f"Composing video: {output_path}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Video created: {output_path} ({size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    compose_video()
