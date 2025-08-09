# ai_service.py - Service to interact with AI models (Gemini, OpenAI)

import os
import google.generativeai as genai
import openai
from config import Config
from cryptography.fernet import Fernet
import json
import logging
import asyncio

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AIService:
    
    def __init__(self, app_config):
        self.app_config = app_config
        
        # Ensure the encryption key is valid before initializing Fernet
        encryption_key = self.app_config.get('ENCRYPTION_KEY')
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY not set in app config.")
        
        self.cipher_suite = Fernet(encryption_key.encode())
        
        try:
            # Configure Gemini and OpenAI clients on initialization
            if Config.GOOGLE_API_KEY:
                genai.configure(api_key=Config.GOOGLE_API_KEY)
            if Config.OPENAI_API_KEY:
                openai.api_key = Config.OPENAI_API_KEY
            logger.info("[AI SERVICE] AI clients configured successfully.")
        except Exception as e:
            logger.error(f"[AI SERVICE ERROR] Failed to configure AI clients: {str(e)}")

    def encrypt_api_key(self, key: str) -> str:
        """Encrypts an API key for secure storage."""
        return self.cipher_suite.encrypt(key.encode()).decode()

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypts a stored API key."""
        return self.cipher_suite.decrypt(encrypted_key.encode()).decode()

    async def chat_with_gemini(self, messages: list, api_key: str, context: dict):
        """
        Communicates with the Google Gemini API.
        """
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash-latest', tools=self._get_tools())
        
        # Format message history for Gemini
        history = [{'role': m['role'], 'parts': [m['content']]} for m in messages]
        
        try:
            response = await model.generate_content_async(history)
            
            if response.candidates and response.candidates[0].content.parts[0].function_call:
                function_call = response.candidates[0].content.parts[0].function_call
                return "", function_call
            else:
                return response.text, None
        
        except Exception as e:
            logger.error(f"[GEMINI CHAT ERROR] {e}")
            return "Sorry, I couldn't process that request with Gemini.", None

    async def chat_with_openai(self, messages: list, api_key: str, context: dict):
        """
        Communicates with the OpenAI API.
        """
        # Note: You'll need to set up the OpenAI client with the API key here
        # For simplicity, this is a placeholder
        logger.warning("[OPENAI CHAT] OpenAI functionality is a placeholder.")
        return "Sorry, OpenAI support is currently a placeholder.", None

    def _get_tools(self):
        """
        Defines the available tools (functions) the AI can call.
        These functions must be defined within a class or module and be callable.
        """
        # This is where you would define the actual tool functions.
        # For now, let's keep them as placeholders that return a dummy response.
        # In a full implementation, these would call helper functions
        # that interact with your database (e.g., from chatbot.py)
        
        def get_user_bills():
            """Returns a list of all bills for the current user."""
            return {"bills_list": ["Internet bill", "Electricity bill", "Rent"]}
        
        def get_upcoming_payments(days: int = 7):
            """Returns a list of unpaid bills due within a specified number of days."""
            return {"upcoming_payments": [{"bill_name": "Internet bill", "due_date": "2025-08-15"}]}

        def get_loan_summary():
            """Returns a summary of the user's active loans and EMIs."""
            return {"loan_summary": "You have 1 active loan with a remaining balance of $500."}

        def create_bill(name: str, amount: float, due_date: str, category: str, frequency: str):
            """Creates a new bill reminder."""
            # The tool would return a success message or an error
            return {"status": "success", "message": f"Bill '{name}' for ${amount} created."}

        return [
            get_user_bills,
            get_upcoming_payments,
            get_loan_summary,
            create_bill
        ]
