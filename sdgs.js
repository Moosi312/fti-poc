
export function displayRelevantSDGByTopic(id, sdgs, indicatorToTopicMap) {
    const docList = document.getElementById('sdg-topic-list');
    const topics = indicatorToTopicMap.get(id);
    docList.innerHTML = '';
    const relDocs = sdgs.filter(doc => doc['bereiche'].filter(t => topics.includes(t)).length);
    console.log("Found sdgs: ", relDocs);
    const sdgMap = new Map();
    relDocs.forEach(doc => {
        const topicId = doc['no'];
        if (!sdgMap.has(topicId)) {
            sdgMap.set(topicId, []);
        }
        sdgMap.set(topicId, sdgMap.get(topicId).concat([doc]));
    })
    sdgMap.forEach((doc, no) => {
        docList.appendChild(getSDGTopicElement(no, doc));

    })
}

function getSDGTopicElement(number, sdgs) {
    const name = sdgs[0]['name-de']
    const el = document.createElement('div');
    el.innerHTML = `
        <div class="sdg">
            <div class="sdg-title">
                <div class="sdg-number">
                    <span>${number}</span>
                </div>
                <span class="sdg-name">${name}</span>
            </div>
            <ul>
                ${sdgs.map(sdg => getSDGElement(sdg)).join('')}
            </ul>
        </div>
    `;
    return el;
}

function getSDGElement(sdg) {
    return `
        <li class="sdg-element">
            <a href="${sdg['url']}">
                <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="100" height="100" viewBox="0 0 24 24">
                    <path d="M 5 3 C 3.9069372 3 3 3.9069372 3 5 L 3 19 C 3 20.093063 3.9069372 21 5 21 L 19 21 C 20.093063 21 21 20.093063 21 19 L 21 12 L 19 12 L 19 19 L 5 19 L 5 5 L 12 5 L 12 3 L 5 3 z M 14 3 L 14 5 L 17.585938 5 L 8.2929688 14.292969 L 9.7070312 15.707031 L 19 6.4140625 L 19 10 L 21 10 L 21 3 L 14 3 z"></path>
                </svg>
                <span>${sdg['indicator-de']}</span>
            </a>
        </li>
    `;
}
