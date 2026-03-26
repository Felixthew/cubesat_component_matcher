# Interacting with the API
First and foremost when developing check out the [API documentation](http://129.159.89.217:8000/docs).

And of course check out the [example website](http://129.159.89.217:8000) I will be talking about in
this doc.

This document will not focus much on technical details of the API. If you want that information
check out either the aforementioned API documentation or read the comprehensive backend README.

## Intended flow
### User builds search request using:
1. /options
2. /options/{solution}
3. /options/{solution}/{system}
4. /kwargs -- for type wide kwargs (can come before or after options, doesn't matter when)

These are all GET requests where the user is receiving information that will help them build their
search request.

### User sends search request for scoring
1. /search

This is a POST where a JSON representing the search request is attached and then the resulting
scored dataset is returned.

### User sends retrieve request
1. /search/{session_id}

This is a POST where a previous search request (specified by session_id) is retrieved from storage
and sorted, filtered, and modified according to the retrieve request attached as a JSON.

## Intended website design
This section is subjective, but it explains some of our design choices in the API and their intended
use. This section also gives design suggestions that we used in making the mock website.

In no way should you feel you have to make exact copies of these features, but they should serve as inspiration.

### Important details
These are the things I want to highlight:
#### In the configure specifications menu
* For strings there is a search dropdown that takes advantage of the col profile option to display all available 
options and provides an easy way to search them. Also note that "," resets teh dropdown in case you are submitted a comma seperated list for the contains_any kwarg.
* Lists have a multi-select dropdown that builds the string for you. You could also use the same search concept as used for strings.
* booleans have forced true/false dropdowns.
* Doesn't allow multiple entries for the same column.

#### In the kwargs menu (Configure scoring parameters)
* Hovering over a selected parameter displays the default value and description provided in the kwarg profile.
* Kwargs with option will have a dropdown selection. (example: list, match mode)
* Boolean kwargs have a true false dropdown
* Kwarg default value are autoselected

#### In the results
* Scores are highlighted
* Filter min or max can be omitted
* Scrollable table 

### More complete list
Here's a more complete list of all the features summarized by AI:
### Core Workflow Design

**Progressive Disclosure**: The interface uses a 4-step wizard approach where each step is revealed only after the previous is completed. This prevents user confusion and ensures proper data validation flow.

**State Management**: The application maintains hierarchical state resets - changing solution resets system and all subsequent steps, changing system resets specifications and results. This prevents invalid state combinations.

**Session Persistence**: Search results are cached server-side with session IDs, enabling result refinement without re-running expensive searches.

### API Integration Architecture

**Base Structure**: The website communicates with FastAPI endpoints using standard fetch requests with JSON payloads. CORS is handled server-side to enable cross-origin requests.

**Endpoint Usage**:
- `GET /options` → Loads solution schemas (filtered to exclude 'metadata' and 'pg_toast')
- `GET /options/{solution}` → Loads system tables for selected solution
- `GET /options/{solution}/{system}` → Loads parameter profiles including dtype and options
- `POST /search` → Performs initial component search with specifications
- `POST /search/{session_id}` → Retrieves filtered/sorted results using session persistence

**Error Handling**: Comprehensive try-catch blocks with user-friendly error messages displayed as dismissible banners. Network failures and API errors are caught and displayed contextually.

### Intelligent Input System

**Dynamic Parameter Detection**: The system automatically detects parameter data types from API responses and adapts input methods:

- **String parameters** → Standard text input with optional dropdown suggestions
- **Boolean parameters** (`dtype: "boolean"`) → Forced true/false dropdown to prevent invalid inputs
- **List parameters** (`dtype: "list"`) → Multi-select checkbox interface that builds comma-separated strings
- **Numeric parameters** → Number inputs with step validation

**Duplicate Prevention**: Smart dropdown filtering prevents users from selecting the same parameter multiple times in specifications or filters, eliminating common user errors.

**Auto-Complete with Alphabetical Sorting**: When parameters have predefined options, the interface provides sorted dropdown suggestions. String fields support both free-text entry and option selection, while list fields enforce multi-selection from available choices.

### Search and Result Management

**Specification Builder**: Users build searches by adding parameter-value-weight triplets. The interface validates completeness and converts values to appropriate types (string/number) before API submission.

**Advanced Result Controls**: Post-search, users can apply filters (min/max numeric ranges), sorting (any column, ascending/descending, with score coupling option), and pagination without losing their search session. Settings persist across filter applications but reset for new searches.

**Score Highlighting**: Result tables automatically identify and highlight score-related columns with bold green formatting for easy identification of key metrics.

### User Experience Optimizations

**Loading Indicators**: Contextual loading messages appear during API calls ("Loading systems...", "Loading parameters...") providing clear feedback during network requests.

**Responsive Data Display**: Results table implements horizontal scrolling for wide datasets while maintaining vertical page flow. Table container uses `overflow-x: auto` with `min-width` constraints.

**Form Validation**: Prevents submission of incomplete specifications and provides clear error messaging. Required fields are validated before API calls.

**Settings Preservation**: Filter, sort, and pagination preferences are preserved when refining results but reset cleanly for new searches, balancing continuity with fresh-start clarity.

### Technical Implementation Highlights

**Dynamic DOM Generation**: All form elements are created programmatically based on API responses, ensuring the interface adapts to any backend schema changes without code modifications.

**Event Delegation**: Uses targeted event listeners with proper cleanup to handle dynamic content without memory leaks.

**State Synchronization**: Dropdown options update reactively - selecting a parameter removes it from other specification dropdowns, maintaining data consistency.

**Type-Safe API Communication**: JavaScript objects are constructed to match Pydantic models exactly, ensuring reliable API communication with proper typing.

### Data Flow Architecture

**Cascading Updates**: Parameter selection triggers cascading updates through dependent dropdowns. Importantly, column selection updates the available cols and dtypes in kwargs. Boolean parameters automatically populate with true/false options, list parameters populate with multi-select checkboxes, ensuring type safety.

**Memory Management**: Uses efficient DOM manipulation with fragment-based updates and selective re-rendering. Old elements are properly removed to prevent memory leaks during dynamic updates.

**Session State Tracking**: Maintains current solution, system, available columns, and session ID in JavaScript variables. State is synchronized across all interface components for consistency.

### Advanced Functionality

**Multi-Select Implementation**: List parameters use checkbox-based selection with real-time comma-separated string building. Selected items are tracked in arrays and converted to API-compatible format automatically.

**Filter Persistence**: Applied filters remain visible and editable, allowing iterative refinement. New searches clear filters while result refinement preserves user selections.

**Intelligent Defaults**: Sort descending by default (highest scores first), 10 results per page, overall_score as default sort column. Score coupling defaults to false but preserves user preference.

**Schema Filtering**: System schemas like metadata and pg_toast are automatically filtered from user-visible options, keeping the interface clean and focused on relevant data.

The website successfully abstracts complex API interactions behind an intuitive interface while maintaining full access to advanced functionality through progressive disclosure and intelligent defaults.

## Notes for consideration & moving forward
- filter does NOTHING if non-numeric column is passed to it (can be swapped for a valueError)
- scores are returns unrounded
- Consider neglecting "notes" cols on prompt (startswith "notes"?)
- range accepts NUMBERS not ranges from user
- Consider auto applying filters and settings after initial search