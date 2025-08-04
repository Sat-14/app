import os
from elevenlabs.client import ElevenLabs
from elevenlabs import save, Voice, VoiceSettings
import tempfile
# Assuming you have a .env file or environment variables set for your keys
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Create a single, reusable client instance
client = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"), 
)

def generate_voice_audio(text: str, voice_id: str = None):
    """Generate voice audio using the new ElevenLabs client."""
    try:
        # Use the default voice ID from environment variables if none is provided
        if not voice_id:
            voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default if not set

        # Generate audio using the client instance
        audio = client.generate(
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

        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            save(audio, tmp_file.name)
            return {"success": True, "audio_path": tmp_file.name}

    except Exception as e:
        print(f"Error generating ElevenLabs audio: {e}")
        return {"success": False, "error": str(e)}

def get_available_voices():
    """Get list of available voices using the new ElevenLabs client."""
    try:
        # Get voices using the client instance
        available_voices = client.voices.get_all()

        voice_list = [
            {
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
            }
            for voice in available_voices.voices
        ]

        return {"success": True, "voices": voice_list}
    except Exception as e:
        print(f"Error getting ElevenLabs voices: {e}")
        return {"success": False, "error": str(e)}
    