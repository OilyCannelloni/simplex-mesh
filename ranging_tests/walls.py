import pandas as pd
import matplotlib.pyplot as plt

FILENAME = "./walls/nrfdm_2024-05-13_08-35_1650mm.csv"
TARGET = 16.5
TITLE = "16.5m through 2 thin walls"
LD = - 0.3

df = pd.read_csv(FILENAME)

df.drop(["Addr", "RSSI", "PS", "BEST"], axis=1)
df = df.drop(df[(abs(df["MCPD"] - df["IFFT"]) > 8) | (df["MCPD"] < 1) | (df["IFFT"] < 1)].index)

length = len(df["MCPD"])

df["MCPD"] = df["MCPD"].rolling(5).median() - 0.6
df["IFFT"] = df["IFFT"].rolling(5).median() - 0.6
mean_mcpd = df["MCPD"].mean()
mean_ifft = df["IFFT"].mean()

plt.title(TITLE)
plt.xlabel("Sample #")
plt.ylabel("Measured distance [m]")

plt.scatter(range(length), df["MCPD"], color="tab:blue")
plt.scatter(range(length), df["IFFT"], color="tab:orange")

plt.axhline(y=mean_mcpd, color='tab:blue', linestyle='-', alpha=0.4)
plt.axhline(y=mean_ifft, color='tab:orange', linestyle='-', alpha=0.4)
plt.axhline(y=TARGET, color='tab:green', linestyle='-', linewidth=3)

t = plt.text(0, TARGET - LD, str(TARGET), ha='left', va='bottom', color="tab:green", size=12, weight="bold")
t.set_bbox(dict(facecolor="white", alpha=1, linewidth=0))

# plt.ylim((5, 23))
plt.legend(labels=["MCPD", "IFFT"])
plt.show()