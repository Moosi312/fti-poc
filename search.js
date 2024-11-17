import {displayRelevantDocsByTopic, displayDocsByType} from "./docs.js";
import {displayAffectedTopics} from "./topics.js";
import {displayRelevantEDGByTopic} from "./egds.js";
import {displayRelevantSDGByTopic} from "./sdgs.js";

export class Search {
    validIndicators = [];
    indicatorToTopicMap = new Map();
    loc = {};
    indicatorLocMap = new Map();
    documents = [];
    egds = [];
    sdgs = [];

    constructor (labels, str, documents, egds, sdgs, values) {
        this.documents = documents;
        this.egds = egds;
        this.sdgs = sdgs;
        this.loc = labels;

        this.valuesMap = new Map(values.map(value => [value['id'], value]));
        this.indicatorToTopicMap = this.getIndicatorMap(str);
        this.validIndicators = Array.from(this.indicatorToTopicMap.keys());
        this.indicatorLocMap = this.getIndicatorLocMap(this.validIndicators, this.loc);

        console.log("Values map", this.valuesMap);
        console.log("Valid Indicators", this.validIndicators);
        console.log("Indicator -> Topic[] map", this.indicatorToTopicMap);
        console.log("Localization", this.loc);
        console.log("Indicator -> Localization map", this.indicatorLocMap);
        console.log("Documents", this.documents);
        console.log("EGDs", this.egds);
        console.log("SDGs", this.sdgs);
    }

    onSearch() {
        let value = document.getElementById('indicator-search').value;

        const id = this.indicatorLocMap.get(value);
        console.log(id);
        if (this.validIndicators.includes(id)) {
            console.log("Search for value ", value, " (ID: ", id, ")");
            displayAffectedTopics(id, this.indicatorToTopicMap, this.loc, this.valuesMap);
            displayRelevantDocsByTopic(id, this.documents, this.indicatorToTopicMap);
            displayRelevantEDGByTopic(id, this.egds, this.indicatorToTopicMap);
            displayRelevantSDGByTopic(id, this.sdgs, this.indicatorToTopicMap);
        }
    }

    onExpandDocs(type) {
        let value = document.getElementById('indicator-search').value;
        const id = this.indicatorLocMap.get(value);
        const topics = this.indicatorToTopicMap.get(id);
        const relDocs = this.documents
            .filter(doc => doc['topicIds'].filter(t => topics.includes(t)).length && doc['type'] === type);
        console.log("Found docs: ", relDocs);
        displayDocsByType(type, relDocs, topics, true);
    }

    getIndicatorMap(str) {
        const map = new Map();
        Object.entries(str).forEach(topic => {
            topic[1]['i'].forEach(indic => {
                if (!map.has(indic)) {
                    map.set(indic, []);
                }
                map.set(indic, map.get(indic).concat(topic[0]));
            })
        })
        return map;
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