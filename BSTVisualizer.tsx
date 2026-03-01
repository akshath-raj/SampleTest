import { useState, useCallback, FC, ReactNode } from "react";

// ── Types ─────────────────────────────────────────────────────────────────
interface BSTNode {
  v: number;
  left: BSTNode | null;
  right: BSTNode | null;
}

interface Position { x: number; y: number; node: BSTNode; }
type PositionMap = Record<string, Position>;

type HighlightState = {
  value: number | null;
  color: string | null;
};

type ToastState = {
  msg: string;
  ok: boolean;
} | null;

// ── BST Pure Functions ────────────────────────────────────────────────────
const makeNode = (v: number): BSTNode => ({ v, left: null, right: null });

const clone = (n: BSTNode | null): BSTNode | null =>
  n ? { ...n, left: clone(n.left), right: clone(n.right) } : null;

const insert = (root: BSTNode | null, v: number): BSTNode => {
  if (!root) return makeNode(v);
  if (v < root.v) return { ...root, left: insert(root.left, v) };
  if (v > root.v) return { ...root, right: insert(root.right, v) };
  return root;
};

const search = (root: BSTNode | null, v: number): boolean => {
  if (!root) return false;
  if (v === root.v) return true;
  return v < root.v ? search(root.left, v) : search(root.right, v);
};

const minNode = (n: BSTNode): BSTNode => (n.left ? minNode(n.left) : n);

const remove = (root: BSTNode | null, v: number): BSTNode | null => {
  if (!root) return null;
  if (v < root.v) return { ...root, left: remove(root.left, v) };
  if (v > root.v) return { ...root, right: remove(root.right, v) };
  if (!root.left) return root.right;
  if (!root.right) return root.left;
  const s = minNode(root.right);
  return { ...root, v: s.v, right: remove(root.right, s.v) };
};

const height = (n: BSTNode | null): number =>
  n ? 1 + Math.max(height(n.left), height(n.right)) : 0;

const count = (n: BSTNode | null): number =>
  n ? 1 + count(n.left) + count(n.right) : 0;

const inorder   = (n: BSTNode | null, r: number[] = []): number[] =>
  n ? (inorder(n.left, r), r.push(n.v), inorder(n.right, r), r) : r;

const preorder  = (n: BSTNode | null, r: number[] = []): number[] =>
  n ? (r.push(n.v), preorder(n.left, r), preorder(n.right, r), r) : r;

const postorder = (n: BSTNode | null, r: number[] = []): number[] =>
  n ? (postorder(n.left, r), postorder(n.right, r), r.push(n.v), r) : r;

const layout = (
  node: BSTNode | null, depth: number,
  left: number, right: number,
  acc: PositionMap = {}
): PositionMap => {
  if (!node) return acc;
  acc[node.v] = { x: (left + right) / 2, y: depth * 80 + 50, node };
  layout(node.left,  depth + 1, left, (left + right) / 2, acc);
  layout(node.right, depth + 1, (left + right) / 2, right, acc);
  return acc;
};

// ── Sub-Components ────────────────────────────────────────────────────────
const R = 22;
const SVG_W = 900;

const Edge: FC<{ x1:number; y1:number; x2:number; y2:number }> = ({ x1,y1,x2,y2 }) => {
  const dx=x2-x1, dy=y2-y1, len=Math.sqrt(dx*dx+dy*dy);
  return len ? <line x1={x1+dx/len*R} y1={y1+dy/len*R} x2={x2-dx/len*R} y2={y2-dy/len*R}
    stroke="#3b3b5c" strokeWidth={1.5}/> : null;
};

const NodeCircle: FC<{ x:number; y:number; value:number; hl:HighlightState }> = ({ x,y,value,hl }) => {
  const active = hl.value === value;
  return (
    <g>
      <circle cx={x} cy={y} r={R}
        fill={active ? (hl.color ?? '#7c3aed') : '#1e1e2e'}
        stroke={active ? (hl.color ?? '#7c3aed') : '#3b3b5c'} strokeWidth={2} />
      <text x={x} y={y+1} textAnchor="middle" dominantBaseline="middle"
        fill="#e4e4f0" fontSize={12} fontFamily="Space Mono,monospace" fontWeight={700}>
        {value}
      </text>
    </g>
  );
};

const TreeCanvas: FC<{ root: BSTNode | null; hl: HighlightState }> = ({ root, hl }) => {
  const h = Math.max(420, height(root) * 80 + 80);
  const pos = layout(root, 0, 0, SVG_W);
  return (
    <svg width={SVG_W} height={h}>
      {Object.entries(pos).flatMap(([v, { x, y, node }]) => [
        node.left  && pos[node.left.v]  && <Edge key={`l${v}`} x1={x} y1={y} x2={pos[node.left.v].x}  y2={pos[node.left.v].y}  />,
        node.right && pos[node.right.v] && <Edge key={`r${v}`} x1={x} y1={y} x2={pos[node.right.v].x} y2={pos[node.right.v].y} />,
      ])}
      {Object.entries(pos).map(([v, { x, y }]) =>
        <NodeCircle key={v} x={x} y={y} value={parseInt(v)} hl={hl} />
      )}
    </svg>
  );
};

const Stat: FC<{ label: string; value: ReactNode }> = ({ label, value }) => (
  <span style={{ fontSize:12, color:'#6b6b8a' }}>{label}: <b style={{ color:'#e4e4f0' }}>{value}</b></span>
);

