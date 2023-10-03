import requests
import base64
import sys
from pydub import AudioSegment
from tqdm import tqdm
import io


def get_sections_from_file(filename):
    with open(filename, 'r') as file:
        text = [word for word in file.read().split(' ') if word != '']

    sections = []
    section = ''
    for word in text:
        if len(section + word) < 300:
            section += word + ' '
        else:
            sections.append(section)
            section = word + ' '
    sections.append(section)
    return sections


def fetch_audio_for_section(section):
    request = requests.post('https://tiktok-tts.weilnet.workers.dev/api/generation', json={"text": section, "voice": "en_us_006"})
    response = request.json()
    return base64.b64decode(response['data'])


def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py [path_to_text_file]")
        sys.exit(1)

    filename = sys.argv[1]
    sections = get_sections_from_file(filename)

    combined_audio = AudioSegment.empty()

    print("Fetching audio data...")
    for section in tqdm(sections):
        audio_bytes = fetch_audio_for_section(section)
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
        combined_audio += audio_segment

    combined_audio.export("combined_audio.mp3", format="mp3")
    print("Audio data saved as combined_audio.mp3.")


if __name__ == "__main__":
    main()
