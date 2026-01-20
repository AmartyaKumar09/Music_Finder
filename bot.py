import os
import telebot
from telebot import types
import requests
from dotenv import load_dotenv
from rapidfuzz import fuzz
import re
import speech_recognition as sr
from pydub import AudioSegment
import subprocess
import sys
import librosa
import soundfile as sf
import numpy as np


def clean_lyrics(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return text.strip()

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GENIUS_API_KEY = os.environ.get('GENIUS_API_KEY')

if not BOT_TOKEN:
    raise ValueError(
        "❌ BOT_TOKEN environment variable not set!\n\n"
        "Set it with:\n"
        "  set BOT_TOKEN=your_token_here (cmd)\n"
        "  or\n"
        "  $env:BOT_TOKEN='your_token_here' (PowerShell)\n\n"
        "Get your token from BotFather on Telegram."
    )

bot = telebot.TeleBot(BOT_TOKEN)

# Genius API endpoint
GENIUS_API_URL = "https://api.genius.com"

def search_song_by_lyrics(lyrics):
    """Search for songs by partial lyrics using Genius API"""
    if not GENIUS_API_KEY:
        return None, "Genius API key not configured"
    
    headers = {
        "Authorization": f"Bearer {GENIUS_API_KEY}"
    }
    
    params = {
        "q": lyrics,
        "per_page": 5
    }
    
    try:
        response = requests.get(
            f"{GENIUS_API_URL}/search",
            headers=headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        hits = data.get("response", {}).get("hits", [])
        if not hits:
            return None, "No songs found matching those lyrics"
        
        results = []
        for hit in hits:
            song = hit.get("result", {})
            results.append({
                "title": song.get("title", "Unknown"),
                "artist": song.get("primary_artist", {}).get("name", "Unknown"),
                "url": song.get("url", ""),
                "album": song.get("album", {}).get("name", "Unknown") if song.get("album") else "Unknown"
            })
        
        return results, None
    except (requests.RequestException, ValueError) as e:
        return None, f"Error searching: {str(e)}"
    
@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    bot.send_message(message.chat.id, "🎙️ Listening to your voice...")

    try:
        print("✓ Voice message received")
        
        file_info = bot.get_file(message.voice.file_id)
        print(f"✓ File info retrieved: {file_info.file_path}")
        
        downloaded_file = bot.download_file(file_info.file_path)
        print(f"✓ File downloaded: {len(downloaded_file)} bytes")

        voice_file = f"voice_{message.chat.id}.ogg"
        wav_file = f"voice_{message.chat.id}.wav"

        # Save OGG file
        with open(voice_file, "wb") as f:
            f.write(downloaded_file)
        print(f"✓ OGG file saved: {voice_file}")

        # Convert OGG → WAV using librosa (no ffmpeg needed!)
        try:
            print(f"✓ Loading audio with librosa...")
            # Load OGG file
            audio_data, sr_rate = librosa.load(voice_file, sr=16000, mono=True)
            
            # Save as WAV
            sf.write(wav_file, audio_data, sr_rate)
            print(f"✓ WAV file created: {wav_file}")
        except Exception as librosa_err:
            print(f"✗ Librosa conversion failed: {librosa_err}")
            raise Exception(f"Failed to convert audio: {librosa_err}")

        # Speech recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio = recognizer.record(source)
        print("✓ Audio recorded from file")

        try:
            text = recognizer.recognize_google(audio, language='en-US')
            print(f"✓ Speech recognized: {text}")
            bot.send_message(message.chat.id, f"📝 Heard: '{text}'")
            search_and_send_results(message, text)
        except sr.UnknownValueError:
            print("✗ Could not understand audio (speech too quiet or unclear)")
            bot.send_message(message.chat.id, "❌ Sorry, I couldn't understand the audio. Please speak clearly.")
        except sr.RequestError as e:
            print(f"✗ Speech service error: {type(e).__name__}: {e}")
            # Try alternative speech service
            if "Connection" in str(e) or "Network" in str(e):
                bot.send_message(message.chat.id, "⚠️ Network error: Check your internet connection")
            else:
                bot.send_message(message.chat.id, f"⚠️ Speech service error: {str(e)}")
        finally:
            # Cleanup temporary files
            if os.path.exists(voice_file):
                os.remove(voice_file)
                print(f"✓ Cleaned up: {voice_file}")
            if os.path.exists(wav_file):
                os.remove(wav_file)
                print(f"✓ Cleaned up: {wav_file}")
    except Exception as e:
        print(f"✗ Exception in voice handler: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        bot.send_message(message.chat.id, f"❌ Error processing voice: {str(e)}")

@bot.message_handler(commands=['start'])
def start(message):
    """Handle /start command"""
    markup = types.ReplyKeyboardMarkup(row_width=1)
    markup.add(types.KeyboardButton("🎵 Search Song"))
    
    bot.send_message(
        message.chat.id,
        "🎵 Welcome to Song Finder Bot!\n\n"
        "Send me some lyrics (even incomplete) and I'll help you find the song.\n\n"
        "Just type the lyrics you remember and I'll search for matching songs!",
        reply_markup=markup
    )

def send_results(message, results):
    """Send search results to user"""
    response = "🎵 Found matching songs:\n\n"
    for i, song in enumerate(results, 1):
        response += (
            f"{i}. <b>{song['title']}</b>\n"
            f"   Artist: {song['artist']}\n"
            f"   Album: {song['album']}\n"
            f"   🔗 <a href='{song['url']}'>View on Genius</a>\n\n"
        )
    bot.send_message(message.chat.id, response, parse_mode="HTML")

def search_and_send_results(message, lyrics):
    """Search for songs and send results with smart suggestions"""
    bot.send_message(message.chat.id, f"🔍 Searching for: '{lyrics}'...")
    
    # Try direct search
    results, error = search_song_by_lyrics(lyrics)
    if results:
        send_results(message, results)
        return
    
    # Smart search with cleaned lyrics
    cleaned = clean_lyrics(lyrics)
    if cleaned and cleaned != lyrics:
        bot.send_message(message.chat.id, "🤔 Couldn't find exact match. Trying smarter search...")
        retry_results, _ = search_song_by_lyrics(cleaned)
        if retry_results:
            send_results(message, retry_results)
            return
    
    # No results found
    bot.send_message(
        message.chat.id, 
        "❌ No songs found.\n\n💡 Tips:\n- Try fewer words\n- Use the chorus\n- Check spelling"
    )

@bot.message_handler(commands=['help'])
def help_message(message):
    """Handle /help command"""
    bot.send_message(
        message.chat.id,
        "📝 How to use:\n\n"
        "1. Send me any lyrics you remember (doesn't need to be exact or complete)\n"
        "2. I'll search for matching songs\n"
        "3. I'll show you the song title, artist, and album\n\n"
        "Example: 'imagine all the people' → will find John Lennon's 'Imagine'\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this message\n"
        "/search <lyrics> - Search for a song"
    )

@bot.message_handler(commands=['search'])
def search_command(message):
    """Handle /search command with lyrics"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Usage: /search <lyrics>")
        return
    
    lyrics = args[1]
    search_and_send_results(message, lyrics)

@bot.message_handler(func=lambda message: message.text == "🎵 Search Song")
def search_button(message):
    """Handle search button press"""
    msg = bot.send_message(message.chat.id, "Send me the lyrics you remember:")
    bot.register_next_step_handler(msg, search_from_input)

def search_from_input(message):
    """Handle lyrics input from next step handler"""
    search_and_send_results(message, message.text)

@bot.message_handler(func=lambda message: message.content_type == 'text')
def handle_message(message):
    """Handle regular text messages with lyrics"""
    search_and_send_results(message, message.text)

if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling()