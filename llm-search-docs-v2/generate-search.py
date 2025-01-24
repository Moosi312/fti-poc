from shared.chatGPTclient import ChatGPTClient
from shared.setup import get_topics_for_indicator

USE_MODEL = 'gpt-4o-mini'


def main():
    client = ChatGPTClient(USE_MODEL, prompt_template='./prompt_v4')

    client.set_prompt(generate_promt(client.get_prompt_template(), client))
    # client.extract_text()
    client.prompt_query()
    client.invert_map()


def generate_promt(prompt_template: str, client: ChatGPTClient) -> str:
    return (prompt_template +
            '\n' +
            '\n'.join([get_indicator_line(key, value, client) for key, value in client.indicators.items()]))


def get_indicator_line(indicator_key: str, indicator_name: str, client: ChatGPTClient) -> str:
    topics = [client.labels[topic]['short'] for topic in get_topics_for_indicator(indicator_key, client.topicIndicatorMap)]
    topics_line = f"In den Bereichen: {', '.join(topics)}" if len(topics) != 1 else f"Im Bereich: {topics[0]}"
    return f"\"{indicator_name}\": \"{client.labels[indicator_key]['text']}. {topics_line}\""

if __name__ == "__main__":
    main()
