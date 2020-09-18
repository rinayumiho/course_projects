"""
CISC684 -- HW1 Group

Members: Jie Ren; Long Chen; Yun Tang; Yifan Wang (Leader)
"""
import sys, math, random
import pandas as pd
import numpy as np

# Command line arguments
L = int(sys.argv[1])
K = int(sys.argv[2])
train_path = sys.argv[3]
valid_path = sys.argv[4]
test_path = sys.argv[5]
to_print = sys.argv[6]
# For debug purpose
# print(sys.argv[1])
# print(sys.argv[2])
# print(sys.argv[3])
# print(sys.argv[4])
# print(sys.argv[5])
# print(sys.argv[6])

# Global Variables
label0 = 0
label1 = 0 
node_list = []

# Function Definitions 
class Node:
    def __init__(self, feature, label=-1):
        """
        label is used to denote whether or not a node is leaf.
            -1 -> non-leaf node
            0/1 -> leaf
        """
        self.feature = feature
        self.label = label
        self.right = None
        self.left = None

def load_data(file):
    data_file = pd.read_csv(file, header=0)
    attrs = list(data_file.columns.values)
    return attrs, data_file.to_numpy()

def log2(x):
    """
    Handle the condition where x = 0.    
    """
    if x == 0:
        return 0
    else:
        return math.log(x, 2)

def entropy(posi, nega):
    """
    Param:
        posi: int, positive count of current attribute
        nega: int, negative count of current attribute
    """
    if posi == 0 and nega == 0:
        return 0
    else:
        return - (posi / (posi + nega)) * log2(posi / (posi + nega)) - (nega / (posi + nega)) * log2(nega / (posi + nega))

def variance(posi, nega):
    """
    Param:
        posi: int, positive count of current attribute
        nega: int, negative count of current attribute
    """    
    if posi==0 and nega==0:
        return 0
    else: 
        return posi * nega / ((posi + nega) ** 2)

def gen_subarray(input_arr, attritbute, target_value):
    """
    Based on the give attribute index and tatget_value get a 
    subarray of the input_arr
    """
    subarr = []
    for r in input_arr:
        if r[attritbute] == target_value:
            subarr.append(r)

    return np.array(subarr)

def build_tree(node, input_arr, attrs, method):
    """
    Build decision tree based on given params

    Params:
        node: the node to begin with
        input_arr: the data array to train the tree
        attrs: the headers of the given data array, the feature attribute of
               node will be set to one of the values in attrs
        method: the heuristic to build decision tree. Value will be either
                'entropy' or 'variance' 
    """
    ones = len(gen_subarray(input_arr, -1, 1))
    zeros = len(gen_subarray(input_arr, -1, 0))

    if method == 'entropy':
        total = entropy(ones, zeros)
    elif method == 'variance':
        total = variance(ones, zeros)

    if total == 0:
        node.feature = -1 
        node.label = input_arr[0][-1]
        return node
    
    max_index = -1
    max_diff = -1

    for i in range(0, len(input_arr[0]) - 1):
        s1 = gen_subarray(input_arr, i, 1)
        s0 = gen_subarray(input_arr, i, 0)
        n1 = len(s1)
        n0 = len(s0)
        s0p = gen_subarray(s0, -1, 1)
        s0n = gen_subarray(s0, -1, 0)
        s1p = gen_subarray(s1, -1, 1)
        s1n = gen_subarray(s1, -1, 0)
        if method == 'entropy':
            partial = (n1/(n1+n0)) * entropy(len(s1p), len(s1n)) + (n0/(n0+n1)) * entropy(len(s0p), len(s0n))
        elif method == 'variance':
            partial = (n1/(n1+n0)) * variance(len(s1p), len(s1n)) + (n0/(n0+n1)) * variance(len(s0p), len(s0n))
        diff = total - partial
        if diff > max_diff:
            max_diff = diff
            max_index = i
    node.feature = attrs[max_index]
    left = Node("")
    left = build_tree(left, gen_subarray(input_arr, max_index, 0), attrs, method)
    
    right = Node("")
    right = build_tree(right, gen_subarray(input_arr, max_index, 1), attrs, method)       
    node.left = left
    node.right = right
    return node
                                   
