import { useState, useRef, useEffect, useCallback } from "react";

// ── BST Engine ────────────────────────────────────────────────────────────
class BSTNode { constructor(v){ this.v=v; this.left=null; this.right=null; } }

function bstInsert(root, v) {
  if (!root) return new BSTNode(v);
  if (v < root.v) root.left  = bstInsert(root.left, v);
  else if (v > root.v) root.right = bstInsert(root.right, v);
  return root;
}

function bstSearch(root, v) {
  if (!root) return false;
  if (v === root.v) return true;
  return v < root.v ? bstSearch(root.left, v) : bstSearch(root.right, v);
}

function bstDelete(root, v) {
  if (!root) return null;
  if (v < root.v) { root.left = bstDelete(root.left, v); }
  else if (v > root.v) { root.right = bstDelete(root.right, v); }
  else {
    if (!root.left) return root.right;
    if (!root.right) return root.left;
    let s = root.right; while (s.left) s = s.left;
    root.v = s.v; root.right = bstDelete(root.right, s.v);
  }
  return root;
}

function cloneTree(n) {
  if (!n) return null;
  const c = new BSTNode(n.v);
  c.left = cloneTree(n.left); c.right = cloneTree(n.right);
  return c;
}

function treeHeight(n) { return n ? 1 + Math.max(treeHeight(n.left), treeHeight(n.right)) : 0; }
function treeCount(n)  { return n ? 1 + treeCount(n.left) + treeCount(n.right) : 0; }

function inorder(n, r=[])   { if(n){inorder(n.left,r); r.push(n.v); inorder(n.right,r);} return r; }
function preorder(n, r=[])  { if(n){r.push(n.v); preorder(n.left,r); preorder(n.right,r);} return r; }
function postorder(n, r=[]) { if(n){postorder(n.left,r); postorder(n.right,r); r.push(n.v);} return r; }

function layoutTree(node, depth, left, right, positions={}) {
  if (!node) return positions;
  const x = (left + right) / 2;
  const y = depth * 80 + 50;
  positions[node.v] = { x, y, node };
  layoutTree(node.left, depth+1, left, (left+right)/2, positions);
  layoutTree(node.right, depth+1, (left+right)/2, right, positions);
  return positions;
}

// ── Components ────────────────────────────────────────────────────────────
const R = 22;
const W = 900;

function TreeEdge({ x1, y1, x2, y2 }) {
  const dx=x2-x1, dy=y2-y1, len=Math.sqrt(dx*dx+dy*dy);
  if (!len) return null;
  return <line x1={x1+dx/len*R} y1={y1+dy/len*R} x2={x2-dx/len*R} y2={y2-dy/len*R}
    stroke="#3b3b5c" strokeWidth={1.5} />;
}

function TreeNode({ x, y, value, highlight, highlightColor }) {
  const fill   = highlight ? (highlightColor || '#7c3aed') : '#1e1e2e';
  const stroke = highlight ? (highlightColor || '#7c3aed') : '#3b3b5c';
  return (
    <g style={{ transition: 'all .3s' }}>
      <circle cx={x} cy={y} r={R} fill={fill} stroke={stroke} strokeWidth={2} />
      <text x={x} y={y+1} textAnchor="middle" dominantBaseline="middle"
        fill="#e4e4f0" fontSize={12} fontFamily="Space Mono, monospace" fontWeight={700}>
        {value}
      </text>
    </g>
  );
}

function TreeSVG({ root, highlight, highlightColor }) {
  const h = Math.max(420, treeHeight(root) * 80 + 80);
  const positions = layoutTree(root, 0, 0, W);
  const entries = Object.entries(positions);

  return (
    <svg width={W} height={h}>
      {entries.map(([v, { x, y, node }]) => [
        node.left  && positions[node.left.v]  && <TreeEdge key={`e-l-${v}`} x1={x} y1={y} x2={positions[node.left.v].x}  y2={positions[node.left.v].y}  />,
        node.right && positions[node.right.v] && <TreeEdge key={`e-r-${v}`} x1={x} y1={y} x2={positions[node.right.v].x} y2={positions[node.right.v].y} />,
      ])}
      {entries.map(([v, { x, y }]) => (
        <TreeNode key={v} x={x} y={y} value={v}
          highlight={parseInt(v) === highlight} highlightColor={highlightColor} />
      ))}
    </svg>
  );
}

function TraversalRow({ label, values }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:4 }}>
      <span style={{ color:'#6b6b8a', fontSize:11, textTransform:'uppercase', letterSpacing:'.05em' }}>{label}</span>
      <span style={{ color:'#06b6d4', fontSize:13 }}>{values.join(' → ') || '—'}</span>
    </div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────
