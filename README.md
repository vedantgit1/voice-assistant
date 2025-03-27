# AI Voice Assistant

A web-based AI voice assistant that uses OpenRouter API for text generation and Google's Text-to-Speech for voice output.

## Features

- Voice input using Web Speech API
- Text-to-speech output
- Real-time chat interface
- Modern and responsive UI
- Automatic message sending after voice input

## Deployment Instructions

1. Fork this repository
2. Sign up for a free account at [Render.com](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Add your OpenRouter API key as an environment variable:
   - Name: `OPENROUTER_API_KEY`
   - Value: Your OpenRouter API key

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Requirements

- Python 3.8+
- OpenRouter API key
- Modern web browser with Web Speech API support (Chrome recommended)

## Example Questions

The bot is designed to answer questions about itself, such as:
- What should we know about your life story in a few sentences?
- What's your #1 superpower?
- What are the top 3 areas you'd like to grow in?
- What misconception do your coworkers have about you?
- How do you push your boundaries and limits?

## Troubleshooting

- If you encounter microphone issues, make sure your microphone is properly connected and set as the default input device
- If you get audio playback errors, verify that your speakers are working and properly connected
- For API-related issues, check that your API keys are correctly set in the .env file

## License

This project is open-source and available under the MIT License. 