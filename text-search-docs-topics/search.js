import {displayRelevantDocs, displayDocsByType} from "./docs.js";

export class Search {
    validIndicators = new Set();
    loc = {};
    documents = [];
    indicatorDocumentMap = {};

    constructor (labels, str, documents, indicatorDocumentMap) {
        this.documents = documents;
        this.loc = labels;
        this.indicatorDocumentMap = indicatorDocumentMap;

        this.validIndicators = this.getValidIndicators(str);
        this.indicatorLocMap = this.getIndicatorLocMap(this.validIndicators, this.loc);

        console.log("Valid Indicators", this.validIndicators);
        console.log("Localization", this.loc);
        console.log("Indicator -> Localization map", this.indicatorLocMap);
        console.log("Documents", this.documents);
    }

    onSearch() {
        let value = document.getElementById('indicator-search').value;

        const id = this.indicatorLocMap.get(value);
        if (this.validIndicators.has(id)) {
            console.log("Search for value ", value, " (ID: ", id, ")");
            displayRelevantDocs(id, this.documents, this.indicatorDocumentMap);
        }
    }

    onExpandDocs(type) {
        let value = document.getElementById('indicator-search').value;
        const id = this.indicatorLocMap.get(value);
        const docs = this.indicatorDocumentMap[id];
        if (!docs) {
            return;
        }
        const relDocs = docs.map(doc => this.documents.find(d => d['file'] === doc)).filter(doc => doc && doc['type'] === type);
        console.log("Found docs: ", relDocs);
        displayDocsByType(type, relDocs, true);
    }

    getValidIndicators(str) {
        return new Set(Object.entries(str).flatMap(topic => topic[1]['i']));
    }

    getIndicatorLocMap(indicators, loc) {
        const map = new Map();
        const list = document.getElementById('indicators-list');
        list.innerHTML = '';
        map.clear();
        indicators.forEach(option => {
            const el = document.createElement('option');
            const l = loc[option]['short'];
            el.setAttribute('value', l ?? option);
            list.appendChild(el);
            if (l) {
                map.set(l, option);
            }
        })
        return map;
    }
}