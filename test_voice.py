#!/usr/bin/env python3
"""Test script to diagnose voice processing issues"""

import os
import sys
import subprocess

print("🔍 Diagnosing voice processing setup...\n")

# Check 1: FFmpeg
print("1. Checking FFmpeg...")
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        print("   ✓ FFmpeg is installed and working")
    else:
        print("   ✗ FFmpeg exists but not working")
except FileNotFoundError:
    print("   ✗ FFmpeg NOT found in system PATH")
    print("   → Install from: https://ffmpeg.org/download.html")
    print("   → Or: pip install pydub-stubs")

# Check 2: Required Python packages
print("\n2. Checking Python packages...")
packages = ['telebot', 'speech_recognition', 'pydub', 'requests', 'python-dotenv', 'rapidfuzz']
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_').split('-')[0])
        print(f"   ✓ {pkg}")
    except ImportError:
        print(f"   ✗ {pkg} - MISSING")

# Check 3: Environment variables
print("\n3. Checking environment variables...")
from dotenv import load_dotenv
load_dotenv()

bot_token = os.environ.get('BOT_TOKEN')
genius_key = os.environ.get('GENIUS_API_KEY')

if bot_token:
    print(f"   ✓ BOT_TOKEN configured")
else:
    print(f"   ✗ BOT_TOKEN not found in .env")

if genius_key:
    print(f"   ✓ GENIUS_API_KEY configured")
else:
    print(f"   ⚠ GENIUS_API_KEY not found (optional)")

# Check 4: Test speech recognition
print("\n4. Testing Speech Recognition...")
try:
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    print("   ✓ speech_recognition module loaded")
except Exception as e:
    print(f"   ✗ Error loading speech_recognition: {e}")

# Check 5: Test audio file conversion
print("\n5. Testing audio conversion...")
try:
    from pydub import AudioSegment
    print("   ✓ pydub loaded")
    print("   ⚠ Note: pydub requires ffmpeg to convert OGG to WAV")
except Exception as e:
    print(f"   ✗ Error with pydub: {e}")

print("\n" + "="*50)
print("SUMMARY:")
print("="*50)
print("""
The main requirement for voice support is FFmpeg.

If you see ✗ for FFmpeg above:
1. Download from: https://ffmpeg.org/download.html
2. Extract and add to your system PATH
3. Or place ffmpeg.exe in: d:\\Downloads\\TelegramBot\\

Then restart the bot and try sending a voice message.
""")
