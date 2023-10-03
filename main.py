import requests
import base64
import sys
import re
from pydub import AudioSegment, silence
import io
import time
from typing import List, Tuple, Optional
from tqdm import tqdm


class TextToAudioConverter:

    VOICE_CATEGORIES = {
        "Disney Voices": [
            ("Ghost Face", "en_us_ghostface"),
            ("Chewbacca", "en_us_chewbacca"),
            ("C3PO", "en_us_c3po"),
            ("Stitch", "en_us_stitch"),
            ("Stormtrooper", "en_us_stormtrooper"),
            ("Rocket", "en_us_rocket"),
            ("Madame Leota", "en_female_madam_leota"),
            ("Ghost Host", "en_male_ghosthost"),
            ("Pirate", "en_male_pirate"),
        ],
        "English Voices": [
            ("English AU - Female", "en_au_001"),
            ("English AU - Male", "en_au_002"),
            ("English UK - Male 1", "en_uk_001"),
            ("English UK - Male 2", "en_uk_003"),
            ("English US - Female 1", "en_us_001"),
            ("English US - Female 2", "en_us_002"),
            ("English US - Male 1", "en_us_006"),
            ("English US - Male 2", "en_us_007"),
            ("English US - Male 3", "en_us_009"),
            ("English US - Male 4", "en_us_010"),
        ],
        "English Voices (Other)": [
            ("Narrator", "en_male_narration"),
            ("Wacky", "en_male_funny"),
            ("Peaceful", "en_female_emotional"),
            ("Serious", "en_male_cody"),
        ],
        "Western European": [
            ("French - Male 1", "fr_001"),
            ("French - Male 2", "fr_002"),
            ("German - Female", "de_001"),
            ("German - Male", "de_002"),
            ("Spanish - Male", "es_002"),
        ],
        "South American Languages": [
            ("Spanish MX - Male", "es_mx_002"),
            ("Portuguese BR - Female 1", "br_001"),
            ("Portuguese BR - Female 2", "br_003"),
            ("Portuguese BR - Female 3", "br_004"),
            ("Portuguese BR - Male", "br_005"),
        ],
        "Asian Languages": [
            ("Indonesian - Female", "id_001"),
            ("Japanese - Female 1", "jp_001"),
            ("Japanese - Female 2", "jp_003"),
            ("Japanese - Female 3", "jp_005"),
            ("Japanese - Male", "jp_006"),
            ("Korean - Male 1", "kr_002"),
            ("Korean - Female", "kr_003"),
            ("Korean - Male 2", "kr_004"),
        ],
        "Vocals": [
            ("Alto", "en_female_f08_salut_damour"),
            ("Tenor", "en_male_m03_lobby"),
            ("Sunshine Soon", "en_male_m03_sunshine_soon"),
            ("Warmy Breeze", "en_female_f08_warmy_breeze"),
            ("Glorious", "en_female_ht_f08_glorious"),
            ("It Goes Up", "en_male_sing_funny_it_goes_up"),
            ("Chipmunk", "en_male_m2_xhxs_m03_silly"),
            ("Dramatic", "en_female_ht_f08_wonderful_world"),
        ]
    }

    SILENCE_THRESHOLD = -40
    MIN_SILENCE_LEN = 200
    SPLIT_PATTERN = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    API_ENDPOINT = 'https://tiktok-tts.weilnet.workers.dev/api/generation'
    VOICE = None

    def __init__(self, filename: str):
        self.filename = filename

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
                sections.append(section.strip())
                section = word + ' '
        sections.append(section.strip())
        return sections

    def fetch_audio_for_section(self, section: str, retries: int = 3) -> bytes:
        for _ in range(retries):
            request = requests.post(self.API_ENDPOINT, json={
                                    "text": section, "voice": self.VOICE})
            response = request.json()
            if response.get('data'):
                return base64.b64decode(response['data'])
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

    def get_voice_from_user(self) -> Optional[str]:
        print("\nChoose a voice from the following categories:")
        for idx, category in enumerate(self.VOICE_CATEGORIES.keys(), start=1):
            print(f"{idx}. {category}")

        choice = None
        while True:
            try:
                choice = int(
                    input("\nEnter the number of your chosen category: "))
                if 1 <= choice <= len(self.VOICE_CATEGORIES):
                    break
                print("Invalid choice. Please choose a valid category.")
            except ValueError:
                print("Please enter a number.")

        selected_category = list(self.VOICE_CATEGORIES.keys())[choice - 1]
        print(f"\nYou've selected: {selected_category}")
        print("\nChoose a voice:")

        voices = self.VOICE_CATEGORIES[selected_category]
        for idx, (name, _) in enumerate(voices, start=1):
            print(f"{idx}. {name}")

        voice_choice = None
        while True:
            try:
                voice_choice = int(
                    input("\nEnter the number of your chosen voice: "))
                if 1 <= voice_choice <= len(voices):
                    break
                print("Invalid choice. Please choose a valid voice.")
            except ValueError:
                print("Please enter a number.")

        _, voice_code = voices[voice_choice - 1]
        print(f"You've chosen the voice: {voice_code}")
        return voice_code

    def convert(self, output_filename=None):
        self.VOICE = self.get_voice_from_user()
        sentences = self.get_sentences_from_file(self.filename)
        combined_audio = AudioSegment.empty()
        print("Fetching audio data...")

        for sentence in tqdm(sentences, desc="Processing", ncols=100):
            sentence_audio = AudioSegment.empty()
            for section in self.get_sections_from_sentence(sentence):
                audio_bytes = self.fetch_audio_for_section(section)
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
                cleaned_audio = self.remove_long_pauses(audio_segment)
                sentence_audio += cleaned_audio

            combined_audio += sentence_audio + \
                AudioSegment.silent(duration=500)

        if not output_filename:
            output_filename = input(
                "Enter the output filename (default is processed_audio.mp3): ") or "processed_audio.mp3"
        combined_audio.export(output_filename, format="mp3")
        print(f"Audio data saved as {output_filename}.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python script_name.py [path_to_text_file] [optional_output_filename]")
        sys.exit(1)

    text_filename = sys.argv[1]
    output_filename = sys.argv[2] if len(sys.argv) > 2 else None

    converter = TextToAudioConverter(text_filename)
    converter.convert(output_filename)
