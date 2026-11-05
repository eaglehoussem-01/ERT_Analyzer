import matplotlib
matplotlib.use("Agg")
import pygimli as pg
from pygimli.physics import ert
import matplotlib.pyplot as plt
electrodes=pg.Vector(range(0, 60, 5))
print(f"عدد الأقطاب: {len(electrodes)}")
print(f"مواقع الأقطاب: {list(electrodes)}")
scheme=ert.createData(elecs=electrodes, schemeName="wa")
print(f"عدد القياسات (Wenner): {scheme.size()}")
print()
mesh=pg.createGrid(
    x=pg.utils.grange(-10, 70, n=80),
    y=pg.utils.grange(-30, 2, n=30)
)
print(f"عدد الخلايا في الشبكة: {mesh.cellCount()}")
print()
res=[]
for cell in mesh.cells():
    y_center=cell.center()[1]
    if y_center>-10:
        res.append(500.0)
    else:
        res.append(50.0)
print(f"نموذج أرضي: طبقتان")
print(f"  الطبقة العليا (0 to 10 m): 500 Ohm.m")
print(f"  الطبقة السفلى (10 to 30 m): 50 Ohm.m")
print()
print("جاري المحاكاة الأمامية...")
mgr = ert.ERTManager(scheme)
synth = mgr.simulate(mesh, res=res, verbose=False)
rhoa_synth = synth["rhoa"]
print(f"تمت المحاكاة!")
print(f"  عدد القياسات المحسوبة: {synth.size()}")
print(f"  نطاق المقاومية الظاهرية: {min(rhoa_synth):.1f} - {max(rhoa_synth):.1f} Ohm.m")
print()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
pg.show(mesh, res, ax=ax1, cMin=10, cMax=1000,
        logScale=True, cMap="jet",
        label="True Resistivity (Ohm.m)")
ax1.set_title("True Resistivity Model (Input)", fontsize=13)
ax1.set_xlabel("Distance (m)")
ax1.set_ylabel("Depth (m)")
ert.showData(synth, ax=ax2, cMin=10, cMax=1000,
             logScale=True, cMap="jet",
             label="Apparent Resistivity (Ohm.m)")
ax2.set_title("Forward Response - Simulated Pseudosection", fontsize=13)

plt.tight_layout()
plt.savefig("../output/forward_model_2layer.png", dpi=300, bbox_inches="tight")
plt.show()

print("تم حفظ الرسم في: forward_model_2layer.png")