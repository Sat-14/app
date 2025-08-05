import os
import requests
from datetime import datetime
from twilio.rest import Client
import google.generativeai as genai
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Gemini
logger.info("[GEMINI CONFIG] Configuring Gemini AI")
genai.configure(api_key=Config.GOOGLE_API_KEY)
logger.debug(f"[GEMINI CONFIG] API key configured: {'*' * 10 + Config.GOOGLE_API_KEY[-4:] if Config.GOOGLE_API_KEY else 'NOT SET'}")

def generate_reminder_message(name, bill_data):
    """Generate reminder message using Gemini AI"""
    logger.info(f"[MESSAGE GEN] Starting message generation for user: {name}")
    logger.debug(f"[MESSAGE GEN] Bill data received: {bill_data}")
    
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    current_hour = datetime.now().hour
    logger.debug(f"[MESSAGE GEN] Current hour: {current_hour}")
    
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    logger.debug(f"[MESSAGE GEN] Selected greeting: {greeting}")
    
    prompt = f"""
    You are a friendly financial assistant creating a reminder message.
    
    Create a natural, friendly reminder with this structure:
    1. Start with: "Hey {name}, {greeting}."
    2. Remind about the bill payment:
       - Bill: {bill_data.get('name')}
       - Amount: ₹{bill_data.get('amount')}
       - Due Date: {bill_data.get('due_date')}
    3. End with: "Hope you have a nice day."
    
    Keep it brief and friendly.
    """
    
    logger.debug(f"[MESSAGE GEN] Generated prompt for Gemini: {prompt[:200]}...")
    
    try:
        logger.info("[MESSAGE GEN] Calling Gemini AI to generate message")
        response = gemini_model.generate_content(prompt)
        generated_message = response.text.strip()
        logger.info(f"[MESSAGE GEN] Successfully generated message via Gemini")
        logger.debug(f"[MESSAGE GEN] Generated message: {generated_message}")
        return generated_message
    except Exception as e:
        logger.error(f"[MESSAGE GEN ERROR] Gemini generation failed: {str(e)}", exc_info=True)
        # Fallback message
        fallback_message = (
            f"Hi {name}, this is a reminder that your payment for '{bill_data.get('name')}' "
            f"is due on {bill_data.get('due_date')}. Amount due: ₹{bill_data.get('amount')}."
        )
        logger.info("[MESSAGE GEN] Using fallback message due to Gemini error")
        logger.debug(f"[MESSAGE GEN] Fallback message: {fallback_message}")
        return fallback_message

#................added by me (satvik kesarwani)................
def send_whatsapp_reminder(phone_number, message_body):
    """Send WhatsApp reminder using Twilio"""
    logger.info(f"[WHATSAPP] Starting WhatsApp reminder to: {phone_number}")
    logger.debug(f"[WHATSAPP] Message length: {len(message_body)} characters")
    logger.debug(f"[WHATSAPP] Message preview: {message_body[:100]}...")
    
    try:
        # --- NEW DEBUG CODE ---
        print("--- DEBUG: CHECKING TWILIO KEYS ---")
        print(f"Account SID from Config: {Config.TWILIO_ACCOUNT_SID}")
        print(f"Auth Token from Config: {Config.TWILIO_AUTH_TOKEN}")
        print("-----------------------------------")
        # --- END OF NEW DEBUG CODE ---
        
        logger.debug(f"[WHATSAPP] Twilio Account SID: {'*' * 30 + Config.TWILIO_ACCOUNT_SID[-4:] if Config.TWILIO_ACCOUNT_SID else 'NOT SET'}")
        logger.debug(f"[WHATSAPP] Twilio Auth Token: {'*' * 30 + Config.TWILIO_AUTH_TOKEN[-4:] if Config.TWILIO_AUTH_TOKEN else 'NOT SET'}")
        logger.debug(f"[WHATSAPP] WhatsApp From Number: {Config.TWILIO_WHATSAPP_FROM}")
        
        logger.info("[WHATSAPP] Creating Twilio client")
        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        formatted_to = f'whatsapp:{phone_number}'
        logger.debug(f"[WHATSAPP] Formatted recipient: {formatted_to}")
        
        logger.info("[WHATSAPP] Sending message via Twilio")
        message = client.messages.create(
            body=message_body,
            from_=Config.TWILIO_WHATSAPP_FROM,
            to=formatted_to
        )
        
        logger.info(f"[WHATSAPP] Message sent successfully with SID: {message.sid}")
        logger.debug(f"[WHATSAPP] Message status: {message.status}")
        
        return {"success": True, "sid": message.sid}
    except Exception as e:
        logger.error(f"[WHATSAPP ERROR] Failed to send WhatsApp message: {str(e)}", exc_info=True)
        logger.debug(f"[WHATSAPP ERROR] Error type: {type(e).__name__}")
        return {"success": False, "error": str(e)}
    
