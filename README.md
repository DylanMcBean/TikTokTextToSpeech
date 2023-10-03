# TikTok TTS Audio Generation

A comprehensive Python tool that harnesses the power of TikTok's TTS (Text-to-Speech) API to produce audio files derived from provided text in a `.txt` file format. Following the text-to-audio conversion, the tool seamlessly stitches all the generated audio segments into a single `.mp3` audio file.

## Features
- Sources text directly from a designated `.txt` file.
- Intelligently segments the text to align with the character constraints of the TTS API.
- Leverages TikTok's TTS API to procure audio segments for each split section of text.
- Seamlessly amalgamates all these audio segments into one unified `.mp3` file.
- Enhances user experience by offering a real-time progress bar to track the conversion status.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/DylanMcBean/TikTokTextToSpeach.git
cd TikTokTextToSpeach
```

2. Set up a virtual environment (optional but highly recommended):

```sh
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install necessary dependencies:

```sh
pip install -r requirements.txt
```

## Usage

1. Prepare a `.txt` file with the text content you're keen to transform into speech.

2. Execute the script, supplying the path of your `.txt` file:

```sh
python main.py path/to/your/textfile.txt
```

Optionally, you can specify the output filename:

```sh
python main.py path/to/your/textfile.txt desired_output_filename.mp3
```

3. Post execution, locate the resulting audio file (defaulted to `processed_audio.mp3` if no name was provided) in the main directory.

## Note on Voice Selection
Upon execution, the script prompts the user to select from a list of diverse voice options, ranging from regional accents to iconic fictional characters!

## Extra

1. For the tool's seamless operation, ensure `ffmpeg` is installed. Additionally, `ffprobe` should either reside in the same directory as the script or be accessible from the `PATH`.
