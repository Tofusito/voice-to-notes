# Whisper to Markdown Processing Pipeline

## Overview

This project is designed to automate the process of converting audio files into well-structured Markdown notes. The pipeline utilizes Docker, Whisper.cpp, and a custom Python script to transcribe audio files, format the transcription according to a Markdown template, and then enhance the transcription by sending it to a language model API for further processing.

## Tools and Technologies Used

- **Ollama**: A lightweight all-in-one LLM that supports a variety of models, including Whisper.
- **Docker**: Used to run Whisper.cpp in a containerized environment, ensuring consistency across different systems.
- **Whisper.cpp**: A lightweight and efficient implementation of OpenAI’s Whisper model, used here to transcribe audio files.
- **Python**: The primary language for scripting the automation process, including handling Docker, sending requests to the language model API, and processing files.
- **Requests** (Python library): Utilized to send HTTP POST requests to the language model API.
- **Markdown**: The output format for the transcriptions, structured according to a predefined template.
- **AI Models**:
    - **Whisper.cpp**: Handles the transcription of audio files into text. It is a reduced version wrote in C++ of the original Whisper by OpenAI
    - **LLaMA (Large Language Model Meta AI)**: Specifically, the model llama3.1:latest, is used to process the transcribed text, improving and structuring it according to the provided Markdown template.

## Requirements

- Ollama: Ensure you have Llama3.1:latest instaled.
- Docker: Ensure Docker is installed and running on your machine.
- Python 3.x: Required to run the script.
- Python libraries:
  - `requests`
- Whisper.cpp Docker Image: Ensure the `whisper-cpp-alpine` Docker image is available locally.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/whisper-to-markdown.git
   cd whisper-to-markdown

2. **Install Python Dependencies**:
Ensure you have requests installed:
   ```bash
   pip install requests
```
3. ** Run the pipeline**:
    - Place your audio files in the inputs directory.
    - Execute the Python script:
```bash
    pip install requests
```

## Usage

1. **Place Audio Files**:
   - Place all audio files you want to transcribe in the `inputs` directory. Supported formats include `.wav`, `.mp3`, `.m4a`, `.ogg`, and `.flac`.
   
2. **Run the Script**:
   - Execute the Python script to start the process. The script will first run the Docker container to transcribe the audio files, then process the transcriptions with the LLaMA API, and finally save the structured Markdown output in the `outputs_md` directory.

3. **Output**:
   - The final Markdown files will be available in the `outputs_md` directory, named according to the original audio files.

## Example

**Input:**

- `inputs/meeting_audio.mp3`

**Output:**

- `outputs_md/meeting_audio.md`

## Project Structure

```bash
.
├── inputs/           # Directory for input audio files
├── outputs/          # Directory where Whisper.cpp saves transcriptions
├── outputs_md/       # Directory where the final Markdown files are saved
├── templates/        # Directory containing the Markdown template
│   └── template.md   # Markdown template used for structuring the output
├── main.py           # Main Python script that orchestrates the process
└── README.md         # Project documentation

## Additional Information

- **Error Handling**:
  - The script includes error handling for Docker execution and API requests. If an error occurs during any part of the process, it will be logged, and the script will attempt to continue processing remaining files.

- **Performance**:
  - The pipeline is designed for batch processing. Depending on the number of audio files and their duration, the processing time may vary. The total execution time is displayed at the end of the process.

## Conclusion

This project provides an automated and efficient solution for converting audio transcriptions into structured Markdown documents, leveraging the power of Docker and advanced language models. It’s a versatile tool that can be adapted for various use cases, such as meeting notes, podcast transcriptions, or lecture summaries.