#................added by me (satvik kesarwani)................
def send_voice_reminder(phone_number, message_body):
    """Send voice reminder using Bland AI"""
    logger.info(f"[VOICE CALL] Starting voice reminder to: {phone_number}")
    logger.debug(f"[VOICE CALL] Original message length: {len(message_body)} characters")
    
    headers = {
        'Authorization': Config.BLAND_AI_API_KEY,
        'Content-Type': 'application/json'
    }
    
    logger.debug(f"[VOICE CALL] Bland AI API key: {'*' * 30 + Config.BLAND_AI_API_KEY[-4:] if Config.BLAND_AI_API_KEY else 'NOT SET'}")
    
    # Remove any URLs from voice message
    voice_task = message_body.split("http")[0].strip()
    logger.debug(f"[VOICE CALL] Voice task after URL removal: {voice_task}")
    logger.debug(f"[VOICE CALL] Voice task length: {len(voice_task)} characters")
    
    payload = {
        'phone_number': phone_number,
        'task': voice_task,
        'reduce_latency': True,
        'voice_id': 'e917d52a-5a9e-4c7c-8d1e-92719114343a',
        'speed': 0.85
    }
    
    logger.debug(f"[VOICE CALL] Request payload: {payload}")
    logger.debug(f"[VOICE CALL] Using voice_id: {payload['voice_id']}")
    logger.debug(f"[VOICE CALL] Speed setting: {payload['speed']}")
    
    try:
        logger.info("[VOICE CALL] Sending POST request to Bland AI API")
        logger.debug(f"[VOICE CALL] API endpoint: https://api.bland.ai/v1/calls")
        
        response = requests.post(
            'https://api.bland.ai/v1/calls',
            json=payload,
            headers=headers
        )
        
        logger.debug(f"[VOICE CALL] Response status code: {response.status_code}")
        logger.debug(f"[VOICE CALL] Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        call_data = response.json()
        logger.info(f"[VOICE CALL] Call initiated successfully")
        logger.debug(f"[VOICE CALL] Response data: {call_data}")
        
        call_id = call_data.get('call_id')
        logger.info(f"[VOICE CALL] Call ID: {call_id}")
        
        return {"success": True, "call_id": call_id}
    except requests.exceptions.RequestException as e:
        logger.error(f"[VOICE CALL ERROR] Request failed: {str(e)}", exc_info=True)
        logger.debug(f"[VOICE CALL ERROR] Request error type: {type(e).__name__}")
        if hasattr(e, 'response') and e.response is not None:
            logger.debug(f"[VOICE CALL ERROR] Response status: {e.response.status_code}")
            logger.debug(f"[VOICE CALL ERROR] Response body: {e.response.text}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"[VOICE CALL ERROR] Unexpected error: {str(e)}", exc_info=True)
        logger.debug(f"[VOICE CALL ERROR] Error type: {type(e).__name__}")
        return {"success": False, "error": str(e)}