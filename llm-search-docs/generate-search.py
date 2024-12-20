import json
import itertools
import os
import time
from datetime import datetime
from time import sleep
from collections import ChainMap

import pymupdf
from dotenv import load_dotenv
from path import Path
from openai import OpenAI

USE_MODEL = 'gpt-4o-mini'


def main():
    docs = Path('../assets/docs/pdf')
    text_folder = Path('./extracted-text')
    prompt_input = Path('./prompt_v2')
    query_input = Path('./prompt_v2')
    batches_file = Path('./batches.jsonl')
    prompt_output = Path('./indicators-for-docs.json')
    output = Path('./docs-by-indicator.json')

    strings = json.loads(Path('../assets/data/str.json').read_text())
    labels = json.loads(Path('../assets/data/labels.json').read_text())
    indicators = get_indicators(strings, labels)

    # print_indicators(indicators)
    # extract_text(docs, text_folder)
    # prompt_query(text_folder, query_input, prompt_output)
    # prompt_batches(text_folder, prompt_input, batches_file, prompt_output)
    invert_map(prompt_output, output, indicators)


def print_indicators(indicators):
    print('\n'.join(indicators.values()))


def get_indicators(strings, labels):
    indicator_keys = list(itertools.chain.from_iterable(ind['i'] for ind in strings.values()))
    indicator_map = {i: labels[i]['short'] for i in indicator_keys}
    return indicator_map


def extract_text(doc_folder: Path, text_folder: Path):
    text_folder.rmtree_p()
    text_folder.mkdir_p()

    file_amount = len(doc_folder.files())

    for i, doc_path in enumerate(doc_folder.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Extract {doc_path.name}", end='')
        output = text_folder / '.'.join(doc_path.name.split('.')[:-1] + ['txt'])
        doc = pymupdf.open(doc_path)
        with open(output, 'wb') as f:
            for page in doc:
                text = page.get_text().encode('utf-8')
                f.write(text)

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished extracting text from PDFs")


def generate_batches(text_folder: Path, prompt_input: Path):
    with open(prompt_input, 'r') as f:
        prompt = f.read()

    return (get_batch_line(prompt, file) for file in text_folder.files())


def get_batch_line(system_prompt: str, file: Path):
    document = file.read_text()
    filename = f"{file.stripext().name}.pdf"
    return {
        "custom_id": filename,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": USE_MODEL,
            "messages": [
                {
                    "content": system_prompt,
                    "role": "system",
                },
                {
                    "content": f"{filename}\n{document}",
                    "role": "user",
                }
            ],
            "max_tokens": 2048,
            "response_format": {
                "type": "json_object"
            },
        }
    }


def prompt_query(text_folder: Path, prompt_input: Path, prompt_output: Path):
    load_dotenv()
    api_key = os.getenv('OPEN_AI_API_TOKEN')

    client = OpenAI(
        api_key=api_key,
        project="proj_oR5I1XR4jtW2dcV6Um9QUbvZ"
    )

    with open(prompt_input, 'r') as f:
        prompt = f.read()
        output = {}

    file_amount = len(text_folder.files())
    for i, file in enumerate(text_folder.files()):
        print(f"\r[{i:>3}/{file_amount:>3}] Prompting for doc {file.name.stripext()}", end='')
        try:
            indicators = make_query(client, prompt, file)
        except Exception as e:
            print(f"\r[ERROR] <{file.name.stripext()}.pdf> {e}")
        else:
            output.update(indicators)
        sleep(15)

    print(f"\r[{file_amount:>3}/{file_amount:>3}] Finished prompts")

    with open(prompt_output, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def prompt_batches(text_folder: Path, prompt_input: Path, batches_file: Path, prompt_output: Path):
    load_dotenv()
    api_key = os.getenv('OPEN_AI_API_TOKEN')

    client = OpenAI(
        api_key=api_key,
        project="proj_oR5I1XR4jtW2dcV6Um9QUbvZ"
    )

    with open(prompt_input, 'r') as f:
        prompt = f.read()
        output = {}

    for file in text_folder.files():
        line = get_batch_line(prompt, file)
        with open(batches_file, 'w') as f:
            json.dump(line, f)

        print(f"[{get_iso_date()}] Prompting for docs {file.name.stripext()}")
        t = time.time()
        data = (prompt_batch(client, batches_file))
        output.update(data)
        print(f"\r[{get_iso_date()}] Prompt finished after {time.time() - t:.2f} seconds")
        print()

    with open(prompt_output, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def prompt_batch(client, batches_file):
    batch_input_file = client.files.create(file=open(batches_file, 'rb'), purpose="batch")
    batch_object = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    batch_id = batch_object.id

    batch_status = client.batches.retrieve(batch_id=batch_id)
    while batch_status.status not in ['cancelled', 'completed', 'expired', 'failed']:
        print(f"\r[{get_iso_date()}] Current status: {batch_status.status}", end='')
        sleep(10)
        batch_status = client.batches.retrieve(batch_id=batch_id)

    print(f"\r[{get_iso_date()}] Current status: {batch_status.status}", end='')

    if batch_status.status != 'completed':
        print(f"\r[{get_iso_date()}] ERROR: unknown error occurred for this request")
        return {}

    if batch_status.output_file_id is None:
        print(f"\r[{get_iso_date()}] ERROR: unknown error occurred for this request")
        return {}

    results = client.files.content(file_id=batch_status.output_file_id)

    dicts = (json.loads(json.loads(line)['response']['body']['choices'][0]['message']['content']) for line in
             results.text.split('\n')[0:-1])

    print(f"\r[{get_iso_date()}] SUCCESS: requests successful")

    return dict(ChainMap(*dicts))


def make_query(client: OpenAI, system_prompt: str, file: Path):
    document = file.read_text()
    response = client.chat.completions.create(
        model=USE_MODEL,
        messages=[
            {
                "content": system_prompt,
                "type": "text",
                "role": "system",
            },
            {
                "content": f"{file.stripext().name}.pdf\n{document}",
                "type": "text",
                "role": "user",
            }
        ],
        response_format={
            "type": "json_object"
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    data = json.loads(response.choices[0].message.content)

    # assert f"{file.stripext().name}.pdf" in data

    return data


def invert_map(map_input, output, indicator_map):
    with open(map_input, 'r') as f:
        orig = json.load(f)
    inverted_ind_map = {v: k for k, v in indicator_map.items()}
    invert = {}

    for file, indicators in orig.items():
        for indicator in indicators:
            if indicator not in inverted_ind_map:
                print(f"Indicator {indicator} not found")
                continue
            ind_id = inverted_ind_map[indicator]
            if ind_id not in invert:
                invert[ind_id] = []
            invert[ind_id].append(file)

    with open(output, 'w') as f:
        json.dump(invert, f, indent=2, ensure_ascii=False)


def get_iso_date():
    return datetime.now().replace(microsecond=0).isoformat()


if __name__ == "__main__":
    main()
