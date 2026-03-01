// Binary Search Tree — C++ Implementation (OOP with templates & iterators)
// Operations: insert, search, delete, traversals, height, count

#include <iostream>
#include <queue>
#include <vector>
#include <functional>
#include <stdexcept>

template <typename T>
class BST {
private:
    struct Node {
        T value;
        Node* left;
        Node* right;
        explicit Node(T val) : value(val), left(nullptr), right(nullptr) {}
    };

    Node* root;

    // ── Private Helpers ──────────────────────────────────────────────────
    Node* insertRec(Node* node, const T& value) {
        if (!node) return new Node(value);
        if (value < node->value)      node->left  = insertRec(node->left,  value);
        else if (value > node->value) node->right = insertRec(node->right, value);
        return node;
    }

    bool searchRec(Node* node, const T& value) const {
        if (!node) return false;
        if (value == node->value) return true;
        return (value < node->value)
            ? searchRec(node->left,  value)
            : searchRec(node->right, value);
    }

    T minValue(Node* node) const {
        while (node->left) node = node->left;
        return node->value;
    }

    Node* deleteRec(Node* node, const T& value) {
        if (!node) return nullptr;
        if (value < node->value) {
            node->left = deleteRec(node->left, value);
        } else if (value > node->value) {
            node->right = deleteRec(node->right, value);
        } else {
            if (!node->left) { Node* tmp = node->right; delete node; return tmp; }
            if (!node->right){ Node* tmp = node->left;  delete node; return tmp; }
            node->value = minValue(node->right);
            node->right = deleteRec(node->right, node->value);
        }
        return node;
    }

    int heightRec(Node* node) const {
        if (!node) return 0;
        return 1 + std::max(heightRec(node->left), heightRec(node->right));
    }

    int countRec(Node* node) const {
        if (!node) return 0;
        return 1 + countRec(node->left) + countRec(node->right);
    }

    void inorderRec(Node* node, std::vector<T>& out) const {
        if (!node) return;
        inorderRec(node->left, out);
        out.push_back(node->value);
        inorderRec(node->right, out);
    }

    void preorderRec(Node* node, std::vector<T>& out) const {
        if (!node) return;
        out.push_back(node->value);
        preorderRec(node->left, out);
        preorderRec(node->right, out);
    }

    void postorderRec(Node* node, std::vector<T>& out) const {
        if (!node) return;
        postorderRec(node->left, out);
        postorderRec(node->right, out);
        out.push_back(node->value);
    }

    void freeRec(Node* node) {
        if (!node) return;
        freeRec(node->left);
        freeRec(node->right);
        delete node;
    }

public:
    // ── Constructor / Destructor ─────────────────────────────────────────
    BST() : root(nullptr) {}
    ~BST() { freeRec(root); }

    // Disable copy (deep copy would be needed)
    BST(const BST&) = delete;
    BST& operator=(const BST&) = delete;

    // ── Public API ───────────────────────────────────────────────────────
    void insert(const T& value)  { root = insertRec(root, value); }
    bool search(const T& value) const { return searchRec(root, value); }
    void remove(const T& value)  { root = deleteRec(root, value); }
    int  height()  const { return heightRec(root); }
    int  count()   const { return countRec(root); }
    bool isEmpty() const { return root == nullptr; }

    std::vector<T> inorder()   const { std::vector<T> v; inorderRec(root, v);   return v; }
    std::vector<T> preorder()  const { std::vector<T> v; preorderRec(root, v);  return v; }
    std::vector<T> postorder() const { std::vector<T> v; postorderRec(root, v); return v; }

    // Level-order (BFS) returns levels as vector of vectors
    std::vector<std::vector<T>> levelOrder() const {
        std::vector<std::vector<T>> result;
        if (!root) return result;
        std::queue<Node*> q;
        q.push(root);
        while (!q.empty()) {
            int sz = static_cast<int>(q.size());
            std::vector<T> level;
            for (int i = 0; i < sz; i++) {
                Node* cur = q.front(); q.pop();
                level.push_back(cur->value);
                if (cur->left)  q.push(cur->left);
                if (cur->right) q.push(cur->right);
            }
            result.push_back(level);
        }
        return result;
    }
};

// ── Print Helpers ──────────────────────────────────────────────────────────
template <typename T>
void printVec(const std::string& label, const std::vector<T>& vec) {
    std::cout << label;
    for (const auto& v : vec) std::cout << v << " ";
    std::cout << "\n";
}

// ── Demo ───────────────────────────────────────────────────────────────────
int main() {
    BST<int> tree;
    std::vector<int> values = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45};

    std::cout << "=== Binary Search Tree — C++ (Template) ===\n\n";
    std::cout << "Inserting: ";
    for (int v : values) { std::cout << v << " "; tree.insert(v); }
    std::cout << "\n\n";

    printVec("Inorder:   ", tree.inorder());
    printVec("Preorder:  ", tree.preorder());
    printVec("Postorder: ", tree.postorder());

    auto levels = tree.levelOrder();
    std::cout << "Level-order:\n";
    for (size_t i = 0; i < levels.size(); i++) {
        std::cout << "  L" << i << ": ";
        for (int v : levels[i]) std::cout << v << " ";
        std::cout << "\n";
    }

    std::cout << "\nHeight:     " << tree.height() << "\n";
    std::cout << "Node count: " << tree.count()  << "\n";

    std::cout << "\nSearch 40:  " << (tree.search(40) ? "found" : "not found") << "\n";
    std::cout << "Search 99:  " << (tree.search(99) ? "found" : "not found") << "\n";

    std::cout << "\nRemoving 30 (two children)...\n";
    tree.remove(30);
    printVec("Inorder: ", tree.inorder());

    std::cout << "Removing 80 (leaf)...\n";
    tree.remove(80);
    printVec("Inorder: ", tree.inorder());

    std::cout << "\nFinal node count: " << tree.count() << "\n";
    return 0;
}
