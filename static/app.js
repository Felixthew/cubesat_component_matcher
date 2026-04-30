const API_BASE = '';

let currentSolution = '';
let currentSystem = '';
let availableColumns = [];
let currentSessionId = '';
let allResultColumns = [];
let availableDataTypes = new Set();
let globalKwargProfiles = {};

async function init() {
    await loadSolutions();
    await loadGlobalKwargProfiles();
}

async function loadSolutions() {
    try {
        const response = await fetch(`${API_BASE}/options`);
        const data = await response.json();

        const select = document.getElementById('solutionSelect');
        select.innerHTML = '<option value="">Select a solution...</option>';

        data.schemas.forEach(schema => {
            if (schema !== 'metadata' && schema !== 'pg_toast') {
                const option = document.createElement('option');
                option.value = schema;
                option.textContent = schema;
                select.appendChild(option);
            }
        });
    } catch (error) {
        showError('Failed to load solutions: ' + error.message);
    }
}

async function loadGlobalKwargProfiles() {
    try {
        const response = await fetch(`${API_BASE}/kwargs`);
        const data = await response.json();
        globalKwargProfiles = data;
    } catch (error) {
        console.warn('Failed to load global kwargs profiles:', error.message);
        globalKwargProfiles = {};
    }
}

async function loadSystems(solution) {
    try {
        resetSystemAndBelow();

        document.getElementById('systemSection').classList.remove('hidden');
        document.getElementById('systemLoadingIndicator').classList.add('show');

        const response = await fetch(`${API_BASE}/options/${solution}`);
        const data = await response.json();

        const select = document.getElementById('systemSelect');
        select.innerHTML = '<option value="">Select a system...</option>';

        data.tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.textContent = table;
            select.appendChild(option);
        });

        document.getElementById('systemLoadingIndicator').classList.remove('show');

    } catch (error) {
        document.getElementById('systemLoadingIndicator').classList.remove('show');
        showError('Failed to load systems: ' + error.message);
    }
}

function resetSystemAndBelow() {
    document.getElementById('systemSelect').innerHTML = '<option value="">Select a system...</option>';
    document.getElementById('specsSection').classList.add('hidden');
    resetResultsAndBelow();
    currentSystem = '';
    availableColumns = [];
    availableDataTypes.clear();
}

async function loadParameters(solution, system) {
    try {
        resetResultsAndBelow();

        document.getElementById('specsSection').classList.remove('hidden');
        document.getElementById('specsLoadingIndicator').classList.add('show');

        const response = await fetch(`${API_BASE}/options/${solution}/${system}`);
        const data = await response.json();

        availableColumns = data.columns;

        availableDataTypes.clear();
        data.columns.forEach(col => availableDataTypes.add(col.dtype));

        setupSpecsSection();

        document.getElementById('specsLoadingIndicator').classList.remove('show');

    } catch (error) {
        document.getElementById('specsLoadingIndicator').classList.remove('show');
        showError('Failed to load parameters: ' + error.message);
    }
}

function resetResultsAndBelow() {
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('resultControls').classList.add('hidden');
    const emptyState = document.getElementById('emptyState');
    if (emptyState) emptyState.classList.remove('hidden');
    currentSessionId = '';
    allResultColumns = [];
}

function setupSpecsSection() {
    resetResultsAndBelow();
    const container = document.getElementById('specsContainer');
    container.innerHTML = '';
    addSpecificationRow();
}

// ─── Spec Cards ──────────────────────────────────────────────────────────────

