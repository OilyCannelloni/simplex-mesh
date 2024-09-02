import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_json(path_or_buf="C:\\Users\\barte\\Desktop\\mesh\\silabs\\silabs-0902-1114-1wall-4m.jsonl", lines=True)

# grouped = {5: [], 10: [], 15:[], 20:[]}
#
# for row in data.iterrows():
#     group = (int(row[1]["distance"]) + 2.5) // 5 * 5
#     grouped[int(group)].append(row[1]["distance"])
#
# fig, axs = plt.subplots(1, 4)
#
# for i, (target, data) in enumerate(grouped.items()):
#     axs[i].hist(data, bins=np.arange(min(data), max(data) + 0.03, 0.03))
#     axs[i].axvline(target, c="orange")
#
# fig.suptitle("SiLabs Openspace")
# fig.supxlabel("Distance")
# fig.supylabel("Frequency")

d = data["distance"]

plt.title("SiLabs 3.5m through 1 thick wall")
plt.xlabel("Distance")
plt.ylabel("Frequency")
plt.hist(d, bins=np.arange(min(d), max(d) + 0.1, 0.1))
plt.axvline(3.5, c="orange")


plt.show()