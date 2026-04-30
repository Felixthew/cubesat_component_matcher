export const initialState = {
  solutions: [],
  systems: [],
  columns: [],
  allKwargs: {},

  solution: null,
  system: null,
  specs: [],
  globalTypeKwargs: {},

  sessionId: null,
  totalResults: null,
  currentResults: [],
  columnOrder: [],
  lastSearchRequest: null,
  searchedSpecs: null,

  sort: { by: 'overall_score', asc: false },
  filters: [],
  pagination: { page: 1, perPage: 10 },
  showFilters: false,
  showNotes: false,

  loadingSolutions: false,
  loadingSystems: false,
  loadingColumns: false,
  searching: false,
  applying: false,

  errors: [],
  toast: null,
};

let specIdCounter = 0;
export const newSpec = () => ({
  id: ++specIdCounter,
  column: null,
  value: '',
  weight: 1.0,
  colKwargs: {},
  advancedOpen: false,
});

export function reducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, [action.key]: action.value };

    case 'SET_SOLUTIONS':
      return { ...state, solutions: action.solutions, loadingSolutions: false };

    case 'SET_SYSTEMS':
      return { ...state, systems: action.systems, loadingSystems: false };

    case 'SET_COLUMNS':
      return { ...state, columns: action.columns, loadingColumns: false };

    case 'SET_ALL_KWARGS':
      return { ...state, allKwargs: action.kwargs };

    case 'SET_SOLUTION':
      return {
        ...state,
        solution: action.solution,
        system: null, systems: [], columns: [],
        specs: [], globalTypeKwargs: {},
        sessionId: null, totalResults: null, currentResults: [], columnOrder: [],
        sort: initialState.sort, filters: [], pagination: initialState.pagination,
        lastSearchRequest: null, searchedSpecs: null,
      };

    case 'SET_SYSTEM':
      return {
        ...state,
        system: action.system,
        columns: [], specs: [], globalTypeKwargs: {},
        sessionId: null, totalResults: null, currentResults: [], columnOrder: [],
        sort: initialState.sort, filters: [], pagination: initialState.pagination,
        lastSearchRequest: null, searchedSpecs: null,
      };

    case 'ADD_SPEC':
      return { ...state, specs: [...state.specs, newSpec()] };

    case 'UPDATE_SPEC': {
      const specs = state.specs.map(s => s.id === action.id ? { ...s, ...action.patch } : s);
      return { ...state, specs };
    }

    case 'REMOVE_SPEC':
      return { ...state, specs: state.specs.filter(s => s.id !== action.id) };

    case 'SET_GLOBAL_KWARG': {
      const type = action.kwargType;
      const prev = state.globalTypeKwargs[type] || {};
      return {
        ...state,
        globalTypeKwargs: {
          ...state.globalTypeKwargs,
          [type]: { ...prev, [action.name]: action.value },
        },
      };
    }

    case 'SET_RESULTS':
      return {
        ...state,
        sessionId: action.sessionId,
        totalResults: action.totalResults,
        currentResults: action.results,
        columnOrder: action.columnOrder,
        lastSearchRequest: action.searchRequest ?? state.lastSearchRequest,
        searchedSpecs: action.searchedSpecs ?? state.searchedSpecs,
        searching: false,
        applying: false,
        sort: action.resetSort ? initialState.sort : state.sort,
        filters: action.resetFilters ? [] : state.filters,
        pagination: action.resetPagination
          ? { page: 1, perPage: state.pagination.perPage }
          : state.pagination,
      };

    case 'SET_SORT':
      return { ...state, sort: { ...state.sort, ...action.patch } };

    case 'SET_FILTERS':
      return { ...state, filters: action.filters };

    case 'ADD_FILTER':
      return { ...state, filters: [...state.filters, { id: Date.now(), name: '', min_val: null, max_val: null }] };

    case 'UPDATE_FILTER': {
      const filters = state.filters.map(f => f.id === action.id ? { ...f, ...action.patch } : f);
      return { ...state, filters };
    }

    case 'REMOVE_FILTER':
      return { ...state, filters: state.filters.filter(f => f.id !== action.id) };

    case 'CLEAR_FILTERS':
      return { ...state, filters: [] };

    case 'SET_PAGINATION':
      return { ...state, pagination: { ...state.pagination, ...action.patch } };

    case 'TOGGLE_FILTERS':
      return { ...state, showFilters: !state.showFilters };

    case 'TOGGLE_NOTES':
      return { ...state, showNotes: !state.showNotes };

    case 'ADD_ERROR':
      return { ...state, errors: [...state.errors, { id: Date.now(), message: action.message }] };

    case 'DISMISS_ERROR':
      return { ...state, errors: state.errors.filter(e => e.id !== action.id) };

    case 'SET_TOAST':
      return { ...state, toast: action.message };

    case 'CLEAR_TOAST':
      return { ...state, toast: null };

    default:
      return state;
  }
}