function addSpecificationRow() {
    const container = document.getElementById('specsContainer');
    const specCard = document.createElement('div');
    specCard.className = 'spec-card';

    const usedParams = Array.from(container.querySelectorAll('.spec-card .param-select'))
        .map(select => select.value)
        .filter(val => val);

    // Header: param select + weight + remove
    const cardHeader = document.createElement('div');
    cardHeader.className = 'spec-card-header';

    const paramSelect = document.createElement('select');
    paramSelect.className = 'param-select';
    paramSelect.innerHTML = '<option value="">Select parameter...</option>';
    availableColumns.forEach(col => {
        if (!usedParams.includes(col.name)) {
            const option = document.createElement('option');
            option.value = col.name;
            option.textContent = `${col.name} (${col.dtype})`;
            paramSelect.appendChild(option);
        }
    });

    const weightInput = document.createElement('input');
    weightInput.type = 'number';
    weightInput.className = 'weight-input';
    weightInput.placeholder = 'Wt';
    weightInput.value = '1';
    weightInput.step = '0.1';
    weightInput.min = '0.1';
    weightInput.title = 'Weight (relative importance)';

    const removeBtn = document.createElement('button');
    removeBtn.textContent = '×';
    removeBtn.className = 'remove-btn';
    removeBtn.onclick = () => specCard.remove();

    cardHeader.appendChild(paramSelect);
    cardHeader.appendChild(weightInput);
    cardHeader.appendChild(removeBtn);

    // Value container (dropdown overlay logic)
    const valueContainer = document.createElement('div');
    valueContainer.className = 'spec-value-container';

    const valueInput = document.createElement('input');
    valueInput.type = 'text';
    valueInput.placeholder = 'Value';
    valueInput.className = 'spec-search-input';
    valueInput.readOnly = true;

    const multiSelectDiv = document.createElement('div');
    multiSelectDiv.className = 'spec-multi-select';

    const selectedItemsDiv = document.createElement('div');
    selectedItemsDiv.className = 'spec-selected-items';

    valueContainer.appendChild(valueInput);
    valueContainer.appendChild(selectedItemsDiv);
    valueContainer.appendChild(multiSelectDiv);

    let currentOptions = [];
    let selectedValues = [];
    let isMultiSelect = false;

    // Inline scoring section
    const scoringDetails = document.createElement('details');
    scoringDetails.className = 'spec-scoring hidden';

    const scoringSummary = document.createElement('summary');
    scoringSummary.textContent = 'Matching options';

    const scoringInner = document.createElement('div');
    scoringInner.className = 'spec-scoring-inner';

    scoringDetails.appendChild(scoringSummary);
    scoringDetails.appendChild(scoringInner);

    // Parameter change handler
    paramSelect.addEventListener('change', function() {
        const selectedParam = availableColumns.find(col => col.name === this.value);
        currentOptions = selectedParam?.options || [];
        selectedValues = [];

        if (selectedParam && selectedParam.dtype === 'boolean') {
            isMultiSelect = false;
            currentOptions = ['true', 'false'];
            valueInput.placeholder = 'Click to select true/false';
            valueInput.readOnly = true;
        } else if (selectedParam && selectedParam.dtype === 'list' && currentOptions.length > 0) {
            isMultiSelect = true;
            valueInput.placeholder = 'Click to select options';
            valueInput.readOnly = true;
        } else if (currentOptions.length > 0) {
            isMultiSelect = false;
            valueInput.placeholder = 'Value (click to see options)';
            valueInput.readOnly = false;
        } else {
            isMultiSelect = false;
            valueInput.placeholder = 'Value';
            valueInput.readOnly = false;
        }

        valueInput.value = '';
        multiSelectDiv.style.display = 'none';
        selectedItemsDiv.innerHTML = '';

        // Populate inline scoring
        if (this.value && selectedParam) {
            scoringDetails.classList.remove('hidden');
            scoringInner.innerHTML = '';
            addInlineScoringSection(scoringInner, selectedParam.name, selectedParam.dtype, selectedParam);
        } else {
            scoringDetails.classList.add('hidden');
            scoringInner.innerHTML = '';
        }

        updateParameterDropdowns();
    });

    valueInput.addEventListener('click', function() {
        const selectedParam = availableColumns.find(col => col.name === paramSelect.value);

        if (selectedParam && selectedParam.dtype === 'boolean') {
            showBooleanSelect();
        } else if (isMultiSelect && currentOptions.length > 0) {
            showMultiSelect();
        } else if (!isMultiSelect && currentOptions.length > 0) {
            showSingleSelect();
        }
    });

    valueInput.addEventListener('input', function() {
        if (!isMultiSelect && currentOptions.length > 0) {
            const fullValue = this.value;
            const lastCommaIndex = fullValue.lastIndexOf(',');
            let searchTerm = fullValue;
            let prefix = '';

            if (lastCommaIndex !== -1) {
                prefix = fullValue.substring(0, lastCommaIndex + 1).trim() + ' ';
                searchTerm = fullValue.substring(lastCommaIndex + 1).trim();
            }

            showSingleSelect(searchTerm, prefix);
        }
    });

    function showSingleSelect(query = '', prefix = '') {
        multiSelectDiv.innerHTML = '';

        if (currentOptions.length === 0) {
            multiSelectDiv.style.display = 'none';
            return;
        }

        const filteredOptions = query === ''
            ? currentOptions
            : currentOptions.filter(option =>
                option.toString().toLowerCase().includes(query.toLowerCase())
            );

        if (filteredOptions.length === 0) {
            multiSelectDiv.style.display = 'none';
            return;
        }

        const sortedOptions = filteredOptions.sort((a, b) => a.toString().localeCompare(b.toString()));

        sortedOptions.forEach(option => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'spec-multi-option';
            optionDiv.style.justifyContent = 'flex-start';

            const label = document.createElement('span');
            label.textContent = option;
            label.style.cursor = 'pointer';
            optionDiv.appendChild(label);

            optionDiv.addEventListener('click', function() {
                valueInput.value = prefix ? prefix + option : option;
                multiSelectDiv.style.display = 'none';
            });

            multiSelectDiv.appendChild(optionDiv);
        });

        multiSelectDiv.style.display = 'block';
    }

    function showBooleanSelect() {
        multiSelectDiv.innerHTML = '';

        ['false', 'true'].forEach(option => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'spec-multi-option';
            optionDiv.style.justifyContent = 'flex-start';

            const label = document.createElement('span');
            label.textContent = option;
            label.style.cursor = 'pointer';
            optionDiv.appendChild(label);

            optionDiv.addEventListener('click', function() {
                valueInput.value = option;
                multiSelectDiv.style.display = 'none';
            });

            multiSelectDiv.appendChild(optionDiv);
        });

        multiSelectDiv.style.display = 'block';
    }

    function showMultiSelect() {
        multiSelectDiv.innerHTML = '';

        const sortedOptions = [...currentOptions].sort((a, b) => a.toString().localeCompare(b.toString()));

        sortedOptions.forEach(option => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'spec-multi-option';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = selectedValues.includes(option);

            const label = document.createElement('span');
            label.textContent = option;

            optionDiv.appendChild(checkbox);
            optionDiv.appendChild(label);

            optionDiv.addEventListener('click', function(e) {
                if (e.target.type !== 'checkbox') checkbox.checked = !checkbox.checked;
                toggleOption(option, checkbox.checked);
            });

            checkbox.addEventListener('change', function() {
                toggleOption(option, this.checked);
            });

            multiSelectDiv.appendChild(optionDiv);
        });

        multiSelectDiv.style.display = 'block';
    }

    function toggleOption(option, isSelected) {
        if (isSelected) {
            if (!selectedValues.includes(option)) selectedValues.push(option);
        } else {
            selectedValues = selectedValues.filter(val => val !== option);
        }
        if (isMultiSelect) valueInput.value = selectedValues.join(', ');
    }

    document.addEventListener('click', function(e) {
        if (!valueContainer.contains(e.target)) multiSelectDiv.style.display = 'none';
    });

    specCard.appendChild(cardHeader);
    specCard.appendChild(valueContainer);
    specCard.appendChild(scoringDetails);
    container.appendChild(specCard);
}

