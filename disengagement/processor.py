from sklearn.tree import *
import pandas as pds
import numpy as np
from matplotlib import pyplot as plt

data: pds.DataFrame = pds.read_excel("encoded.xlsx")
output: np.array = np.array(data["output"].values.tolist())
input: np.array = np.array(data.values.tolist())[:, :-1]
print(input.shape)
print(output.shape)
print(output.sum()/output.size)

tree = DecisionTreeClassifier(criterion="gini", max_depth=10, min_samples_split=5, min_samples_leaf=5)
tree.fit(input, output)

# show
feature_names = "AURORA", "WERIDE", "QCRAFT", "DEEPROUTE", "QUALCOMM", "AUTOX", "TOYOTA", "UDELV", "ARGO", "VALEO", "DIDI", "APOLLO", "MERCEDES", "CRUISE","WAYMO","GATIK","LYFT","APPLE","NISSAN","AIMOTIVE","ZOOX","EASYMILE","NURO","PONY","NVIDIA","date", "loc","auto capable"
print(len(feature_names))
plot_tree(tree, label="root", filled=True, feature_names=feature_names, class_names=("human", "av"), impurity=False, fontsize=5)
plt.show()

print(export_text(tree, feature_names=feature_names))
print(tree.score(input, output))


if __name__ == '__main__':
    pass