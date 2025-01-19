import json
import itertools
import pymupdf
from thefuzz import fuzz
from path import Path

from shared.setup import *

TARGET_SCORE = 80


def main():
    docs = get_docs_folder()
    text_folder = get_extracted_text_folder()
    output = get_output_file()

    strings = get_strings()
    labels = get_labels()
    indicators = get_indicators(strings, labels)
    topic_map = get_topic_indicator_map(strings)

    extract_text(text_folder, docs)
    search_texts(text_folder, output, indicators, topic_map)


def search_texts(text_folder: Path, output: Path, indicators: dict[str: str], topic_map: dict[str: list[str]]):
    output_file = {}
    ind_amount = len(indicators)
    for i, (key, name) in enumerate(indicators.items()):
        print(f"\r[{i:>3}/{ind_amount:>3}] Search for \"{name}\"", end='')
        for text in text_folder.files():
            if fuzz.partial_ratio(name, text.read_text()) > TARGET_SCORE:
                if key not in output_file:
                    output_file[key] = []
                output_file[key].append(f"{text.stripext().name}.pdf")
            for topic in topic_map[key]:
                if fuzz.partial_ratio(topic, text.read_text()) > TARGET_SCORE:
                    if key not in output_file:
                        output_file[key] = []
                    output_file[key].append(f"{text.stripext().name}.pdf")

    print(f"\r[{ind_amount:>3}/{ind_amount:>3}] Finished searching text")

    with open(output, 'w') as f:
        json.dump(output_file, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()