// ─── Inline Scoring ───────────────────────────────────────────────────────────

function addInlineScoringSection(scoringInner, colName, dtype, colData) {
    const allKwargs = [];
    const addedNames = new Set();

    // Column-specific kwargs take precedence
    if (colData && colData.kwargs && colData.kwargs.length > 0) {
        colData.kwargs.forEach(kp => {
            if (!addedNames.has(kp.name)) {
                allKwargs.push(kp);
                addedNames.add(kp.name);
            }
        });
    }

    // Then type-wide kwargs
    if (globalKwargProfiles[dtype]) {
        globalKwargProfiles[dtype].forEach(kp => {
            if (!addedNames.has(kp.name)) {
                allKwargs.push(kp);
                addedNames.add(kp.name);
            }
        });
    }

    if (allKwargs.length === 0) {
        const note = document.createElement('p');
        note.className = 'kwarg-no-options';
        note.textContent = 'No scoring options for this parameter type.';
        scoringInner.appendChild(note);
        return;
    }

    allKwargs.forEach(kp => {
        const row = document.createElement('div');
        row.className = 'kwarg-row';
        row.dataset.kwargName = kp.name;

        const labelEl = document.createElement('label');
        labelEl.className = 'kwarg-label';
        labelEl.textContent = kp.name.replace(/_/g, ' ');

        let input;
        const kpDtype = (kp.dtype || '').toLowerCase();

        if (kp.options && kp.options.length > 0) {
            input = document.createElement('select');
            input.className = 'kwarg-input';
            kp.options.forEach(opt => {
                const option = document.createElement('option');
                option.value = opt;
                option.textContent = opt;
                if (opt === kp.default || opt === String(kp.default)) option.selected = true;
                input.appendChild(option);
            });
        } else if (kpDtype === 'boolean') {
            input = document.createElement('select');
            input.className = 'kwarg-input';
            const trueOpt = document.createElement('option');
            trueOpt.value = 'true';
            trueOpt.textContent = 'true';
            if (kp.default === true) trueOpt.selected = true;
            const falseOpt = document.createElement('option');
            falseOpt.value = 'false';
            falseOpt.textContent = 'false';
            if (kp.default === false) falseOpt.selected = true;
            input.appendChild(trueOpt);
            input.appendChild(falseOpt);
        } else if (kpDtype === 'int' || kpDtype === 'integer') {
            input = document.createElement('input');
            input.type = 'number';
            input.step = '1';
            input.className = 'kwarg-input';
            if (kp.default !== undefined && kp.default !== null) input.value = kp.default;
        } else if (kpDtype === 'float' || kpDtype === 'number') {
            input = document.createElement('input');
            input.type = 'number';
            input.step = 'any';
            input.className = 'kwarg-input';
            if (kp.default !== undefined && kp.default !== null) input.value = kp.default;
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.className = 'kwarg-input';
            if (kp.default !== undefined && kp.default !== null) input.value = String(kp.default);
        }

        const descEl = document.createElement('span');
        descEl.className = 'kwarg-description';
        descEl.textContent = kp.description || '';

        row.appendChild(labelEl);
        row.appendChild(input);
        row.appendChild(descEl);
        scoringInner.appendChild(row);
    });
}