def predict(test_instance, root, attrs):
    """
    Predict the label given a single instance
    """
    if root.right == None and root.left == None:
        return root.label
    else:
        x_ib = test_instance[attrs.index(root.feature)]
        if x_ib == 1:
            return predict(test_instance, root.right, attrs)
        else:
            return predict(test_instance, root.left, attrs)

def evaluate(root, input_arr, attrs):
    """
    Predict the label given a single instance
    """
    n_correct = 0
    for x in input_arr:
        p = predict(x, root, attrs)
        if p == x[-1]:
            n_correct += 1

    return n_correct / len(input_arr)   

def listify(node):
    """
    Go through all the nodes in the tree and store in a list
    """
    if not (node.left == None and node.right == None):
        node_list.append(node)
        listify(node.left)
        listify(node.right)

def majority(node):
    """
    Find the majority class the the given subtree
    """
    global label0
    global label1

    if node.left == None and node.right == None:
        if node.label == 0:
            label0 += 1
        elif node.label ==1:
            label1 += 1
    else:
        listify(node.left)
        listify(node.right)

def copy_tree(root):
    """
    Copy the tree
    """
    if root == None:
        return
    node = Node(root.feature, root.label)
    node.left = copy_tree(root.left)
    node.right = copy_tree(root.right)
    return node

def post_pruning(L, K, D, input_arr, valid_attrs):
    global node_list
    global label0
    global label1
    # The accuracy before and after proning
    after = 0
    before = evaluate(D, input_arr, valid_attrs)
    
    D_best = copy_tree(D)
    D_list = []
    for _ in range(L):
        D0 = copy_tree(D)
        m = random.randint(0,K)
        for _ in range(m):
            listify(D0)
            for ele in node_list:
                D_list.append(ele)
            p = random.randint(0, len(D_list)-1) 
            # Prone the tree node
            D_list[p].right = None
            D_list[p].left = None
            majority(D_list[p])
            if label0 > label1:
                D_list[p].label = 0
            elif label0 < label1:
                D_list[p].label = 1
            else:
                D_list[p].label = random.randint(0,1)            
            D_list[p].feature = None
            after = evaluate(D_list[0], input_arr, valid_attrs)
            
            label0 = 0
            label1 = 0 
            node_list = []
        if after > before:
            D_best = copy_tree(D_list[0])
    return D_best


def display(node, depth, attrs):
    if node.right == None and node.left == None:
        print(node.label)
    else:
        print("")
        for _ in range(0, depth):
            print("| ", end="")
        print(f'{node.feature} = 0 : ', end='')
        display(node.left, depth + 1, attrs)
    
        for _ in range(0, depth):
            print("| ", end = "")
        print(f'{node.feature} = 1 : ', end='')
        display(node.right, depth + 1, attrs)

# Load datasets and attributes
train_attrs, train_set = load_data(train_path)
test_attrs , test_set = load_data(test_path)
validation_attrs, validation_set = load_data(valid_path) 

print(
    f'train shape: {train_set.shape}\n'
    f'test shape: {test_set.shape}\n'
    f'valid shape: {validation_set.shape}\n'
)

# Create two trees using entropy and variance methods
entropy_tree = Node("")
entropy_tree = build_tree(entropy_tree, train_set, train_attrs, 'entropy')
variance_tree = Node("")
variance_tree = build_tree(variance_tree, train_set, train_attrs, 'variance')

# Compute the accuracies of the two trees
entropy_accuracy = evaluate(entropy_tree, test_set, test_attrs)
variance_accuracy = evaluate(variance_tree, test_set, test_attrs)

# Prone the two trees with the given algorithm and compute accuracies
new_etree = post_pruning(L, K, entropy_tree, validation_set, validation_attrs)
new_vtree = post_pruning(L, K, variance_tree, validation_set, validation_attrs)
e_acc = evaluate(new_etree, validation_set, validation_attrs)
v_acc = evaluate(new_vtree, validation_set, validation_attrs)

print(
    f'Entropy\n'
    f'Accuracy before prone: {entropy_accuracy}\n'
    f'Accuracy after  prone: {e_acc}\n\n'
    f'Variance\n'
    f'Accuracy before prone: {variance_accuracy}\n'
    f'Accuracy after  prone: {v_acc}\n\n'
)

if to_print.lower() == 'yes':
    print('\nTree built by using Entropy\n')
    display(entropy_tree, 0, train_attrs)

    print('\nTree built by using Variance\n')
    display(variance_tree, 0, train_attrs)    