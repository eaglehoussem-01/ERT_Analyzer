import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
data=pd.read_csv("../data/ert_500_with_rho.csv")
print(f"عدد القياسات: {int(len(data))}")
print(f"نطاق المقاومية: {float(data['rho_app'].min()):.1f} - {float(data['rho_app'].max()):.1f} Ohm.m")
print()
fig, ax = plt.subplots(figsize=(14, 5))
scatter = ax.scatter(
    data["x_center"],
    data["pseudo_depth"],
    c=data["rho_app"],
    cmap="jet",
    norm=LogNorm(),
    s=40,
    edgecolors="black",
    linewidths=0.3
)
ax.invert_yaxis()

ax.set_xlabel("Distance (m)", fontsize=12)
ax.set_ylabel("Pseudo-depth (m)", fontsize=12)
ax.set_title("Apparent Resistivity Pseudosection - Wenner Array", fontsize=14)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Apparent Resistivity (Ohm.m)", fontsize=11)
plt.tight_layout()
plt.savefig("../output/pseudosection_wenner.png", dpi=300, bbox_inches="tight")
plt.show()
print("تم حفظ الرسم في: pseudosection_wenner.png")