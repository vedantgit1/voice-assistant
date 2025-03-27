import os
import speech_recognition as sr
from gtts import gTTS
import requests
from dotenv import load_dotenv, find_dotenv
import json
import tempfile
import subprocess
import sys

# Load environment variables
load_dotenv(find_dotenv(), override=True)

class VoiceBot:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.model = os.getenv('DEFAULT_MODEL', 'deepseek/deepseek-chat-v3-0324:free')
        
        # System prompt for response generation
        self.system_prompt = """You are a helpful assistant that provides clear and concise responses. 
        Focus on being informative, friendly, and professional in your interactions."""

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

    def get_response(self, user_input):
        """Get response from the API"""
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
            ]
        }
        
        try:
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
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_filename = fp.name
            tts.save(temp_filename)
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(temp_filename)
            else:  # Linux and MacOS
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, temp_filename])
                
            import time
            time.sleep(len(text) * 0.1)
            
        finally:
            try:
                os.unlink(temp_filename)
            except:
                pass

    def run(self):
        """Main loop for the voice assistant"""
        print("Voice Assistant is ready! Speak to ask a question. Say 'exit' to quit.")
        
        while True:
            user_input = self.listen()
            
            if user_input is None:
                continue
                
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
                
            response = self.get_response(user_input)
            print(f"Response: {response}")
            
            self.speak(response)

if __name__ == "__main__":
    bot = VoiceBot()
    bot.run() 