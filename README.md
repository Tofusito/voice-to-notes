# 🎙️ Voice-to-Notes: Your Audio-to-Markdown Wizard! 🧙‍♂️📝

Welcome to Voice-to-Notes, the magical Python-based tool that transforms your audio files into beautifully structured Markdown notes! Using the power of Whisper.cpp for transcription and cutting-edge AI for content processing, we're here to make your note-taking experience smoother than ever. 🚀

## 📚 Table of Contents

1. [✨ Features](#-features)
2. [🛠️ Requirements](#️-requirements)
3. [🔧 Installation](#-installation)
4. [🚀 Usage](#-usage)
5. [🏗️ Project Structure](#️-project-structure)
6. [🔍 How It Works](#-how-it-works)
7. [⚙️ Configuration](#️-configuration)
8. [🐳 Docker](#-docker)
9. [🤝 Contributing](#-contributing)

## ✨ Features

- 🎤 Converts audio files to text using the lightning-fast Whisper.cpp
- 🧠 Processes transcribed text into structured Markdown notes using AI magic
- 🏷️ Automatically generates catchy titles for your notes
- 📁 Supports processing multiple audio files in one go
- 🐳 Docker integration for smooth sailing deployment

## 🛠️ Requirements

**Essential**
- 🐍 Python 3.x (The more recent, the better!)

**Automatic Dependencies**
Don't worry about these - our wizard will summon them if they're not already in your realm:
- 🐳 Docker
- 🦙 Ollama (Our AI companion)

## 🔧 Installation

1. Clone the repository (It's like summoning the Voice-to-Notes spell book):
```bash
git clone https://github.com/yourusername/voice-to-notes.git
cd voice-to-notes
```

## 🚀 Usage

1. 🎵 Place your audio files in the `input` directory. Think of it as the "To Be Transformed" pile.

2. 🧙‍♂️ Wave your wand (or just run the script):
```bash
python tofu_notes.py
```

3. 🎉 Ta-da! Find your processed Markdown files in the `output_md` directory, ready to be read and enjoyed.

## 🏗️ Project Structure

Let's take a tour of our magical workshop:

- `tofu_notes.py`: 🧠 The brain of the operation, containing all the core spells (functions)
- `templates/template.md`: 📜 The mystical scroll that defines the structure of your notes
- `Dockerfile`: 📦 Instructions for creating our Docker potion
- `input/`: 📂 The arrivals hall for your audio files
- `output/`: 📂 Temporary resting place for Whisper.cpp's whispers
- `output_md/`: 📂 The final destination of your beautifully crafted Markdown notes

## 🔍 How It Works

1. 🕵️‍♂️ Our script checks if the Whisper.cpp potion (Docker image) is ready. If not, it brews a fresh batch.
2. 🎭 Your audio files are processed by Whisper.cpp, which is safely contained in a Docker bottle.
3. 🧠 The transcribed text is sent to our AI companion for some deep thinking.
4. 🏷️ The AI conjures up a title and organizes the content according to our mystical template.
5. 💾 The final Markdown note materializes in the `output_md` directory, ready for your perusal!

## ⚙️ Configuration

While not visible in this spell book, there's likely a secret scroll (configuration file) containing:

- 🔗 The mystical API URL
- 🤖 Which AI model to consult
- 📂 Paths to the input and output realms
- 🐳 The name of our Docker vessel

## 🐳 Docker

We use Docker to contain the powerful Whisper.cpp. The `Dockerfile` is the recipe for this potion, located right next to `tofu_notes.py`.

To manually brew the Docker potion:
```bash
docker build -t whisper-cpp-alpine .
```

## 🤝 Contributing

We welcome all magical beings to contribute! Feel free to send a owl (Pull Request) with your enchantments. Together, we can make Voice-to-Notes even more spellbinding! ✨

Remember, the true magic lies in collaboration. Happy note-taking, wizards! 🧙‍♀️📚🔮
