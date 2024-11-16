let options = [];
let optionsTopic = new Map();
let topics = {};
let loc = {};
let optionsLocRev = new Map();
let docs = [];
let edgs = [];
let sdgs = [];

function onSearch() {
    let value = document.getElementById('indicator-search').value;

    id = optionsLocRev.get(value);
    if (options.includes(id)) {
        console.log("Search for value ", value, " (ID: ", id, ")");
        displayAffectedTopics(id);
        displayRelevantDocsByTopic(id);
        displayRelevantEDGByTopic(id);
        displayRelevantSDGByTopic(id);
    }
}

function displayAffectedTopics(id) {
    const topicList = document.getElementById('topic-list');
    topics = optionsTopic.get(id);
    topicList.innerHTML = '';
    console.log("Affected topics: ", topics);
    topics.forEach((topic) => {
        var l = loc[topic]['short']
        var io = loc[id]['io']
        var el = document.createElement('li');
        el.innerHTML = `${topic}: ${l ?? topic} - not i/o`;
        if (io) {
            el.innerHTML = `${topic}: ${l ?? topic} - ${io === 'i' ? 'Input' : 'Output'}`;
        }
        topicList.appendChild(el);
    });
}

function displayRelevantDocsByTopic(id) {
    // const docList = document.getElementById('doc-topic-list');
    topics = optionsTopic.get(id);
    // docList.innerHTML = '';
    const relDocs = docs.filter(doc => doc['topicIds'].filter(t => topics.includes(t)).length);
    console.log("Found docs: ", relDocs);
    // relDocs.forEach(doc => {
    //     relTop = doc['topicIds'].filter(t => topics.includes(t));
    //     var el = document.createElement('div');
    //     el.setAttribute('class', 'doc-wrapper');
    //     el.innerHTML = getDocumentElement(doc);
    //     docList.appendChild(el);
    // })
    const docsMap = new Map();
    relDocs.forEach(doc => {
        const type = doc['type'];
        if (!docsMap.has(type)) {
            docsMap.set(type, []);
        }
        docsMap.get(type).push(doc);
    });
    console.log(docsMap)
    docsMap.forEach((value, key) => {
        displayDocsByType(key, value, topics);
    })
}

function displayDocsByType(type, docs, topics) {
    console.log(type, docs);
    const docList = document.getElementById(`doc-list-${type}`);
    docList.innerHTML = '';
    docs.slice(0, 3).forEach((doc) => {
        relTop = doc['topicIds'].filter(t => topics.includes(t));
        var el = document.createElement('div');
        el.setAttribute('class', 'doc-wrapper');
        el.innerHTML = getDocumentElement(doc, topics);
        docList.appendChild(el);
    })
    if (docs.length > 3) {
        const el = document.createElement('span');
        el.innerHTML = 'More...';
        docList.appendChild(el);
    }
}

function getDocumentElement(doc, topics) {
    const relTop = doc['topicIds'].filter(t => topics.includes(t));
    return (
    `<a href="docs/pdf/${doc['file']}" class="document">
        <img src="/docs/img/${doc['file']}.png" alt="PDF"/>
        <div class="doc-content">
            <span class="doc-title">${doc['name']}</span>
            <span class="doc-institute">Inst?</span>
            <span>${doc['year']}</span>
            <span>${relTop.join(', ')}</span>
        </div>
    </a>`
    );
}

function displayRelevantEDGByTopic(id) {
    const docList = document.getElementById('edg-topic-list');
    topics = optionsTopic.get(id);
    docList.innerHTML = '';
    const relDocs = edgs.filter(doc => doc['bereiche'].filter(t => topics.includes(t)).length);
    console.log("Found edgs: ", relDocs);
    relDocs.forEach(doc => {
        relTop = doc['bereiche'].filter(t => topics.includes(t));
        var el = document.createElement('li');
        el.innerHTML = `<a href="${doc['url']}">${doc['goal-de']} - ${doc['indicator-de']} (${relTop.join(',')})</a>`;
        docList.appendChild(el);
    })
}

function displayRelevantSDGByTopic(id) {
    const docList = document.getElementById('sdg-topic-list');
    topics = optionsTopic.get(id);
    docList.innerHTML = '';
    const relDocs = sdgs.filter(doc => doc['bereiche'].filter(t => topics.includes(t)).length);
    console.log("Found sdgs: ", relDocs);
    relDocs.forEach(doc => {
        relTop = doc['bereiche'].filter(t => topics.includes(t));
        var el = document.createElement('li');
        el.innerHTML = `<a href="${doc['url']}">${doc['name-de']} - ${doc['indicator-de']} (${relTop.join(',')})</a>`;
        docList.appendChild(el);
    })
}

async function init() {
    await fetch('/data/labels.json')
        .then(data => data.json())
        .then(data => loc = data);
    await fetch('/data/str.json')
        .then(data => data.json())
        .then(data => {
            topics = data
            Object.entries(data).forEach(topic => {
                topic[1]['i'].forEach(indic => {
                    if (!optionsTopic.has(indic)) {
                        optionsTopic.set(indic, []);
                    }
                    optionsTopic.set(indic, optionsTopic.get(indic).concat(topic[0]));
                })
            })
        });
    await fetch('/data/docs.json')
        .then(data => data.json())
        .then(data => docs = data);
    await fetch('/data/egd.json')
        .then(data => data.json())
        .then(data => edgs = data);
    await fetch('/data/sdg.json')
        .then(data => data.json())
        .then(data => sdgs = data);

    console.log(loc);
    console.log(topics);
    console.log(optionsTopic);
}

async function getOptions() {
    options = Array.from(optionsTopic.keys());
    const list = document.getElementById('indicators-list');
    list.innerHTML = '';
    optionsLocRev.clear();
    options.forEach(option => {
        var el = document.createElement('option');
        const l = loc[option]['short'];
        el.setAttribute('value', l ?? option);
        list.appendChild(el);
        if (l) {
            optionsLocRev.set(l, option);
        }
    })
    console.log(options);
}

init().then(() => getOptions()).then(() => onSearch());