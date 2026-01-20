# 🎵 Telegram Lyrics Finder Bot

A Python-based Telegram bot that identifies songs based on lyrics. It supports both text input and voice messages, using the Genius API to fetch song details.

## 🌟 Features

* **Text Search:** Type partial lyrics to find a song.
* **Voice Search:** Record yourself singing or humming lyrics; the bot converts the audio to text and performs a search.
* **Smart Matching:** Uses fuzzy logic and keyword cleaning to improve search results.
* **Genius Integration:** Provides direct links to song lyrics on Genius.com.
* **FFmpeg-Free:** Uses `librosa` and `soundfile` for audio conversion, making deployment easier.

## 📋 Prerequisites

* Python 3.8 or higher
* A Telegram Bot Token
* A Genius API Client Access Token

## 🛠️ Installation

1.  **Clone the repository** (or download the files):
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

You need to set up your environment variables to keep your API keys secure.

1.  Create a file named `.env` in the root directory of the project.
2.  Add the following lines to the file, replacing the placeholders with your actual keys:

    ```env
    BOT_TOKEN=your_telegram_bot_token_here
    GENIUS_API_KEY=your_genius_access_token_here
    ```

### How to get tokens:
* **BOT_TOKEN:** Chat with [@BotFather](https://t.me/BotFather) on Telegram and create a new bot.
* **GENIUS_API_KEY:** Sign up at [Genius API Clients](https://genius.com/api-clients), create a new API Client, and copy the **Client Access Token**.

## 🚀 Usage

1.  **Run the bot:**
    ```bash
    python your_script_name.py
    ```

2.  **Open Telegram** and find your bot.
3.  **Start the conversation:**
    * `/start` - Initializes the bot.
    * `/help` - Shows instructions.
4.  **Search:**
    * **Text:** Simply type the lyrics (e.g., "is this the real life is this just fantasy").
    * **Voice:** Hold the microphone button and speak/sing the lyrics clearly.

## 📝 Notes

* **Audio Processing:** The bot creates temporary `.ogg` and `.wav` files during voice processing (`voice_<chat_id>.wav`). These are automatically deleted after processing to save space.
* **Voice Recognition:** The bot uses Google Speech Recognition (`en-US`). For best results, speak clearly and minimize background noise.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
