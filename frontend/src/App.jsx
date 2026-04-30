import { useReducer, useEffect } from 'react';
import { reducer, initialState } from './reducer';
import * as api from './api';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import EmptyState from './components/EmptyState';
import ResultsView from './components/ResultsView';
import ErrorBanner from './components/ui/ErrorBanner';
import Toast from './components/ui/Toast';

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  useEffect(() => {
    dispatch({ type: 'SET_LOADING', key: 'loadingSolutions', value: true });
    api.getSolutions()
      .then(data => dispatch({ type: 'SET_SOLUTIONS', solutions: data.schemas.filter(s => !/^(metadata$|pg_toast|pg_)/.test(s)) }))
      .catch(() => { dispatch({ type: 'SET_LOADING', key: 'loadingSolutions', value: false }); dispatch({ type: 'ADD_ERROR', message: 'Failed to load solution types.' }); });
    api.getKwargs()
      .then(data => dispatch({ type: 'SET_ALL_KWARGS', kwargs: data }))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!state.solution) return;
    dispatch({ type: 'SET_LOADING', key: 'loadingSystems', value: true });
    api.getSystems(state.solution)
      .then(data => dispatch({ type: 'SET_SYSTEMS', systems: data.tables }))
      .catch(() => { dispatch({ type: 'SET_LOADING', key: 'loadingSystems', value: false }); dispatch({ type: 'ADD_ERROR', message: 'Failed to load systems.' }); });
  }, [state.solution]);

  useEffect(() => {
    if (!state.solution || !state.system) return;
    dispatch({ type: 'SET_LOADING', key: 'loadingColumns', value: true });
    api.getColumns(state.solution, state.system)
      .then(data => dispatch({ type: 'SET_COLUMNS', columns: data.columns }))
      .catch(() => { dispatch({ type: 'SET_LOADING', key: 'loadingColumns', value: false }); dispatch({ type: 'ADD_ERROR', message: 'Failed to load column profiles.' }); });
  }, [state.solution, state.system]);

  function buildSearchRequest(s) {
    const colKwargs = {};
    const typeKwargs = {};
    for (const spec of s.specs) {
      if (spec.column && Object.keys(spec.colKwargs).length > 0) colKwargs[spec.column] = spec.colKwargs;
    }
    for (const [type, kwargs] of Object.entries(s.globalTypeKwargs)) {
      if (Object.keys(kwargs).length > 0) typeKwargs[type] = kwargs;
    }
    const hasKwargs = Object.keys(colKwargs).length > 0 || Object.keys(typeKwargs).length > 0;
    return {
      location: { schema: s.solution, table: s.system },
      specs: s.specs.map(spec => ({ name: spec.column, value: spec.value, weight: spec.weight })),
      ...(hasKwargs ? { kwargs: { col_kwargs: colKwargs, type_kwargs: typeKwargs } } : {}),
    };
  }

  function buildRetrieveRequest(s, overrides = {}) {
    const sort = overrides.sort ?? s.sort;
    const filters = overrides.filters ?? s.filters;
    const pagination = overrides.pagination ? { ...s.pagination, ...overrides.pagination } : s.pagination;
    return {
      filters: filters.filter(f => f.name).map(({ name, min_val, max_val }) => ({ name, min_val, max_val })),
      sort: { by: sort.by, asc: sort.asc, score_coupling: true },
      pagination: { page: pagination.page, per_page: pagination.perPage },
    };
  }

  async function handleSearch() {
    dispatch({ type: 'SET_LOADING', key: 'searching', value: true });
    const searchReq = buildSearchRequest(state);
    try {
      const searchRes = await api.search(searchReq);
      const totalResults = searchRes.values.length;
      const sessionId = searchRes.session_id;

      const defaultSort = initialState.sort;
      const retrieveReq = buildRetrieveRequest(
        { sort: defaultSort, filters: [], pagination: { page: 1, perPage: state.pagination.perPage } },
        {}
      );
      const pageRes = await api.retrieve(sessionId, retrieveReq);

      // Derive column order from the actual returned row keys — the backend applies
      // score-coupling column reordering in the retrieve step, but always returns
      // the original `order` field. Reading from the first row's key order gives us
      // the correct score-coupled sequence.
      const columnOrder = pageRes.values.length > 0
        ? Object.keys(pageRes.values[0])
        : searchRes.order;

      dispatch({
        type: 'SET_RESULTS',
        sessionId,
        totalResults,
        results: pageRes.values,
        columnOrder,
        searchRequest: searchReq,
        searchedSpecs: state.specs.filter(s => s.column),
        resetSort: true,
        resetFilters: true,
        resetPagination: true,
      });
    } catch (err) {
      dispatch({ type: 'SET_LOADING', key: 'searching', value: false });
      let msg;
      if (!err.status) {
        msg = 'Failed to connect — check your network and try again.';
      } else if (err.status === 404) {
        msg = 'The requested data was not found. Try selecting a different system.';
      } else if (err.status === 500) {
        msg = 'Server error — try again in a moment.';
      } else {
        msg = err.detail || err.message || 'Search failed. Please try again.';
      }
      dispatch({ type: 'ADD_ERROR', message: msg });
    }
  }

  async function handleApply(overrides = {}) {
    if (!state.sessionId) return;
    dispatch({ type: 'SET_LOADING', key: 'applying', value: true });
    const retrieveReq = buildRetrieveRequest(state, overrides);
    try {
      const res = await api.retrieve(state.sessionId, retrieveReq);
      // Same score-coupling fix: use row key order, not the response's `order` field
      const columnOrder = res.values.length > 0
        ? Object.keys(res.values[0])
        : state.columnOrder;
      dispatch({
        type: 'SET_RESULTS',
        sessionId: state.sessionId,
        totalResults: state.totalResults,
        results: res.values,
        columnOrder,
        resetSort: false,
        resetFilters: false,
        resetPagination: false,
      });
    } catch (err) {
      if (err.status === 404) {
        dispatch({ type: 'SET_LOADING', key: 'applying', value: false });
        dispatch({ type: 'SET_TOAST', message: 'Session expired — results refreshed.' });
        setTimeout(() => dispatch({ type: 'CLEAR_TOAST' }), 4000);
        await handleSearch();
      } else {
        dispatch({ type: 'SET_LOADING', key: 'applying', value: false });
        dispatch({ type: 'ADD_ERROR', message: `Failed to apply: ${err.detail || err.message}` });
      }
    }
  }

  const hasResults = state.totalResults !== null;

  return (
    <div className="app">
      <Header />
      <div className="app-body">
        <Sidebar state={state} dispatch={dispatch} onSearch={handleSearch} />
        <main className="main">
          {state.errors.map(e => (
            <ErrorBanner key={e.id} message={e.message} onDismiss={() => dispatch({ type: 'DISMISS_ERROR', id: e.id })} autoId={e.id} />
          ))}
          {hasResults
            ? <ResultsView state={state} dispatch={dispatch} onApply={handleApply} />
            : <EmptyState />
          }
        </main>
      </div>
      {state.toast && <Toast message={state.toast} />}
    </div>
  );
}
