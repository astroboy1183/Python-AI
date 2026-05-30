# Conversational AI: Speech-to-Text → ChatGPT → Text-to-Speech

A Python application that converts speech to text, processes it through ChatGPT, and converts the response back to speech.

## Features

- 🎤 **Speech Recognition**: Convert audio to text using OpenAI Whisper API
- 🤖 **ChatGPT Integration**: Send text to GPT-4o-mini for intelligent responses
- 🔊 **Text-to-Speech**: Convert ChatGPT responses back to audio using OpenAI TTS
- 🎯 **Multiple Input Options**: Microphone, audio file, or text input

## Requirements

### System Dependencies

**Linux:**
```bash
sudo apt-get install ffmpeg pulseaudio
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download and install FFmpeg from https://ffmpeg.org/download.html
- Add FFmpeg to your PATH

### Python Dependencies

```bash
pip install -r requirements.txt
```

## Setup

1. **Get OpenAI API Key**
   - Sign up at https://platform.openai.com
   - Create an API key in your account settings
   - Set environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

Run the main script:
```bash
python conversational_ai.py
```

Choose one of three input options:

1. **Microphone Recording**: Record audio directly (default 10 seconds)
2. **Audio File**: Provide path to existing audio file (MP3, WAV, etc.)
3. **Text Input**: Type your message directly

The program will:
- Convert speech to text (if using audio)
- Send to ChatGPT for processing
- Generate audio response
- Play the audio automatically

## Example

```
=== Conversational AI ===
Options:
1. Use microphone input (record audio)
2. Use existing audio file
3. Use text input directly

Choose option (1-3): 1
Recording duration in seconds (default 10): 5
Recording for 5 seconds... Speak now!
Audio saved to input_audio.wav
Converting speech to text...
Transcribed text: What is the capital of France?
Sending to ChatGPT...
ChatGPT response: The capital of France is Paris. It's located in northern France on the Seine River and is known as the "City of Light" for its beautiful architecture, museums, and cultural heritage.
Converting response to speech...
Audio response saved to response_audio.mp3
Playing audio...
```

## Configuration

Edit `conversational_ai.py` to customize:

- **TTS Voice**: Change `voice` parameter (alloy, echo, fable, onyx, nova, shimmer)
- **TTS Speed**: Adjust `speed` parameter (0.25 - 4.0)
- **Model**: Change `model` parameter in `chat_with_gpt()` (gpt-4o-mini, gpt-4-turbo, etc.)
- **Temperature**: Adjust creativity (0.0 - 2.0)
- **Max Tokens**: Limit response length

## Troubleshooting

**"ffmpeg not found"**
- Install FFmpeg for your OS (see Requirements)
- Ensure it's in your PATH

**"OPENAI_API_KEY not set"**
- Set environment variable or create .env file
- Check key is valid and has sufficient credits

**No audio from microphone**
- Check audio device: `pactl list short sources` (Linux)
- Ensure microphone permissions are granted

**Audio file not recognized**
- Check file format is supported (MP3, WAV, FLAC, OGG, M4A)
- Verify file path is correct

## Costs

Usage charges apply:
- Whisper API: ~$0.02 per minute of audio
- GPT-4o-mini: ~$0.15 per 1M input tokens
- TTS: ~$0.015 per 1K characters

## Files

- `conversational_ai.py` - Main script
- `requirements.txt` - Python dependencies
- `input_audio.wav` - Generated input recording
- `response_audio.mp3` - Generated response audio
