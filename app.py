from flask import Flask, render_template, request, jsonify
import os
from gtts import gTTS
import requests
from dotenv import load_dotenv, find_dotenv
import json
import io
import base64
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Load environment variables
load_dotenv(find_dotenv(), override=True)

# Debug: Print environment variables
print("Environment variables loaded:")
print(f"OPENROUTER_API_KEY: {'*' * len(os.getenv('OPENROUTER_API_KEY', '')) if os.getenv('OPENROUTER_API_KEY') else 'Not found'}")
print(f"DEFAULT_MODEL: {os.getenv('DEFAULT_MODEL', 'Not found')}")

app = Flask(__name__)

# Create a thread pool for async operations
executor = ThreadPoolExecutor(max_workers=3)

class VoiceBot:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
        
        # System prompt for response generation
        self.system_prompt = """You are a helpful assistant that provides clear and concise responses. 
        Focus on being informative, friendly, and professional in your interactions."""

    @lru_cache(maxsize=100)
    def get_response(self, user_input):
        """Get response from the API with caching"""
        headers = {
            "HTTP-Referer": "https://github.com/",
            "X-Title": "Voice Assistant",
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return "I apologize, but I encountered an error while processing your request."
        except Exception as e:
            print(f"Error calling API: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

    @lru_cache(maxsize=100)
    def text_to_speech(self, text):
        """Convert text to speech and return base64 encoded audio with caching"""
        tts = gTTS(text=text, lang='en', slow=False)
        
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        audio_base64 = base64.b64encode(audio_io.getvalue()).decode('utf-8')
        return audio_base64

# Initialize the voice bot
bot = VoiceBot()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    # Get response
    response = bot.get_response(user_input)
    
    # Convert response to speech asynchronously
    future = executor.submit(bot.text_to_speech, response)
    audio_base64 = future.result()
    
    return jsonify({
        'response': response,
        'audio': audio_base64
    })

if __name__ == '__main__':
    app.run(debug=True) 