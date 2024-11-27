# FTI - Proof of Concept

Deployed via GitHub pages [https://poc.fti.mooslechner.dev](https://poc.fti.mooslechner.dev)

This is a collection of all proof of concects, tests and mock-ups put to code for the FTI improvement project.

The main page will give an overview of all PoCs.

## Search PoC V1

This was simply to test the fesibility of a search functionality with the provided json files.

The search allows the user to enter a Indicator and for this will return the topics it can be found in. For those topics it will provide all relevant documents / EDGs / SGDs.

#### Findings

 - Connection between topics and goals must be hardcoded, cant be found in the json configs
 - Indicators in the json config are only marked as input/output for the entire project, but should be in-/output depending on topic. This must be hard-coded.

#### Feedback

 - There is no good way to link indicators to docs
   - We can figure out a way to link them (Gen-AI maybe, as manual would be too labour intensive)
   - Otherwise we should not include them in a search results page
 - Focus more on displaying the indicators and its data
   - Include historical data for indicators
   - Show the associated data for the indicator more prominently
