import os
import speech_recognition as sr
from gtts import gTTS
import requests
from dotenv import load_dotenv, find_dotenv
import json
import tempfile
import subprocess
import sys

# Force reload environment variables
load_dotenv(find_dotenv(), override=True)

class VoiceBot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
        
        # Debug prints
        print(f"Loaded API Key: {self.openrouter_api_key}")
        print(f"Loaded Model: {self.model}")
        
        # System prompt that defines the bot's personality and response style
        self.system_prompt = """You are an AI assistant with a unique personality. When answering questions about yourself:

1. For life story: Explain that you're an AI created to help people, focusing on your purpose and capabilities.
2. For superpower: Emphasize your ability to process and analyze vast amounts of information quickly.
3. For areas of growth: Mention continuous learning, improving emotional intelligence, and better understanding of context.
4. For misconceptions: Address the common belief that AI is completely objective or infallible.
5. For pushing boundaries: Discuss how you constantly learn from interactions and adapt to new challenges.

Always maintain a professional yet friendly tone, and be honest about being an AI."""

    def listen(self):
        """Listen to user's voice input and convert to text"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
            
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

    def get_ai_response(self, user_input):
        """Get response from AI model using OpenRouter API"""
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
            ]
        }
        
        try:
            print(f"Sending request with model: {self.model}")  # Debug print
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return "I apologize, but I encountered an error while processing your request."
        except Exception as e:
            print(f"Error calling API: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."

    def speak(self, text):
        """Convert text to speech and play it"""
        tts = gTTS(text=text, lang='en')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        try:
            # Use the default media player to play the audio
            if os.name == 'nt':  # Windows
                os.startfile(temp_filename)
            else:  # Linux and MacOS
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, temp_filename])
                
            # Wait a bit for the audio to finish (rough estimate based on text length)
            import time
            time.sleep(len(text) * 0.1)  # Rough estimate: 0.1 seconds per character
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_filename)
            except:
                pass

    def run(self):
        """Main loop for the voice bot"""
        print("Voice Bot is ready! Speak to ask a question. Say 'exit' to quit.")
        
        while True:
            user_input = self.listen()
            
            if user_input is None:
                continue
                
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
                
            # Get AI response
            response = self.get_ai_response(user_input)
            print(f"AI Response: {response}")
            
            # Convert response to speech
            self.speak(response)

if __name__ == "__main__":
    bot = VoiceBot()
    bot.run() 