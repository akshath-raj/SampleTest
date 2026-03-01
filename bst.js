/**
 * Binary Search Tree — Pure JavaScript (ES Module)
 * Self-contained BST class with interactive CLI-style demo via console.
 * Operations: insert, search, delete, traversals, height, count, levelOrder
 */

// ── Node ──────────────────────────────────────────────────────────────────
class BSTNode {
  /** @param {number} value */
  constructor(value) {
    this.value = value;
    /** @type {BSTNode|null} */ this.left  = null;
    /** @type {BSTNode|null} */ this.right = null;
  }
}

// ── BST Class ─────────────────────────────────────────────────────────────
export class BST {
  constructor() {
    /** @type {BSTNode|null} */
    this.root = null;
  }

  // ── Insert ───────────────────────────────────────────────────────────
  /** @param {number} value */
  insert(value) {
    this.root = this.#insertRec(this.root, value);
    return this; // fluent API
  }

  /** @param {BSTNode|null} node @param {number} value @returns {BSTNode} */
  #insertRec(node, value) {
    if (!node) return new BSTNode(value);
    if (value < node.value)      node.left  = this.#insertRec(node.left,  value);
    else if (value > node.value) node.right = this.#insertRec(node.right, value);
    // duplicates are silently ignored
    return node;
  }

  // ── Search ───────────────────────────────────────────────────────────
  /** @param {number} value @returns {boolean} */
  search(value) {
    return this.#searchRec(this.root, value);
  }

  #searchRec(node, value) {
    if (!node) return false;
    if (value === node.value) return true;
    return value < node.value
      ? this.#searchRec(node.left,  value)
      : this.#searchRec(node.right, value);
  }

  // ── Delete ───────────────────────────────────────────────────────────
  /** @param {number} value */
  delete(value) {
    this.root = this.#deleteRec(this.root, value);
    return this;
  }

  #deleteRec(node, value) {
    if (!node) return null;
    if (value < node.value) {
      node.left  = this.#deleteRec(node.left,  value);
    } else if (value > node.value) {
      node.right = this.#deleteRec(node.right, value);
    } else {
      // Node found — three cases
      if (!node.left)  return node.right;
      if (!node.right) return node.left;
      // Two children: replace with inorder successor
      const successor = this.#minNode(node.right);
      node.value = successor.value;
      node.right = this.#deleteRec(node.right, successor.value);
    }
    return node;
  }

  #minNode(node) {
    let cur = node;
    while (cur.left) cur = cur.left;
    return cur;
  }

  // ── Height & Count ───────────────────────────────────────────────────
  height() { return this.#heightRec(this.root); }
  #heightRec(n) { return n ? 1 + Math.max(this.#heightRec(n.left), this.#heightRec(n.right)) : 0; }

  count() { return this.#countRec(this.root); }
  #countRec(n) { return n ? 1 + this.#countRec(n.left) + this.#countRec(n.right) : 0; }

  get isEmpty() { return this.root === null; }

  // ── Traversals ───────────────────────────────────────────────────────
  /** @returns {number[]} Values in ascending order */
  inorder() {
    const result = [];
    const walk = (n) => { if (!n) return; walk(n.left); result.push(n.value); walk(n.right); };
    walk(this.root);
    return result;
  }

  /** @returns {number[]} Root first */
  preorder() {
    const result = [];
    const walk = (n) => { if (!n) return; result.push(n.value); walk(n.left); walk(n.right); };
    walk(this.root);
    return result;
  }

  /** @returns {number[]} Root last */
  postorder() {
    const result = [];
    const walk = (n) => { if (!n) return; walk(n.left); walk(n.right); result.push(n.value); };
    walk(this.root);
    return result;
  }

  /** @returns {number[][]} Each sub-array is one level */
  levelOrder() {
    if (!this.root) return [];
    const result = [];
    const queue  = [this.root];
    while (queue.length) {
      const level = [];
      const size  = queue.length;
      for (let i = 0; i < size; i++) {
        const node = queue.shift();
        level.push(node.value);
        if (node.left)  queue.push(node.left);
        if (node.right) queue.push(node.right);
      }
      result.push(level);
    }
    return result;
  }

  // ── ASCII Print ──────────────────────────────────────────────────────
  /** Renders a sideways ASCII tree to console */
  print() {
    const lines = [];
    const walk = (n, prefix, isLeft) => {
      if (!n) return;
      walk(n.right, prefix + (isLeft ? '│   ' : '    '), false);
      lines.push(prefix + (isLeft ? '└── ' : '┌── ') + n.value);
      walk(n.left,  prefix + (isLeft ? '    ' : '│   '), true);
    };
    if (this.root) { walk(this.root.right, '', false); lines.push(String(this.root.value)); walk(this.root.left, '', true); }
    console.log(lines.join('\n'));
  }
}

// ── Demo (runs when executed directly with Node.js) ───────────────────────
const tree = new BST();
const values = [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45];

console.log('=== Binary Search Tree — JavaScript ===\n');
console.log('Inserting:', values.join(', '));
values.forEach(v => tree.insert(v));

console.log('\nASCII Tree:');
tree.print();

console.log('\nInorder:   ', tree.inorder().join(' → '));
console.log('Preorder:  ', tree.preorder().join(' → '));
console.log('Postorder: ', tree.postorder().join(' → '));
console.log('LevelOrder:', tree.levelOrder().map((l,i) => `L${i}:[${l}]`).join('  '));

console.log('\nHeight:    ', tree.height());
console.log('Count:     ', tree.count());

console.log('\nSearch 40: ', tree.search(40));
console.log('Search 99: ', tree.search(99));

console.log('\nDeleting 30 (two children)...');
tree.delete(30);
console.log('Inorder:   ', tree.inorder().join(' → '));

console.log('Deleting 80 (leaf)...');
tree.delete(80);
console.log('Inorder:   ', tree.inorder().join(' → '));

console.log('\nFinal count:', tree.count(), '| Height:', tree.height());
