import pandas as pd
import math
data=pd.read_csv("../data/ert_500_clean.csv")
print("=" * 50)
print("   حساب المقاومية الظاهرية (Wenner)")
print("=" * 50)
print()
print(f"عدد القياسات: {int(len(data))}")
print()
data["current_A"]=data["current_mA"]/1000.0
data["voltage_V"]=data["voltage_mV"]/1000.0
print(" ===========تحويل الوحدات============")
print(f"  التيار: mA -> A ")
print(f"  الجهد:  mV -> V ")
print()
data["a"]=data["P1_x"]-data["C1_x"]
print(" ==========حساب المسافة بين الأقطاب==========")
print(f"  أصغر مسافة: {float(data['a'].min())} م")
print(f"  أكبر مسافة: {float(data['a'].max())} م")
print()
data["K"] = 2.0 * math.pi * data["a"]
print("========== حساب K = 2 x pi x a==========")
print(f"  pi = {math.pi}")
print(f"  أصغر K: {round(float(data['K'].min()), 2)} م")
print(f"  أكبر K: {round(float(data['K'].max()), 2)} م")
print()
data["rho_app"]=data["K"]*data["voltage_V"]/data["current_A"]
print(" حساب rho_a = K x V / I")
print()
data["x_center"]=(data["C1_x"]+data["C2_x"])/2.0
data["pseudo_depth"] = 0.519 * data["a"]
print("========== حساب مواقع العرض==========")
print(f"  الموقع الأفقي = (C1 + C2) / 2")
print(f"  العمق الوسيطي = 0.519 x a")
print()
print("=" * 50)
print("   النتائج")
print("=" * 50)
print()
cols = ["C1_x", "P1_x", "P2_x", "C2_x", "a", "K", "rho_app", "x_center", "pseudo_depth"]
print("أول 5 قياسات:")
print(data[cols].head().round(2))
print()
print("آخر 5 قياسات:")
print(data[cols].tail().round(2))
print()
print("إحصاءات المقاومية الظاهرية (Ohm.m):")
print(data["rho_app"].describe(percentiles=[0.25, 0.50, 0.75]).round(2))
print()
print("التحقق من المنطق الفيزيائي:")
print("-" * 40)
rho_min=float(data["rho_app"].min())
rho_max=float(data["rho_app"].max())
print(f"  أقل مقاومية: {round(rho_min, 2)} Ohm.m")
print(f"  أعلى مقاومية: {round(rho_max, 2)} Ohm.m")
print()
if rho_min<0:
    print("  تحذير: توجد قيم سالبة! خطأ في الحساب")
elif rho_min<1:
    print("  ملاحظة: قيم منخفضة جداً (قد تكون مياه مالحة)")
else:
    print("  الحد الأدنى معقول")
if rho_max>100000:
    print("  ملاحظة: قيم عالية جداً (صخور جافة أو تجاويف)")
elif rho_max<100000:
    print("  ملاحظة: قيم عالية (صخور صلبة)")
else:
    print("  الحد الأقصى معقول")
print()
data.to_csv("ert_500_with_rho.csv", index=False)
print("تم حفظ البيانات في: ert_500_with_rho.csv")
print(f"عدد الأعمدة: {int(data.shape[1])}")
print(f"عدد الصفوف: {int(data.shape[0])}")
