import {Search} from "./search.js";

let search = null;

function onSearch() {
    if (search) {
        search.onSearch();
    }
}

function onExpandDocs(type) {
    if (search) {
        search.onExpandDocs(type);
    }
}

async function init() {
    const labels = await fetch('../assets/data/labels.json')
        .then(data => data.json());
    const str = await fetch('../assets/data/str.json')
        .then(data => data.json());
    const docs = await fetch('../assets/data/docs.json')
        .then(data => data.json());
    const edg = await fetch('../assets/data/egd.json')
        .then(data => data.json());
    const sdg = await fetch('../assets/data/sdg.json')
        .then(data => data.json());
    const values = await fetch('../assets/data/values.json')
        .then(data => data.json());

    search = new Search(labels,str, docs, edg, sdg, values);
}

window.onload = () => {
    window.onSearch = onSearch;
    window.onExpandDocs = onExpandDocs;
    init().then(() => onSearch());
}
