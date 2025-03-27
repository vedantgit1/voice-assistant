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

# Force reload environment variables
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
        
        # System prompt that defines the bot's personality and response style
        self.system_prompt = """You are an AI assistant with a unique personality. When answering questions about yourself:

1. For life story: Explain that you're an AI created to help people, focusing on your purpose and capabilities.
2. For superpower: Emphasize your ability to process and analyze vast amounts of information quickly.
3. For areas of growth: Mention continuous learning, improving emotional intelligence, and better understanding of context.
4. For misconceptions: Address the common belief that AI is completely objective or infallible.
5. For pushing boundaries: Discuss how you constantly learn from interactions and adapt to new challenges.

Always maintain a professional yet friendly tone, and be honest about being an AI."""

    @lru_cache(maxsize=100)
    def get_ai_response(self, user_input):
        """Get response from AI model using OpenRouter API with caching"""
        headers = {
            "HTTP-Referer": "https://github.com/",
            "X-Title": "AI Voice Bot",
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,  # Add temperature for faster responses
            "max_tokens": 150    # Limit response length
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10  # Reduce timeout
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
        tts = gTTS(text=text, lang='en', slow=False)  # Use fast mode
        
        # Save to memory instead of file
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        audio_io.seek(0)
        
        # Convert to base64
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
    
    # Get AI response
    response = bot.get_ai_response(user_input)
    
    # Convert response to speech asynchronously
    future = executor.submit(bot.text_to_speech, response)
    audio_base64 = future.result()  # Wait for the result
    
    return jsonify({
        'response': response,
        'audio': audio_base64
    })

if __name__ == '__main__':
    app.run(debug=True) 