// ── Main App ──────────────────────────────────────────────────────────────
export default function App() {
  const [root, setRoot]   = useState<BSTNode | null>(null);
  const [input, setInput] = useState<string>('');
  const [hl, setHl]       = useState<HighlightState>({ value: null, color: null });
  const [toast, setToast] = useState<ToastState>(null);

  const showToast = (msg: string, ok: boolean) => {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 2000);
  };

  const flash = (v: number, color: string, ms = 1200) => {
    setHl({ value: v, color });
    setTimeout(() => setHl({ value: null, color: null }), ms);
  };

  const getValue = (): number | null => {
    const v = parseInt(input);
    if (isNaN(v)) { showToast('Enter a number', false); return null; }
    return v;
  };

  const handleInsert = () => {
    const v = getValue(); if (v === null) return;
    setRoot(r => clone(insert(r, v)));
    flash(v, '#7c3aed'); showToast(`Inserted ${v}`, true); setInput('');
  };

  const handleSearch = () => {
    const v = getValue(); if (v === null) return;
    const found = search(root, v);
    flash(v, found ? '#22c55e' : '#ef4444', 1400);
    showToast(found ? `Found ${v}!` : `${v} not found`, found);
  };

  const handleDelete = () => {
    const v = getValue(); if (v === null) return;
    if (!search(root, v)) { showToast(`${v} not in tree`, false); return; }
    flash(v, '#ef4444', 600);
    setTimeout(() => setRoot(r => clone(remove(r, v))), 600);
    showToast(`Deleted ${v}`, true); setInput('');
  };

  const loadDemo = () => {
    let r: BSTNode | null = null;
    [50,30,70,20,40,60,80,10,25,35,45].forEach(v => r = insert(r, v));
    setRoot(r); showToast('Demo tree loaded!', true);
  };

  const Btn: FC<{ label:string; onClick:()=>void; primary?:boolean; danger?:boolean }> = ({ label,onClick,primary,danger }) => (
    <button onClick={onClick} style={{
      fontFamily:"'Space Mono',monospace", fontWeight:700, fontSize:13,
      padding:'8px 16px', borderRadius:6, cursor:'pointer', transition:'all .15s',
      background: primary ? '#7c3aed' : danger ? 'transparent' : 'transparent',
      color:      primary ? '#fff'    : danger ? '#ef4444'    : '#6b6b8a',
      border:     primary ? 'none'    : danger ? '1px solid #ef4444' : '1px solid #1e1e2e',
    }}>{label}</button>
  );

  return (
    <div style={{ background:'#0a0a0f', color:'#e4e4f0', minHeight:'100vh', fontFamily:"'Space Mono',monospace", display:'flex', flexDirection:'column' }}>
      <header style={{ padding:'1.2rem 2rem', borderBottom:'1px solid #1e1e2e', display:'flex', alignItems:'center', gap:16 }}>
        <h1 style={{ fontFamily:'Syne,sans-serif', fontSize:24, fontWeight:800, margin:0, background:'linear-gradient(135deg,#7c3aed,#06b6d4)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}>BST Visualizer</h1>
        <span style={{ color:'#6b6b8a', fontSize:12 }}>TypeScript React · Binary Search Tree</span>
      </header>

      <div style={{ display:'flex', gap:8, padding:'12px 2rem', borderBottom:'1px solid #1e1e2e', flexWrap:'wrap', alignItems:'center' }}>
        <input value={input} type="number" placeholder="value…"
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleInsert()}
          style={{ background:'#111118', border:'1px solid #1e1e2e', borderRadius:6, color:'#e4e4f0', fontFamily:"'Space Mono',monospace", fontSize:13, padding:'8px 12px', width:100, outline:'none' }} />
        <Btn label="Insert"  onClick={handleInsert}                primary />
        <button onClick={handleSearch} style={{ fontFamily:"'Space Mono',monospace", fontWeight:700, fontSize:13, padding:'8px 16px', borderRadius:6, cursor:'pointer', background:'#06b6d4', color:'#000', border:'none' }}>Search</button>
        <Btn label="Delete"  onClick={handleDelete}                danger />
        <Btn label="Reset"   onClick={() => { setRoot(null); showToast('Cleared', true); }} />
        <Btn label="Demo"    onClick={loadDemo} />
      </div>

      <div style={{ flex:1, overflow:'auto', padding:'1rem 2rem' }}>
        {root
          ? <TreeCanvas root={root} hl={hl} />
          : <p style={{ color:'#6b6b8a', marginTop:80, textAlign:'center' }}>Tree is empty — insert values or load a demo.</p>}
      </div>

      <div style={{ display:'flex', gap:32, padding:'12px 2rem', borderTop:'1px solid #1e1e2e', flexWrap:'wrap' }}>
        {[['Inorder',inorder(root)],['Preorder',preorder(root)],['Postorder',postorder(root)]].map(([label,vals]) => (
          <div key={label as string} style={{ display:'flex', flexDirection:'column', gap:4 }}>
            <span style={{ color:'#6b6b8a', fontSize:11, textTransform:'uppercase', letterSpacing:'.05em' }}>{label}</span>
            <span style={{ color:'#06b6d4', fontSize:13 }}>{(vals as number[]).join(' → ') || '—'}</span>
          </div>
        ))}
      </div>

      <div style={{ display:'flex', gap:24, padding:'8px 2rem', borderTop:'1px solid #1e1e2e' }}>
        <Stat label="Nodes" value={count(root)} />
        <Stat label="Height" value={height(root)} />
        <Stat label="Root" value={root ? root.v : '—'} />
      </div>

      {toast && (
        <div style={{
          position:'fixed', bottom:24, right:24, padding:'10px 18px', borderRadius:8,
          fontWeight:700, fontSize:13, boxShadow:'0 4px 20px rgba(0,0,0,.4)',
          background: toast.ok ? '#22c55e' : '#ef4444',
          color: toast.ok ? '#000' : '#fff',
        }}>{toast.msg}</div>
      )}
    </div>
  );
}
