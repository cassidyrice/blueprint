"""
Generate voiceover audio using ElevenLabs TTS API.
Returns the audio file path and its actual duration in seconds.
"""
import os
import requests
import subprocess
import config

def normalize_script(text: str) -> str:
    """
    Converts card notation to spoken words for better TTS pronunciation.
    Example: '8♣' -> 'Eight of Clubs'
    """
    mapping = {
        "A": "Ace", "K": "King", "Q": "Queen", "J": "Jack",
        "♥": " of Hearts", "♣": " of Clubs", "♦": " of Diamonds", "♠": " of Spades"
    }
    # Replace suits first to avoid partial matches
    for char, replacement in mapping.items():
        text = text.replace(char, replacement)
    
    # Handle numbers (e.g., "8 of Clubs")
    return text


def generate_audio(script: str, output_path: str = config.AUDIO_PATH) -> float:
    """
    Send script to ElevenLabs and save MP3 to output_path.
    Returns the audio duration in seconds.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": config.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    # Normalize script for better pronunciation
    spoken_script = normalize_script(script)

    payload = {
        "text": spoken_script,
        "model_id": config.ELEVENLABS_MODEL,
        "speed": 0.82, # Slightly faster than before but still meditative
        "voice_settings": {
            "stability": 0.65,        # Higher stability for authoritative, non-emotional delivery
            "similarity_boost": 0.85, # Keep the gravelly brand texture
            "style": 0.0,             # Keep it flat and strategic
            "use_speaker_boost": True,
        },
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Audio saved: {output_path} ({len(response.content) / 1024:.1f} KB)")

    duration = get_audio_duration(output_path)
    print(f"Audio duration: {duration:.2f}s")
    return duration


def get_audio_duration(path: str) -> float:
    """Use ffprobe to get accurate audio duration in seconds."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


if __name__ == "__main__":
    test = "The solar spread reveals your path through the coming year."
    duration = generate_audio(test)
    print(f"Duration: {duration:.2f}s")