export default function BSTVisualizer() {
  const [root, setRoot] = useState(null);
  const [input, setInput] = useState('');
  const [highlight, setHighlight] = useState(null);
  const [highlightColor, setHighlightColor] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (msg, ok) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2000);
  };

  const flash = (val, color, ms=1200) => {
    setHighlight(val); setHighlightColor(color);
    setTimeout(() => { setHighlight(null); setHighlightColor(null); }, ms);
  };

  const handleInsert = () => {
    const v = parseInt(input); if (isNaN(v)) { showToast('Enter a number', false); return; }
    setRoot(r => cloneTree(bstInsert(cloneTree(r), v)));
    flash(v, '#7c3aed'); showToast(`Inserted ${v}`, true); setInput('');
  };

  const handleSearch = () => {
    const v = parseInt(input); if (isNaN(v)) { showToast('Enter a number', false); return; }
    const found = bstSearch(root, v);
    flash(v, found ? '#22c55e' : '#ef4444', 1400);
    showToast(found ? `Found ${v}!` : `${v} not found`, found);
  };

  const handleDelete = () => {
    const v = parseInt(input); if (isNaN(v)) { showToast('Enter a number', false); return; }
    if (!bstSearch(root, v)) { showToast(`${v} not in tree`, false); return; }
    flash(v, '#ef4444', 600);
    setTimeout(() => setRoot(r => cloneTree(bstDelete(cloneTree(r), v))), 600);
    showToast(`Deleted ${v}`, true); setInput('');
  };

  const loadDemo = () => {
    let r = null;
    [50,30,70,20,40,60,80,10,25,35,45].forEach(v => r = bstInsert(r, v));
    setRoot(cloneTree(r)); showToast('Demo loaded!', true);
  };

  const s = { background:'#0a0a0f', color:'#e4e4f0', minHeight:'100vh', fontFamily:"'Space Mono', monospace", display:'flex', flexDirection:'column' };

  const btn = (label, onClick, style={}) => (
    <button onClick={onClick} style={{
      fontFamily:"'Space Mono',monospace", fontWeight:700, fontSize:13,
      padding:'8px 16px', borderRadius:6, border:'1px solid transparent',
      cursor:'pointer', transition:'all .15s', ...style
    }}>{label}</button>
  );

  return (
    <div style={s}>
      <header style={{ padding:'1.2rem 2rem', borderBottom:'1px solid #1e1e2e', display:'flex', alignItems:'center', gap:16 }}>
        <h1 style={{ fontFamily:"'Syne',sans-serif", fontSize:24, fontWeight:800, background:'linear-gradient(135deg,#7c3aed,#06b6d4)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>BST Visualizer</h1>
        <span style={{ color:'#6b6b8a', fontSize:12 }}>React · Insert · Search · Delete · Traverse</span>
      </header>

      <div style={{ display:'flex', gap:8, padding:'12px 2rem', borderBottom:'1px solid #1e1e2e', flexWrap:'wrap', alignItems:'center' }}>
        <input value={input} onChange={e=>setInput(e.target.value)}
          onKeyDown={e=>e.key==='Enter' && handleInsert()}
          type="number" placeholder="value…"
          style={{ background:'#111118', border:'1px solid #1e1e2e', borderRadius:6, color:'#e4e4f0', fontFamily:"'Space Mono',monospace", fontSize:13, padding:'8px 12px', width:100, outline:'none' }} />
        {btn('Insert',  handleInsert,  { background:'#7c3aed', color:'#fff', border:'none' })}
        {btn('Search',  handleSearch,  { background:'#06b6d4', color:'#000', border:'none' })}
        {btn('Delete',  handleDelete,  { background:'transparent', color:'#ef4444', borderColor:'#ef4444' })}
        {btn('Reset',   () => { setRoot(null); showToast('Cleared','ok'); }, { background:'transparent', color:'#6b6b8a', borderColor:'#1e1e2e' })}
        {btn('Demo',    loadDemo,      { background:'transparent', color:'#6b6b8a', borderColor:'#1e1e2e' })}
      </div>

      <div style={{ flex:1, overflow:'auto', padding:'1rem 2rem' }}>
        {root ? <TreeSVG root={root} highlight={highlight} highlightColor={highlightColor} />
               : <div style={{ color:'#6b6b8a', marginTop:80, textAlign:'center' }}>Tree is empty — insert values or load a demo.</div>}
      </div>

      <div style={{ display:'flex', gap:32, padding:'12px 2rem', borderTop:'1px solid #1e1e2e', flexWrap:'wrap' }}>
        <TraversalRow label="Inorder"   values={inorder(root)} />
        <TraversalRow label="Preorder"  values={preorder(root)} />
        <TraversalRow label="Postorder" values={postorder(root)} />
      </div>

      <div style={{ display:'flex', gap:24, padding:'8px 2rem', borderTop:'1px solid #1e1e2e', fontSize:12, color:'#6b6b8a' }}>
        {[['Nodes', treeCount(root)], ['Height', treeHeight(root)], ['Root', root ? root.v : '—']].map(([k,v]) => (
          <span key={k}>{k}: <b style={{ color:'#e4e4f0' }}>{v}</b></span>
        ))}
      </div>

      {toast && (
        <div style={{
          position:'fixed', bottom:24, right:24, padding:'10px 18px', borderRadius:8,
          fontWeight:700, fontSize:13,
          background: toast.ok ? '#22c55e' : '#ef4444',
          color: toast.ok ? '#000' : '#fff',
          boxShadow:'0 4px 20px rgba(0,0,0,.4)',
          transition:'opacity .3s'
        }}>{toast.msg}</div>
      )}
    </div>
  );
}
