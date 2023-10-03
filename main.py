import requests
import base64
import sys
import re
from pydub import AudioSegment, silence
from tqdm import tqdm
import io

def get_sentences_from_file(filename):
    with open(filename, 'r') as file:
        text = file.read().replace('\n', ' ')
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

def get_sections_from_sentence(sentence):
    words = sentence.split()
    sections = []
    section = ''
    for word in words:
        if len(section + word) <= 300:
            section += word + ' '
        else:
            sections.append(section.strip())
            section = word + ' '
    sections.append(section.strip())
    return sections

def fetch_audio_for_section(section):
    request = requests.post('https://tiktok-tts.weilnet.workers.dev/api/generation', json={"text": section, "voice": "en_us_006"})
    response = request.json()
    return base64.b64decode(response['data'])

def remove_long_pauses(audio_segment, silence_threshold=-40, min_silence_len=200):
    chunks = silence.split_on_silence(
        audio_segment,
        min_silence_len=min_silence_len,
        silence_thresh=silence_threshold
    )
    return sum(chunks, AudioSegment.empty())

def main():
    if len(sys.argv) < 2:
        print("Usage: python script_name.py [path_to_text_file]")
        sys.exit(1)

    filename = sys.argv[1]
    sentences = get_sentences_from_file(filename)

    combined_audio = AudioSegment.empty()
    print("Fetching audio data...")

    for sentence in tqdm(sentences):
        sentence_audio = AudioSegment.empty()

        for section in get_sections_from_sentence(sentence):
            audio_bytes = fetch_audio_for_section(section)
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            cleaned_audio = remove_long_pauses(audio_segment)
            sentence_audio += cleaned_audio

        combined_audio += sentence_audio + AudioSegment.silent(duration=500)  # 500ms pause between sentences

    combined_audio.export("processed_audio.mp3", format="mp3")
    print("Audio data saved as processed_audio.mp3.")

if __name__ == "__main__":
    main()
