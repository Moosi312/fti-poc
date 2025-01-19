from json import JSONEncoder

import fuzzysearch

from shared.setup import *

FUZZY_SEARCH_TARGET_SCORE = 80

class IndicatorData:
    def __init__(self, name):
        self.indicator_name = name
        self.topics = []
    indicator_name : str
    indicatorFound: int = 0
    topicsFound: int = 0
    topics: list[str]
    year: int = 0
    totalScore: int = 0

class IndicatorDataEncoder(JSONEncoder):
    def default(self, obj: IndicatorData):
        return {
            'indicator_name': obj.indicator_name,
            'indicatorFound': obj.indicatorFound,
            'topicsFound': obj.topicsFound,
            'topics': obj.topics,
            'year': obj.year,
            'totalScore': obj.totalScore
        }

class ScoringValues:
    INDICATOR = 25
    TOPIC = 5
    YEAR_MAX = 10
    CURRENT_YEAR = datetime.now().year
    @staticmethod
    def get_year_value(year: int | None):
        if not int:
            return 0
        return max(0, ScoringValues.YEAR_MAX - (ScoringValues.CURRENT_YEAR - year))


def main():
    docs = get_docs_folder()
    docs_data = get_docs_data()
    text_folder = get_extracted_text_folder()
    intermediary_output = Path('./tmp/search-result.json')
    output = get_output_file()

    strings = get_strings()
    labels = get_labels()
    synonyms = get_synonyms()
    indicators = get_indicators(strings, labels)
    topic_map = get_topic_indicator_map(strings)

    # extract_text(text_folder, docs)
    search = search_texts(text_folder, indicators, topic_map, labels, synonyms, docs_data)

    with open(intermediary_output, 'w') as f:
        json.dump(search, f, indent=2, ensure_ascii=False, cls=IndicatorDataEncoder)

    with open(output, 'w') as f:
        json.dump(rank_search(search), f, indent=2, ensure_ascii=False)


def search_texts(text_folder: Path, indicators: dict[str: str], topic_map: dict[str: list[str]], labels: LABELS_TYPE, synonyms: Dict[str, list[str]], docs_data: DOCS_TYPE) -> Dict[str, Dict[str, IndicatorData]]:
    output_file = {}
    ind_amount = len(indicators)
    for i, (key, name) in enumerate(indicators.items()):
        print(f"\r[{i:>3}/{ind_amount:>3}] Search for \"{name}\"", end='')
        output_file[key] = {}
        indicator_output = output_file[key]
        for text in text_folder.files():
            file_name = f"{text.stripext().name}.pdf"
            year = int(docs_data[file_name]['year']) if file_name in docs_data else 0
            search = search_text_file(key, name, text, topic_map, labels, synonyms, year)
            if search:
                indicator_output[file_name] = search

    print(f"\r[{ind_amount:>3}/{ind_amount:>3}] Finished searching text")

    return output_file


def search_text_file(indicator_id: str, indicator_name: str, text_file: Path, topic_map: dict[str, list[str]], labels: LABELS_TYPE, synonyms: Dict[str, list[str]], year: int) -> IndicatorData | None:
    data = IndicatorData(indicator_name)
    text = text_file.read_text()

    data.indicatorFound = count_found_searches(text, data.indicator_name)
    data.year = year

    for topic in topic_map[indicator_id]:
        topic_name = labels[topic]['short']
        data.topics.append(topic_name)
        data.topicsFound += count_found_searches(text, topic_name)

        if topic in synonyms:
            for syn in synonyms[topic]:
                data.topics.append(syn)
                data.topicsFound += count_found_searches(text, syn)

    if data.topicsFound == 0 and data.indicatorFound == 0:
        return None

    data.totalScore = (data.indicatorFound * ScoringValues.INDICATOR) + (data.topicsFound / len(data.topics) * ScoringValues.TOPIC) + ScoringValues.get_year_value(data.year)
    return data

def count_found_searches(text: str, search_string: str) -> int:
    return len(fuzzysearch.find_near_matches(search_string, text, max_l_dist=2))


def rank_search(search: Dict[str, Dict[str, IndicatorData]]) -> Dict[str, list[str]]:
    output = {}
    for indicator, files in search.items():
        output[indicator] = get_ranked_files(files)

    return output


def get_ranked_files(files: Dict[str, IndicatorData]) -> list[str]:
    return [name for name, _ in sorted(files.items(), key=lambda x: x[1].totalScore, reverse=True)]


if __name__ == "__main__":
    main()