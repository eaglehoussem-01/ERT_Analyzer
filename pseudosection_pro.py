import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.interpolate import griddata
data= pd.read_csv("../data/ert_500_with_rho.csv")
x = data["x_center"].values
y = data["pseudo_depth"].values
z = data["rho_app"].values
print(f"عدد القياسات: {len(x)}")
print(f"نطاق X: {x.min():.1f} - {x.max():.1f} م")
print(f"نطاق العمق: {y.min():.1f} - {y.max():.1f} م")
print(f"نطاق المقاومية: {z.min():.1f} - {z.max():.1f} Ohm.m")
print()
grid_x = np.linspace(x.min(), x.max(), 300)
grid_y = np.linspace(y.min(), y.max(), 100)
X, Y = np.meshgrid(grid_x, grid_y)
print(f"حجم الشبكة: {X.shape[1]} x {X.shape[0]} = {X.shape[0] * X.shape[1]} نقطة")

Z = griddata(
    points=(x, y),
    values=z,
    xi=(X, Y),
    method="cubic"
)
Z = np.where(Z <= 0, np.nan, Z)

print("تم الاستيفاء بنجاح")
print()
fig, ax = plt.subplots(figsize=(14, 5))
levels = np.logspace(
    np.log10(z.min()),
    np.log10(z.max()),
    20
)

contour = ax.contourf(
    X, Y, Z,
    levels=levels,
    cmap="jet",
    norm=LogNorm()
)
ax.scatter(x, y, c="black", s=3, alpha=0.3)
ax.invert_yaxis()
ax.set_xlabel("Distance (m)", fontsize=12)
ax.set_ylabel("Pseudo-depth (m)", fontsize=12)
ax.set_title("Apparent Resistivity Pseudosection (Contour Fill) - Wenner", fontsize=13)
cbar = plt.colorbar(contour, ax=ax)
cbar.set_label("Apparent Resistivity (Ohm.m)", fontsize=11)
plt.tight_layout()
plt.savefig("../output/pseudosection_contour.png", dpi=300, bbox_inches="tight")
plt.show()
print("تم حفظ الرسم في: pseudosection_contour.png")


