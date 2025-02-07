import itertools
import json
from datetime import datetime
from typing import Dict, List

from path import Path
from pymupdf import pymupdf

from shared.ftiTypings import STRINGS_TYPE, LABELS_TYPE, INDICATOR_TYPE, DOCS_TYPE

USE_MODEL = "gpt-4o-mini"

def extract_text(extracted_text_folder: Path, pdf_folder: Path):
    extracted_text_folder.rmtree_p()
    extracted_text_folder.mkdir_p()

    file_amount = len(pdf_folder.files())

    for i, doc_path in enumerate(pdf_folder.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Extract {doc_path.name}", end='')
        output = extracted_text_folder / '.'.join(doc_path.name.split('.')[:-1] + ['txt'])
        doc = pymupdf.open(doc_path)
        with open(output, 'wb', encoding='UTF-8') as f:
            for page in doc:
                text = page.get_text().encode('utf-8')
                f.write(text)

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished extracting text from PDFs")

def get_docs_folder(docs_folder: str= '../assets/docs/pdf') -> Path:
    return Path(docs_folder)

def get_docs_data() -> DOCS_TYPE:
    return {file['file']: file for file in json.loads(Path('../assets/data/docs.json').read_text('UTF-8'))}

def get_extracted_text_folder(extracted_text_folder: str= './tmp/extracted-text') -> Path:
    folder = Path(extracted_text_folder)
    folder.makedirs_p()
    return folder

def get_output_file(output_file: str= './docs-by-indicator.json') -> Path:
    return Path(output_file)

def get_strings() -> STRINGS_TYPE:
    return json.loads(Path('../assets/data/str.json').read_text('UTF-8'))

def get_labels() -> LABELS_TYPE:
    return json.loads(Path('../assets/data/labels.json').read_text('UTF-8'))

def get_synonyms() -> Dict[str, list[str]]:
    return json.loads(Path('../shared/synonym.json').read_text('UTF-8'))

def get_iso_date() -> str:
    return datetime.now().replace(microsecond=0).isoformat()

def get_topic_indicator_map(strings: STRINGS_TYPE) -> Dict[str, List[str]]:
    topic_indicator_map = {}
    for topic, data in strings.items():
        for indicator in data['i']:
            if indicator not in topic_indicator_map:
                topic_indicator_map[indicator] = []
            topic_indicator_map[indicator].append(topic)
    return topic_indicator_map


def get_topics_for_indicator(indicator: str, topic_indicator_map: Dict[str, List[str]]) -> List[str]:
    if indicator not in topic_indicator_map:
        return []
    return topic_indicator_map[indicator]

def get_indicators(strings: STRINGS_TYPE, labels: LABELS_TYPE) -> INDICATOR_TYPE:
    indicator_keys = list(itertools.chain.from_iterable(ind['i'] for ind in strings.values()))
    indicator_map = {i: labels[i]['short'] for i in indicator_keys}
    return indicator_map
