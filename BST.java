// Binary Search Tree — Java Implementation
// Operations: insert, search, delete, inorder, preorder, postorder traversal

public class BST {

    static class Node {
        int value;
        Node left, right;

        Node(int value) {
            this.value = value;
            this.left = null;
            this.right = null;
        }
    }

    private Node root;

    public BST() {
        root = null;
    }

    // ── Insert ─────────────────────────────────────────────────────────────
    public void insert(int value) {
        root = insertRec(root, value);
    }

    private Node insertRec(Node node, int value) {
        if (node == null) return new Node(value);
        if (value < node.value)      node.left  = insertRec(node.left,  value);
        else if (value > node.value) node.right = insertRec(node.right, value);
        // duplicate values are ignored
        return node;
    }

    // ── Search ─────────────────────────────────────────────────────────────
    public boolean search(int value) {
        return searchRec(root, value);
    }

    private boolean searchRec(Node node, int value) {
        if (node == null) return false;
        if (value == node.value) return true;
        return value < node.value
            ? searchRec(node.left,  value)
            : searchRec(node.right, value);
    }

    // ── Delete ─────────────────────────────────────────────────────────────
    public void delete(int value) {
        root = deleteRec(root, value);
    }

    private Node deleteRec(Node node, int value) {
        if (node == null) return null;

        if (value < node.value) {
            node.left = deleteRec(node.left, value);
        } else if (value > node.value) {
            node.right = deleteRec(node.right, value);
        } else {
            // Node to delete found
            if (node.left == null)  return node.right;
            if (node.right == null) return node.left;

            // Node has two children — replace with inorder successor
            node.value = minValue(node.right);
            node.right = deleteRec(node.right, node.value);
        }
        return node;
    }

    private int minValue(Node node) {
        int min = node.value;
        while (node.left != null) {
            min  = node.left.value;
            node = node.left;
        }
        return min;
    }

    // ── Height ─────────────────────────────────────────────────────────────
    public int height() {
        return heightRec(root);
    }

    private int heightRec(Node node) {
        if (node == null) return 0;
        return 1 + Math.max(heightRec(node.left), heightRec(node.right));
    }

    // ── Traversals ─────────────────────────────────────────────────────────
    public void inorder() {
        System.out.print("Inorder:   ");
        inorderRec(root);
        System.out.println();
    }

    private void inorderRec(Node node) {
        if (node == null) return;
        inorderRec(node.left);
        System.out.print(node.value + " ");
        inorderRec(node.right);
    }

    public void preorder() {
        System.out.print("Preorder:  ");
        preorderRec(root);
        System.out.println();
    }

    private void preorderRec(Node node) {
        if (node == null) return;
        System.out.print(node.value + " ");
        preorderRec(node.left);
        preorderRec(node.right);
    }

    public void postorder() {
        System.out.print("Postorder: ");
        postorderRec(root);
        System.out.println();
    }

    private void postorderRec(Node node) {
        if (node == null) return;
        postorderRec(node.left);
        postorderRec(node.right);
        System.out.print(node.value + " ");
    }

    // ── Level-Order (BFS) ──────────────────────────────────────────────────
    public void levelOrder() {
        if (root == null) { System.out.println("Tree is empty."); return; }
        java.util.Queue<Node> queue = new java.util.LinkedList<>();
        queue.add(root);
        System.out.print("LevelOrder: ");
        while (!queue.isEmpty()) {
            Node current = queue.poll();
            System.out.print(current.value + " ");
            if (current.left  != null) queue.add(current.left);
            if (current.right != null) queue.add(current.right);
        }
        System.out.println();
    }

    // ── Count Nodes ────────────────────────────────────────────────────────
    public int countNodes() {
        return countRec(root);
    }

    private int countRec(Node node) {
        if (node == null) return 0;
        return 1 + countRec(node.left) + countRec(node.right);
    }

    // ── Demo ───────────────────────────────────────────────────────────────
    public static void main(String[] args) {
        BST tree = new BST();
        int[] values = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45};

        System.out.println("=== Binary Search Tree — Java ===\n");
        System.out.print("Inserting: ");
        for (int v : values) {
            System.out.print(v + " ");
            tree.insert(v);
        }
        System.out.println("\n");

        tree.inorder();
        tree.preorder();
        tree.postorder();
        tree.levelOrder();

        System.out.println("\nHeight:     " + tree.height());
        System.out.println("Node count: " + tree.countNodes());

        System.out.println("\nSearch 40:  " + tree.search(40));
        System.out.println("Search 99:  " + tree.search(99));

        System.out.println("\nDeleting 30 (node with two children)...");
        tree.delete(30);
        tree.inorder();

        System.out.println("Deleting 20 (node with one child)...");
        tree.delete(20);
        tree.inorder();

        System.out.println("Deleting 10 (leaf node)...");
        tree.delete(10);
        tree.inorder();

        System.out.println("\nFinal node count: " + tree.countNodes());
    }
}
