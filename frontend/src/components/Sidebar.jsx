import { useState, useRef } from 'react';
import ScopeSection from './ScopeSection';
import SpecBuilder from './SpecBuilder';
import AdvancedScoring from './AdvancedScoring';
import SearchButton from './SearchButton';

const MIN_WIDTH = 280;
const MAX_WIDTH = 620;
const DEFAULT_WIDTH = 400;

export default function Sidebar({ state, dispatch, onSearch }) {
  const [width, setWidth] = useState(DEFAULT_WIDTH);
  const dragging = useRef(false);
  const startX = useRef(0);
  const startW = useRef(0);

  function handleMouseDown(e) {
    dragging.current = true;
    startX.current = e.clientX;
    startW.current = width;
    document.body.style.cursor = 'ew-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();

    function onMove(ev) {
      if (!dragging.current) return;
      const delta = ev.clientX - startX.current;
      setWidth(Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startW.current + delta)));
    }

    function onUp() {
      dragging.current = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  return (
    <div className="sidebar-wrapper" style={{ width }}>
      <aside className="sidebar">
        <ScopeSection state={state} dispatch={dispatch} />
        <SpecBuilder state={state} dispatch={dispatch} />
        <AdvancedScoring state={state} dispatch={dispatch} />
        <div style={{ flex: 1 }} />
        <SearchButton state={state} onSearch={onSearch} />
      </aside>
      <div className="sidebar-resize-handle" onMouseDown={handleMouseDown} title="Drag to resize" />
    </div>
  );
}
