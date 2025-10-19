#include <bits/stdc++.h>
using namespace std;

struct Node {
    char ch;
    int freq;
    Node *left, *right;
    Node(char c, int f) : ch(c), freq(f), left(NULL), right(NULL) {}
};

struct cmp {
    bool operator()(Node* a, Node* b) const {
        return a->freq > b->freq;
    }
};

void buildCode(Node* root, string str, unordered_map<char, string>& codes) {
    if (!root) return;
    if (!root->left && !root->right) {
        codes[root->ch] = str.empty() ? "0" : str;
        return;
    }
    buildCode(root->left, str + "0", codes);
    buildCode(root->right, str + "1", codes);
}

void deleteTree(Node* root) {
    if (!root) return;
    deleteTree(root->left);
    deleteTree(root->right);
    delete root;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cerr << "Usage: huffman <encode|decode> [args]" << endl;
        return 1;
    }

    string mode = argv[1];

    if (mode == "encode") {
        if (argc < 3) {
            cerr << "Usage: huffman encode <input_text>" << endl;
            return 1;
        }

        string text = argv[2];
        if (text.empty()) {
            cerr << "Error: Empty text" << endl;
            return 1;
        }

        // Frequency analysis
        unordered_map<char, int> freq;
        for (char c : text) freq[c]++;

        // Build Huffman tree
        priority_queue<Node*, vector<Node*>, cmp> pq;
        for (auto& [c, f] : freq) {
            pq.push(new Node(c, f));
        }

        // Handle single character case
        if (pq.size() == 1) {
            Node* single = pq.top();
            pq.pop();
            Node* root = new Node('\0', single->freq);
            root->left = single;
            pq.push(root);
        }

        while (pq.size() > 1) {
            Node *left = pq.top(); pq.pop();
            Node *right = pq.top(); pq.pop();
            Node *merged = new Node('\0', left->freq + right->freq);
            merged->left = left;
            merged->right = right;
            pq.push(merged);
        }

        Node* root = pq.top();
        pq.pop();

        // Build codes
        unordered_map<char, string> codes;
        buildCode(root, "", codes);

        // Encode text
        string encoded = "";
        for (char c : text) {
            encoded += codes[c];
        }

        // Output format: first line = encoded bits, then code map
        cout << encoded << "\n";
        for (auto& [c, code] : codes) {
            cout << (int)c << " " << code << "\n";
        }

        deleteTree(root);

    } else if (mode == "decode") {
        if (argc < 3) {
            cerr << "Usage: huffman decode <encoded_bits>" << endl;
            return 1;
        }

        string bits = argv[2];
        if (bits.empty()) {
            cerr << "Error: Empty bits" << endl;
            return 1;
        }

        // Read code map from stdin
        unordered_map<string, char> revCodes;
        int charCode;
        string code;

        while (cin >> charCode >> code) {
            revCodes[code] = (char)charCode;
        }

        if (revCodes.empty()) {
            cerr << "Error: No code map provided" << endl;
            return 1;
        }

        // Decode
        string decoded = "";
        string current = "";
        for (char bit : bits) {
            current += bit;
            if (revCodes.find(current) != revCodes.end()) {
                decoded += revCodes[current];
                current = "";
            }
        }

        if (!current.empty()) {
            cerr << "Warning: Incomplete code at end" << endl;
        }

        cout << decoded;

    } else {
        cerr << "Unknown mode: " << mode << endl;
        return 1;
    }

    return 0;
}

//g++ -O2 -o huffman huffman.cpp