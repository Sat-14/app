import os
import tempfile
from elevenlabs import generate, Voice, VoiceSettings, save, set_api_key, voices
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set your ElevenLabs API key
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

def generate_voice_audio(text: str, voice_id: str = None):
    """Generate voice audio using ElevenLabs API."""
    try:
        # Use default voice ID if none is provided
        if not voice_id:
            voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

        # Generate audio
        audio = generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5,
                    use_speaker_boost=True
                )
            )
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            save(audio, tmp_file.name)
            return {"success": True, "audio_path": tmp_file.name}

    except Exception as e:
        print(f"Error generating ElevenLabs audio: {e}")
        return {"success": False, "error": str(e)}

def get_available_voices():
    """Get list of available voices from ElevenLabs."""
    try:
        available_voices = voices()  # this returns a list of Voice objects

        voice_list = [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
            }
            for voice in available_voices
        ]

        return {"success": True, "voices": voice_list}
    except Exception as e:
        print(f"Error getting ElevenLabs voices: {e}")
        return {"success": False, "error": str(e)}
