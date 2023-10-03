# TikTok TTS Audio Generation

A simple Python script that utilizes the TikTok TTS (Text-to-Speech) API to generate audio files from the text provided in a `.txt` file. The tool then combines all the generated audio snippets into a single `.mp3` file.

## Features
- Takes text from a provided `.txt` file.
- Splits the text into sections, ensuring each is within the character limit for the TTS API.
- Downloads audio snippets for each section using TikTok's TTS API.
- Combines all snippets into a single, continuous `.mp3` file.
- Provides progress tracking using a progress bar.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/DylanMcBean/TikTokTextToSpeach.git
cd TikTokTextToSpeach
```

2. Set up a virtual environment (optional but recommended):

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required dependencies:

```sh
pip install -r requirements.txt
```

## Usage

1. Prepare a `.txt` file with the text you wish to convert to speech.

2. Run the script by passing the path to the `.txt` file:

```sh
python main.py path/to/your/textfile.txt
```

3. After execution, you'll find a file named `combined_audio.mp3` in the directory.

## Extra

1. You will also need to have ffmpeg installed, and have `ffprobe` in the same folder as the script or in `PATH`