function parseKwargValue(input) {
    if (input.tagName === 'SELECT') {
        const value = input.value;
        if (value === 'true') return true;
        if (value === 'false') return false;
        return value || null;
    }
    if (input.type === 'number') {
        return input.value !== '' ? parseFloat(input.value) : null;
    }
    return input.value || null;
}

function collectInlineKwargs() {
    const col_kwargs = {};
    document.querySelectorAll('.spec-card').forEach(card => {
        const colName = card.querySelector('.param-select')?.value;
        if (!colName) return;
        const scoringInner = card.querySelector('.spec-scoring-inner');
        if (!scoringInner) return;
        const kwargValues = {};
        scoringInner.querySelectorAll('.kwarg-row').forEach(row => {
            const name = row.dataset.kwargName;
            if (!name) return;
            const input = row.querySelector('select, input');
            if (!input) return;
            const val = parseKwargValue(input);
            if (val !== null && val !== undefined && val !== '') {
                kwargValues[name] = val;
            }
        });
        if (Object.keys(kwargValues).length > 0) {
            col_kwargs[colName] = kwargValues;
        }
    });
    return col_kwargs;
}

// ─── Shared Helpers ───────────────────────────────────────────────────────────

function updateParameterDropdowns() {
    const container = document.getElementById('specsContainer');
    const allSelects = container.querySelectorAll('.spec-card .param-select');
    const usedParams = Array.from(allSelects).map(select => select.value).filter(val => val);

    allSelects.forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select parameter...</option>';

        availableColumns.forEach(col => {
            if (!usedParams.includes(col.name) || col.name === currentValue) {
                const option = document.createElement('option');
                option.value = col.name;
                option.textContent = `${col.name} (${col.dtype})`;
                if (col.name === currentValue) option.selected = true;
                select.appendChild(option);
            }
        });
    });
}

