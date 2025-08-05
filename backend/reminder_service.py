import os
import requests
from datetime import datetime
from twilio.rest import Client
import google.generativeai as genai
from config import Config

# Configure Gemini
genai.configure(api_key=Config.GOOGLE_API_KEY)

def generate_reminder_message(name, bill_data):
    """Generate reminder message using Gemini AI"""
    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        greeting = "Good morning"
    elif 12 <= current_hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
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
    
    try:
        response = gemini_model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Fallback message
        return (
            f"Hi {name}, this is a reminder that your payment for '{bill_data.get('name')}' "
            f"is due on {bill_data.get('due_date')}. Amount due: ₹{bill_data.get('amount')}."
        )


#................added by me (satvik kesarwani)................
def send_whatsapp_reminder(phone_number, message_body):
    """Send WhatsApp reminder using Twilio"""
    try:
        # --- NEW DEBUG CODE ---
        print("--- DEBUG: CHECKING TWILIO KEYS ---")
        print(f"Account SID from Config: {Config.TWILIO_ACCOUNT_SID}")
        print(f"Auth Token from Config: {Config.TWILIO_AUTH_TOKEN}")
        print("-----------------------------------")
        # --- END OF NEW DEBUG CODE ---

        client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message_body,
            from_=Config.TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:{phone_number}'
        )
        return {"success": True, "sid": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}


    
#................added by me (satvik kesarwani)................


def send_voice_reminder(phone_number, message_body):
    """Send voice reminder using Bland AI"""
    headers = {
        'Authorization': Config.BLAND_AI_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Remove any URLs from voice message
    voice_task = message_body.split("http")[0].strip()
    
    payload = {
        'phone_number': phone_number,
        'task': voice_task,
        'reduce_latency': True,
        'voice_id': 'e917d52a-5a9e-4c7c-8d1e-92719114343a',
        'speed': 0.85
    }
    
    try:
        response = requests.post(
            'https://api.bland.ai/v1/calls',
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        call_data = response.json()
        return {"success": True, "call_id": call_data.get('call_id')}
    except Exception as e:
        return {"success": False, "error": str(e)}