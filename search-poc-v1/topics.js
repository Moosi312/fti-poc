
export function displayAffectedTopics(id, indicatorToTopicMap, loc, valuesMap) {
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
        el.innerHTML = `
            <div class="topic">
                <div title="${io === 'i' ? 'Input' : io === 'o' ? 'Output' : ''}">
                            ${io === 'i'
                    ? '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M160-160q-33 0-56.5-23.5T80-240v-120h80v120h640v-480H160v120H80v-120q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm300-140-56-58 83-82H80v-80h407l-83-82 56-58 180 180-180 180Z"/></svg>'
                    : io === 'o'
                        ? '<svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8eaed"><path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v80h-80v-80H200v560h560v-80h80v80q0 33-23.5 56.5T760-120H200Zm480-160-56-56 103-104H360v-80h367L624-624l56-56 200 200-200 200Z"/></svg>'
                        : ''
                }
                </div>
                <span class="topic-icon ${getColorClass(valuesMap.get(id))}">
                    <span>${topic}</span>
                </span>
                <span>${l ?? topic}</span>
            </div>
        `;
        topicList.appendChild(el);
    });
}

function getColorClass(topicValues) {
    if (!topicValues || !topicValues['rel.inno']) {
        return 'color-c6';
    }
    const relValue = topicValues['rel.inno'];
    if (relValue < 75) {
        return 'color-c1';
    }
    if (relValue < 90) {
        return 'color-c2';
    }
    if (relValue < 100) {
        return 'color-c3';
    }
    if (relValue < 110) {
        return 'color-c4';
    }
    return 'color-c5';
}