function getCurrentSelectedSpecs() {
    const specs = [];
    document.querySelectorAll('.spec-card').forEach(card => {
        const param = card.querySelector('.param-select')?.value;
        if (param) specs.push(param);
    });
    return specs;
}

// ─── Search ───────────────────────────────────────────────────────────────────

async function performSearch() {
    const specs = [];

    for (let card of document.querySelectorAll('.spec-card')) {
        const param = card.querySelector('.param-select')?.value;
        const value = card.querySelector('.spec-value-container input')?.value;
        const weightEl = card.querySelector('.weight-input');
        const weight = weightEl ? parseFloat(weightEl.value) : 1;

        if (param && value && weight) {
            const parsedValue = (!isNaN(value) && !isNaN(parseFloat(value)))
                ? parseFloat(value)
                : value;
            specs.push({ name: param, value: parsedValue, weight: weight });
        }
    }

    if (specs.length === 0) {
        showError('Please add at least one specification');
        return;
    }

    const col_kwargs = collectInlineKwargs();
    const hasKwargs = Object.keys(col_kwargs).length > 0;

    const searchRequest = {
        location: { schema: currentSolution, table: currentSystem },
        specs: specs,
        session_id: currentSessionId || null,
        kwargs: hasKwargs ? { col_kwargs, type_kwargs: {} } : null
    };

    try {
        document.getElementById('searchBtn').disabled = true;
        document.getElementById('searchBtn').textContent = 'Searching...';

        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(searchRequest)
        });

        const data = await response.json();
        currentSessionId = data.session_id;
        displayResults(data.values);

    } catch (error) {
        showError('Search failed: ' + error.message);
    } finally {
        document.getElementById('searchBtn').disabled = false;
        document.getElementById('searchBtn').textContent = 'Search Components';
    }
}

// ─── Results ──────────────────────────────────────────────────────────────────

