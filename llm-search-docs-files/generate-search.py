import itertools
import json
import os
from collections import namedtuple
from pydoc_data.topics import topics
from time import sleep, time

import openai
from dotenv import load_dotenv
from openai import OpenAI
from path import Path

from shared.setup import get_iso_date, get_topic_indicator_map

USE_MODEL = 'gpt-4o-mini'
TEMPERATURE = 0.5
OWN_FOLDER = './llm-search-docs-files/'
OUTPUT_FILE = 'docs-by-indicator.json'
TMP_FOLDER = 'tmp/'
PROMPTS_FOLDER = 'prompts/'
TEMPLATE_FILE = 'prompt-template.json'
STRINGS_FILE = './assets/data/str.json'
LABELS_FILE = './assets/data/labels.json'
VECTOR_STORE_ID = 'vs_6803b9602b4c8191912750177c220dc2'


Topic = namedtuple('Topic', ['name', 'synonyms'])
Indicator = namedtuple('Indicator', ['name', 'topics', 'synonyms'])


def main():
    load_dotenv()
    api_key = os.getenv('OPEN_AI_API_TOKEN')
    client = OpenAI(
        api_key=api_key,
        project="proj_oR5I1XR4jtW2dcV6Um9QUbvZ"
    )
    own_folder = Path(OWN_FOLDER)
    tmp_folder = own_folder / TMP_FOLDER
    if not tmp_folder.exists():
        tmp_folder.makedirs()
    prompts_folder = tmp_folder / PROMPTS_FOLDER
    if not prompts_folder.exists():
        prompts_folder.makedirs()
    output_file = own_folder / OUTPUT_FILE
    prompt_for_indicators(get_indicators(Path(STRINGS_FILE), Path(LABELS_FILE)), json.loads((own_folder / TEMPLATE_FILE).read_text()), output_file, tmp_folder / PROMPTS_FOLDER, client)


def get_indicator_names(indicator_file: Path):
    data = json.loads(indicator_file.read_text())
    return data


def get_indicators(strings_file: Path, labels_file: Path) -> dict[str, Indicator]:
    strings = json.loads(strings_file.read_text())
    indicators = get_topic_indicator_map(strings)
    labels: dict[str, str] = {key: data['short'] for key, data in json.loads(labels_file.read_text()).items()}

    return {
        indicator: get_indicator(indicator, topics, labels) for indicator, topics in indicators.items()
    }


def get_indicator(indicator: str, topics: list[str], labels: dict[str, str]) -> Indicator:
    return Indicator(labels[indicator], [Topic(labels[topic], []) for topic in topics], [])


def prompt_for_indicators(indicators: dict[str, Indicator], template: dict[str, str], output_file: Path, prompts_folder: Path, client: OpenAI):
    output = {}
    total = len(indicators)
    for i, (key, indicator) in enumerate(indicators.items()):
        print(f"[{get_iso_date()}] ({i+1}/{total}) Prompting for Indicator \"{indicator.name}\"", end='')
        t = time()
        prompt = generate_prompt(template, indicator)
        prompt_file = prompts_folder / f'{key}.txt'
        prompt_file.write_text(prompt)
        response = make_query(prompt, client)
        output.update({key: response})
        print(f"\r[{get_iso_date()}] ({i+1}/{total}) Prompt for Indicator \"{indicator.name}\" finished after {time() - t:.2f} seconds with {len(response)} documents found")

    with open(output_file, 'w', encoding='UTF-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

def generate_prompt(template_strings: dict[str, str], indicator: Indicator) -> str:
    prompt = template_strings['intro'] + '\n\n'
    prompt +=  template_strings['indicator'].replace('{{indicator}}', indicator.name)
    prompt += '\n'
    if len(indicator.synonyms) > 0:
        prompt += template_strings['synonyms'].replace('{{indicator}}', ', '.join(indicator.synonyms))
    for topic in indicator.topics:
        prompt += template_strings['topic'].replace('{{topic}}', topic.name)
        if len(topic.synonyms) > 0:
            prompt += template_strings['synonyms'].replace('{{indicator}}', ', '.join(topic.synonyms))
        prompt += '\n'
    prompt += '\n' + template_strings['outro']
    return prompt


def make_query_request(prompt: str, client: OpenAI) -> list[str]:
    response = client.responses.create(
        model=USE_MODEL,
        input=prompt,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [VECTOR_STORE_ID]
        }],
    )

    json_response = client.responses.create(
        model=USE_MODEL,
        input='Extract the JSON file from this :\n' + response.output_text,
        text = {
            "format": {
                "type": "json_schema",
                "name": "files",
                "schema": {
                    "type": "object",
                    "properties": {
                        "fileNames": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                    },
                    "required": ["fileNames"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
    )

    values = json.loads(json_response.output_text)['fileNames']
    if len(values) < 1:
        print(f"\r[{get_iso_date()}] ERROR: no indicators found : {values}")
    return values


def make_query(prompt: str, client: OpenAI, waited=False) -> list[str]:
    try:
        return make_query_request(prompt, client)
    except openai.RateLimitError:
        if not waited:
            print(f"\r[WARN] Rate limit exceeded. Waiting for one minute")
            sleep(60)
            return make_query(prompt, client, True)
    except Exception as e:
        print(f"\r[ERROR] {e}")
        return []



if __name__ == "__main__":
    main()
