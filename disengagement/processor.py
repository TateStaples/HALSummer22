# takes the encoded data from encoded.xlsx and fit decision tree on it

from sklearn.tree import *
import pandas as pds
import numpy as np
from matplotlib import pyplot as plt

# read the file
data: pds.DataFrame = pds.read_excel("encoded.xlsx")
# seperate inputs and results
output: np.array = np.array(data["output"].values.tolist())
input: np.array = np.array(data.values.tolist())[:, :-1]

# create adn fit the tree
tree = DecisionTreeClassifier(criterion="gini", max_depth=5)
tree.fit(input, output)
tree.tree_.children_left

# output the results
feature_names = [str(col).split()[0] for col in data.columns][:-1]
plot_tree(tree, label="root", filled=True, feature_names=feature_names, class_names=("human", "av"), impurity=False, fontsize=5)
plt.show()

print(export_text(tree, feature_names=feature_names))
print(tree.score(input, output))


if __name__ == '__main__':
    pass