function displayResults(results) {
    const container = document.getElementById('resultsContainer');

    if (!results || results.length === 0) {
        container.innerHTML = '<p class="no-results">No results found.</p>';
        document.getElementById('resultsSection').classList.remove('hidden');
        document.getElementById('resultControls').classList.remove('hidden');
        document.getElementById('emptyState').classList.add('hidden');
        return;
    }

    allResultColumns = Object.keys(results[0]);
    setupResultControls();

    const table = document.createElement('table');
    table.className = 'results-table';

    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    allResultColumns.forEach(key => {
        const th = document.createElement('th');
        th.className = 'sortable';
        if (key.toLowerCase().includes('score')) th.classList.add('score-cell');

        const label = document.createElement('span');
        label.textContent = key.replace(/_/g, ' ').toUpperCase();

        const arrow = document.createElement('span');
        arrow.className = 'sort-arrow';
        arrow.dataset.col = key;

        th.appendChild(label);
        th.appendChild(arrow);

        th.addEventListener('click', () => {
            const sortBySelect = document.getElementById('sortBySelect');
            const sortAscCheckbox = document.getElementById('sortAscCheckbox');
            const isSame = sortBySelect.value === key;
            sortBySelect.value = key;
            if (isSame) sortAscCheckbox.checked = !sortAscCheckbox.checked;
            updateSortArrows(key, sortAscCheckbox.checked);
            applyFilters();
        });

        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement('tbody');
    results.forEach(result => {
        const row = document.createElement('tr');
        allResultColumns.forEach(key => {
            const td = document.createElement('td');
            let value = result[key];

            const column = availableColumns.find(col => col.name === key);
            if (column && column.dtype === 'boolean') {
                if (value === 1 || value === '1' || value === true) value = 'true';
                else if (value === 0 || value === '0' || value === false) value = 'false';
            }

            const isScore = key.toLowerCase().includes('score');
            if (isScore) {
                td.className = 'score-cell';
                const numVal = parseFloat(value);
                td.textContent = !isNaN(numVal) ? numVal.toFixed(4) : (value !== null && value !== undefined ? value : 'N/A');
            } else {
                td.textContent = value !== null && value !== undefined ? value : 'N/A';
            }
            row.appendChild(td);
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    const tableContainer = document.createElement('div');
    tableContainer.className = 'results-table-container';
    tableContainer.appendChild(table);

    container.innerHTML = '';
    container.appendChild(tableContainer);

    document.getElementById('resultsSection').classList.remove('hidden');
    document.getElementById('resultControls').classList.remove('hidden');
    document.getElementById('emptyState').classList.add('hidden');

    // Update result count in toolbar
    const countEl = document.getElementById('resultCount');
    if (countEl) countEl.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;

    // Set initial sort arrow
    const currentSort = document.getElementById('sortBySelect').value;
    const currentAsc = document.getElementById('sortAscCheckbox').checked;
    if (currentSort) updateSortArrows(currentSort, currentAsc);
}

function updateSortArrows(activeCol, asc) {
    document.querySelectorAll('.results-table th .sort-arrow').forEach(arrow => {
        arrow.textContent = arrow.dataset.col === activeCol ? (asc ? ' ↑' : ' ↓') : '';
    });
}

function setupResultControls() {
    const currentSortBy = document.getElementById('sortBySelect').value;
    const currentSortAsc = document.getElementById('sortAscCheckbox').checked;
    const currentScoreCoupling = document.getElementById('scoreCouplingCheckbox').checked;
    const currentPage = document.getElementById('pageInput').value;
    const currentPerPage = document.getElementById('perPageSelect').value;

    const sortSelect = document.getElementById('sortBySelect');
    sortSelect.innerHTML = '';
    allResultColumns.forEach(col => {
        const option = document.createElement('option');
        option.value = col;
        option.textContent = col.replace(/_/g, ' ').toUpperCase();
        if (col === currentSortBy || (col === 'overall_score' && !currentSortBy)) option.selected = true;
        sortSelect.appendChild(option);
    });

    if (!document.getElementById('resultControls').classList.contains('hidden')) {
        // Preserve settings when refining results
        document.getElementById('sortAscCheckbox').checked = currentSortAsc;
        document.getElementById('scoreCouplingCheckbox').checked = currentScoreCoupling;
        document.getElementById('pageInput').value = currentPage;
        document.getElementById('perPageSelect').value = currentPerPage;
    } else {
        // Reset settings for new search
        document.getElementById('filtersContainer').innerHTML = '';
        document.getElementById('sortAscCheckbox').checked = false;
        document.getElementById('scoreCouplingCheckbox').checked = false;
        document.getElementById('pageInput').value = '1';
        document.getElementById('perPageSelect').value = '10';
        const filtersBar = document.getElementById('filtersBar');
        if (filtersBar) filtersBar.classList.add('hidden');
    }
}

// ─── Filters ──────────────────────────────────────────────────────────────────

function addFilterRow() {
    const container = document.getElementById('filtersContainer');
    const filterItem = document.createElement('div');
    filterItem.className = 'filter-item';

    const usedParams = Array.from(container.querySelectorAll('.filter-item select'))
        .map(select => select.value)
        .filter(val => val);

    const paramSelect = document.createElement('select');
    paramSelect.innerHTML = '<option value="">Select parameter...</option>';

    allResultColumns.forEach(col => {
        if (!usedParams.includes(col)) {
            const column = availableColumns.find(c => c.name === col);
            const isNumeric = (column && (
                column.dtype === 'number' ||
                column.dtype === 'float' ||
                column.dtype === 'int' ||
                column.dtype === 'integer'
            )) || col.toLowerCase().includes('score');

            if (isNumeric) {
                const option = document.createElement('option');
                option.value = col;
                option.textContent = col.replace(/_/g, ' ').toUpperCase();
                paramSelect.appendChild(option);
            }
        }
    });

    paramSelect.addEventListener('change', updateFilterDropdowns);

    const minInput = document.createElement('input');
    minInput.type = 'number';
    minInput.placeholder = 'Min value';

    const maxInput = document.createElement('input');
    maxInput.type = 'number';
    maxInput.placeholder = 'Max value';

    const removeBtn = document.createElement('button');
    removeBtn.textContent = '×';
    removeBtn.onclick = () => filterItem.remove();

    const controlRow = document.createElement('div');
    controlRow.className = 'filter-controls-row';
    controlRow.appendChild(minInput);
    controlRow.appendChild(maxInput);
    controlRow.appendChild(removeBtn);

    filterItem.appendChild(paramSelect);
    filterItem.appendChild(controlRow);
    container.appendChild(filterItem);
}

function updateFilterDropdowns() {
    const container = document.getElementById('filtersContainer');
    const allSelects = container.querySelectorAll('.filter-item select');
    const usedParams = Array.from(allSelects).map(select => select.value).filter(val => val);

    allSelects.forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select parameter...</option>';

        allResultColumns.forEach(col => {
            if (!usedParams.includes(col) || col === currentValue) {
                const column = availableColumns.find(c => c.name === col);
                const isNumeric = (column && (
                    column.dtype === 'number' ||
                    column.dtype === 'float' ||
                    column.dtype === 'int' ||
                    column.dtype === 'integer'
                )) || col.toLowerCase().includes('score');

                if (isNumeric) {
                    const option = document.createElement('option');
                    option.value = col;
                    option.textContent = col.replace(/_/g, ' ').toUpperCase();
                    if (col === currentValue) option.selected = true;
                    select.appendChild(option);
                }
            }
        });
    });
}

async function applyFilters() {
    if (!currentSessionId) {
        showError('No search session found. Please perform a search first.');
        return;
    }

    const filters = [];
    document.querySelectorAll('.filter-item').forEach(item => {
        const param = item.children[0].value;
        const controls = item.querySelector('.filter-controls-row');
        const minVal = controls.children[0].value;
        const maxVal = controls.children[1].value;

        if (param && (minVal || maxVal)) {
            const filter = { name: param };
            if (minVal) filter.min_val = parseFloat(minVal);
            if (maxVal) filter.max_val = parseFloat(maxVal);
            filters.push(filter);
        }
    });

    const retrieveRequest = {
        session_id: currentSessionId,
        filters: filters,
        sort: {
            by: document.getElementById('sortBySelect').value,
            asc: document.getElementById('sortAscCheckbox').checked,
            score_coupling: document.getElementById('scoreCouplingCheckbox').checked
        },
        pagination: {
            page: parseInt(document.getElementById('pageInput').value) || 1,
            per_page: parseInt(document.getElementById('perPageSelect').value) || 10
        }
    };

    try {
        document.getElementById('applyFiltersBtn').disabled = true;
        document.getElementById('applyFiltersBtn').textContent = 'Applying...';

        const response = await fetch(`${API_BASE}/search/${currentSessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(retrieveRequest)
        });

        const data = await response.json();
        displayResults(data.values);

    } catch (error) {
        showError('Failed to apply filters: ' + error.message);
    } finally {
        document.getElementById('applyFiltersBtn').disabled = false;
        document.getElementById('applyFiltersBtn').textContent = 'Apply';
    }
}

// ─── Notifications ────────────────────────────────────────────────────────────

function showError(message) {
    const existing = document.querySelector('.error');
    if (existing) existing.remove();

    const error = document.createElement('div');
    error.className = 'error';
    error.textContent = message;
    document.querySelector('.search-main').prepend(error);

    setTimeout(() => error.remove(), 5000);
}

function showSuccess(message) {
    const existing = document.querySelector('.success');
    if (existing) existing.remove();

    const success = document.createElement('div');
    success.className = 'success';
    success.textContent = message;
    document.querySelector('.search-main').prepend(success);

    setTimeout(() => success.remove(), 5000);
}

// ─── Event Listeners ──────────────────────────────────────────────────────────

document.getElementById('solutionSelect').addEventListener('change', function(e) {
    currentSolution = e.target.value;
    if (currentSolution) loadSystems(currentSolution);
    else resetSystemAndBelow();
});

document.getElementById('systemSelect').addEventListener('change', function(e) {
    currentSystem = e.target.value;
    if (currentSystem) loadParameters(currentSolution, currentSystem);
    else resetResultsAndBelow();
});

document.getElementById('addSpecBtn').addEventListener('click', addSpecificationRow);
document.getElementById('searchBtn').addEventListener('click', performSearch);

document.getElementById('addFilterBtn').addEventListener('click', () => {
    document.getElementById('filtersBar').classList.toggle('hidden');
});

document.getElementById('addFilterRowBtn').addEventListener('click', addFilterRow);
document.getElementById('applyFiltersBtn').addEventListener('click', applyFilters);

init();
