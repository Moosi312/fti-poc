
export function displayRelevantDocs(id, docs, indicatorDocumentMap) {
    const relDocs = indicatorDocumentMap[id];
    if (!relDocs) {
        return;
    }
    console.log("Found docs: ", relDocs);
    const docsMap = new Map();
    relDocs.forEach(relDoc => {
        const doc = docs.find(doc => doc['file'] === relDoc);
        if (!doc) {
            console.log("Not found: ", relDoc);
            return;
        }
        const type = doc['type'];
        if (!docsMap.has(type)) {
            docsMap.set(type, []);
        }
        docsMap.get(type).push(doc);
    });
    console.log("Docs map", docsMap)
    docsMap.forEach((value, key) => {
        displayDocsByType(key, value);
    })
}

export function displayDocsByType(type, docs, expanded = false) {
    console.log(type, docs);
    const docList = document.getElementById(`doc-list-${type}`);
    docList.innerHTML = '';
    (expanded ? docs : docs.slice(0, 3)).forEach((doc) => {
        const el = document.createElement('div');
        el.setAttribute('class', 'doc-wrapper');
        el.innerHTML = getDocumentElement(doc);
        docList.appendChild(el);
    })
    if (docs.length > 3 && !expanded) {
        const el = document.createElement('button');
        el.classList.add('docs-expand');
        el.setAttribute('onclick', `onExpandDocs('${type}')`)
        el.innerHTML = `▼ &nbsp; Alle ${docs.length} anzeigen`;
        docList.appendChild(el);
    }
}

function getDocumentElement(doc) {
    return (
        `<a href="../assets/docs/pdf/${doc['file']}" target="_blank" class="document">
            <img src="../assets/docs/img/${doc['file']}.png" alt="PDF"/>
            <div class="doc-content">
                <span class="doc-title">${doc['name']}</span>
                <span class="doc-institute">Inst?</span>
                <span>${doc['year']}</span>
            </div>
        </a>`
    );
}

function getTopicIcon(topic) {
    return `
        <span class="topic-icon">
            <span>${topic}</span>
        </span>
    `
}
