# Claude GeoGuessr Bot

A Twitch bot that plays GeoGuessr-style games using AI. Chat users submit location names, and GPT-4 Vision tries to guess coordinates from Street View images.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required API Keys:**
   - **Twitch Bot Token**: Create at https://twitchtokengenerator.com/
   - **OpenAI API Key**: Get from https://platform.openai.com/
   - **Google Maps API Key**: Enable Street View Static API at https://console.cloud.google.com/

## Usage

1. **Start the processing loop:**
   ```bash
   python3 run_loop.py
   ```

2. **Start the Twitch bot:**
   ```bash
   python3 bot.py
   ```

3. **View overlay:** Open `overlay/index.html` in browser

4. **Chat commands:** Users type `!guess [location]` in Twitch chat

## How it works

1. User submits location via `!guess Paris`
2. Bot geocodes location to coordinates
3. Downloads Street View image from Google Maps
4. GPT-4 Vision analyzes image and guesses coordinates
5. Scores based on distance (max 5000 points)
6. Updates live overlay with results

## Files

- `bot.py` - Twitch chat bot
- `run_loop.py` - Main processing loop
- `gpt_guess.py` - OpenAI API integration
- `screenshot.py` - Street View image fetching
- `scorer.py` - Distance/score calculation
- `queue_manager.py` - Request queue management
- `overlay/` - Web overlay for streaming