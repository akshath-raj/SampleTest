/* Binary Search Tree — C Implementation
   Operations: insert, search, delete, traversals, height, count */

#include <stdio.h>
#include <stdlib.h>

/* ── Data Structures ──────────────────────────────────────────────────── */
typedef struct Node {
    int value;
    struct Node* left;
    struct Node* right;
} Node;

typedef struct {
    Node* root;
} BST;

/* ── Node Helpers ─────────────────────────────────────────────────────── */
static Node* new_node(int value) {
    Node* node = (Node*)malloc(sizeof(Node));
    if (!node) { fprintf(stderr, "Out of memory\n"); exit(1); }
    node->value = value;
    node->left  = NULL;
    node->right = NULL;
    return node;
}

void bst_init(BST* tree) {
    tree->root = NULL;
}

/* ── Insert ───────────────────────────────────────────────────────────── */
static Node* insert_rec(Node* node, int value) {
    if (node == NULL) return new_node(value);
    if      (value < node->value) node->left  = insert_rec(node->left,  value);
    else if (value > node->value) node->right = insert_rec(node->right, value);
    return node;
}

void bst_insert(BST* tree, int value) {
    tree->root = insert_rec(tree->root, value);
}

/* ── Search ───────────────────────────────────────────────────────────── */
static int search_rec(Node* node, int value) {
    if (node == NULL)        return 0;
    if (value == node->value) return 1;
    if (value < node->value)  return search_rec(node->left,  value);
    return search_rec(node->right, value);
}

int bst_search(BST* tree, int value) {
    return search_rec(tree->root, value);
}

/* ── Min Value Helper ─────────────────────────────────────────────────── */
static int min_value(Node* node) {
    while (node->left != NULL) node = node->left;
    return node->value;
}

/* ── Delete ───────────────────────────────────────────────────────────── */
static Node* delete_rec(Node* node, int value) {
    if (node == NULL) return NULL;

    if (value < node->value) {
        node->left = delete_rec(node->left, value);
    } else if (value > node->value) {
        node->right = delete_rec(node->right, value);
    } else {
        /* Node found */
        if (node->left == NULL) {
            Node* tmp = node->right;
            free(node);
            return tmp;
        }
        if (node->right == NULL) {
            Node* tmp = node->left;
            free(node);
            return tmp;
        }
        /* Two children: swap with inorder successor */
        node->value = min_value(node->right);
        node->right = delete_rec(node->right, node->value);
    }
    return node;
}

void bst_delete(BST* tree, int value) {
    tree->root = delete_rec(tree->root, value);
}

/* ── Height ───────────────────────────────────────────────────────────── */
static int height_rec(Node* node) {
    if (node == NULL) return 0;
    int lh = height_rec(node->left);
    int rh = height_rec(node->right);
    return 1 + (lh > rh ? lh : rh);
}

int bst_height(BST* tree) {
    return height_rec(tree->root);
}

/* ── Count Nodes ──────────────────────────────────────────────────────── */
static int count_rec(Node* node) {
    if (node == NULL) return 0;
    return 1 + count_rec(node->left) + count_rec(node->right);
}

int bst_count(BST* tree) {
    return count_rec(tree->root);
}

/* ── Traversals ───────────────────────────────────────────────────────── */
static void inorder_rec(Node* node) {
    if (node == NULL) return;
    inorder_rec(node->left);
    printf("%d ", node->value);
    inorder_rec(node->right);
}

static void preorder_rec(Node* node) {
    if (node == NULL) return;
    printf("%d ", node->value);
    preorder_rec(node->left);
    preorder_rec(node->right);
}

static void postorder_rec(Node* node) {
    if (node == NULL) return;
    postorder_rec(node->left);
    postorder_rec(node->right);
    printf("%d ", node->value);
}

void bst_inorder(BST* tree)   { printf("Inorder:   "); inorder_rec(tree->root);   printf("\n"); }
void bst_preorder(BST* tree)  { printf("Preorder:  "); preorder_rec(tree->root);  printf("\n"); }
void bst_postorder(BST* tree) { printf("Postorder: "); postorder_rec(tree->root); printf("\n"); }

/* ── Free Memory ──────────────────────────────────────────────────────── */
static void free_rec(Node* node) {
    if (node == NULL) return;
    free_rec(node->left);
    free_rec(node->right);
    free(node);
}

void bst_free(BST* tree) {
    free_rec(tree->root);
    tree->root = NULL;
}

/* ── Demo ─────────────────────────────────────────────────────────────── */
int main(void) {
    BST tree;
    bst_init(&tree);

    int values[] = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45};
    int n = sizeof(values) / sizeof(values[0]);

    printf("=== Binary Search Tree — C ===\n\n");
    printf("Inserting: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", values[i]);
        bst_insert(&tree, values[i]);
    }
    printf("\n\n");

    bst_inorder(&tree);
    bst_preorder(&tree);
    bst_postorder(&tree);

    printf("\nHeight:     %d\n", bst_height(&tree));
    printf("Node count: %d\n",   bst_count(&tree));

    printf("\nSearch 40:  %s\n", bst_search(&tree, 40) ? "found" : "not found");
    printf("Search 99:  %s\n",   bst_search(&tree, 99) ? "found" : "not found");

    printf("\nDeleting 30 (two children)...\n");
    bst_delete(&tree, 30);
    bst_inorder(&tree);

    printf("Deleting 10 (leaf)...\n");
    bst_delete(&tree, 10);
    bst_inorder(&tree);

    printf("Deleting 70 (one child)...\n");
    bst_delete(&tree, 70);
    bst_inorder(&tree);

    printf("\nFinal node count: %d\n", bst_count(&tree));

    bst_free(&tree);
    return 0;
}
