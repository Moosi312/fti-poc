
export function displayAffectedTopics(id, indicatorToTopicMap, loc) {
    const topicList = document.getElementById('topic-list');
    const topics = indicatorToTopicMap.get(id);
    topicList.innerHTML = '';
    console.log("Affected topics: ", topics);
    topics.forEach((topic) => {
        var l = loc[topic]['short']
        var io = loc[id]['io']
        var el = document.createElement('div');
        el.innerHTML = `${topic}: ${l ?? topic} - not i/o`;
        if (io) {
            el.innerHTML = `${topic}: ${l ?? topic} - ${io === 'i' ? 'Input' : 'Output'}`;
        }
        topicList.appendChild(el);
    });
}
