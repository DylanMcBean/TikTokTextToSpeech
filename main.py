import requests
import base64
import sys
import re
from pydub import AudioSegment, silence
import io
import time
from typing import List
from tqdm import tqdm

class TextToAudioConverter:

    SILENCE_THRESHOLD = -40
    MIN_SILENCE_LEN = 200
    SPLIT_PATTERN = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    API_ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev/api/generation'
    VOICE = "en_us_006"
    
    VOICES = {
        "US FEMALE": "en_us_001",
        "US MALE": "en_us_006",
        "UK MALE": "en_uk_001",
        "AU FEMALE": "en_au_001",
        "AU MALE": "en_au_002",
        "FRENCH MALE": "fr_001",
        "GERMAN FEMALE": "de_001",
        "GERMAN MALE": "de_002",
        "GHOSTFACE": "en_us_ghostface",
        "CHEWBACCA": "en_us_chewbacca",
        "C3PO": "en_us_c3po",
        "STITCH": "en_us_stitch",
        "STORMTROOPER": "en_us_stormtrooper",
        "ROCKET": "en_us_rocket"
    }

    def __init__(self, filename: str, output_filename: str = "processed_audio.mp3", voice: str = VOICE):
        self.filename = filename
        self.output_filename = output_filename
        self.voice = voice

    @staticmethod
    def get_sentences_from_file(filename: str) -> List[str]:
        with open(filename, 'r') as file:
            text = file.read().replace('\n', ' ')
        return re.split(TextToAudioConverter.SPLIT_PATTERN, text)

    @staticmethod
    def get_sections_from_sentence(sentence: str) -> List[str]:
        words = sentence.split()
        sections = []
        section = ''
        for word in words:
            if len(section + word) <= 300:
                section += word + ' '
            else:
                if section.strip() and not all(c in '.?! ' for c in section):
                    sections.append(section.strip())
                section = word + ' '
        if section.strip() and not all(c in '.?! ' for c in section):
            sections.append(section.strip())
        return sections

    def fetch_audio_for_section(self, section: str, retries: int = 3) -> bytes:
        for _ in range(retries):
            request = requests.post(self.API_ENDPOINT, json={"text": section, "voice": self.voice})
            response = request.json()
            if response.get('data'):
                return base64.b64decode(response['data'])
            else:
                time.sleep(1)
        raise ValueError(f"Failed to fetch audio for section: {section}")

    @staticmethod
    def remove_long_pauses(audio_segment: AudioSegment) -> AudioSegment:
        chunks = silence.split_on_silence(
            audio_segment,
            min_silence_len=TextToAudioConverter.MIN_SILENCE_LEN,
            silence_thresh=TextToAudioConverter.SILENCE_THRESHOLD
        )
        return sum(chunks, AudioSegment.empty())

    def convert(self) -> None:
        sentences = self.get_sentences_from_file(self.filename)

        combined_audio = AudioSegment.empty()
        print("Fetching audio data...")

        for sentence in tqdm(sentences, desc="Processing sentences"):
            sentence_audio = AudioSegment.empty()
            for section in self.get_sections_from_sentence(sentence):
                audio_bytes = self.fetch_audio_for_section(section)
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                cleaned_audio = self.remove_long_pauses(audio_segment)
                sentence_audio += cleaned_audio

            combined_audio += sentence_audio + AudioSegment.silent(duration=500)  # 500ms pause between sentences

        combined_audio.export(self.output_filename, format="mp3")
        print(f"Audio data saved as {self.output_filename}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py [path_to_text_file] [optional_output_filename]")
        sys.exit(1)

    output_filename = "processed_audio.mp3"
    if len(sys.argv) >= 3:
        output_filename = sys.argv[2]

    print("Please select a voice:")
    for idx, voice_name in enumerate(TextToAudioConverter.VOICES.keys(), 1):
        print(f"{idx}. {voice_name}")

    choice = int(input("Enter your choice (number): "))
    if choice < 1 or choice > len(TextToAudioConverter.VOICES):
        print("Invalid choice.")
        sys.exit(1)

    selected_voice = list(TextToAudioConverter.VOICES.values())[choice - 1]

    converter = TextToAudioConverter(sys.argv[1], output_filename, selected_voice)
    converter.convert()
