import pandas as pd

file_path = "../data/ert_500_wenner.csv"
data = pd.read_csv(file_path, comment="#")

print("=" * 50)
print("   ERT Data Inspection Report")
print("=" * 50)
print()

num_rows = int(data.shape[0])
num_cols = int(data.shape[1])
print(f"عدد القياسات (الصفوف): {num_rows}")
print(f"عدد الأعمدة: {num_cols}")
print()

print("أسماء الأعمدة:")
for col in data.columns:
    print(f"  - {col}")
print()

print("أنواع البيانات في كل عمود:")
print(data.dtypes)
print()

print("عدد القيم المفقودة في كل عمود:")
print(data.isnull().sum())
print()

print("الإحصاءات الوصفية:")
print(data.describe(percentiles=[0.25, 0.50, 0.75]).round(2))
print()

print("فحص بنية ترتيب Wenner:")
print("-" * 40)

dist_c1_p1 = data["P1_x"] - data["C1_x"]
dist_p1_p2 = data["P2_x"] - data["P1_x"]
dist_p2_c2 = data["C2_x"] - data["P2_x"]

print(f"المسافة C1->P1: min={dist_c1_p1.min()}, max={dist_c1_p1.max()}")
print(f"المسافة P1->P2: min={dist_p1_p2.min()}, max={dist_p1_p2.max()}")
print(f"المسافة P2->C2: min={dist_p2_c2.min()}, max={dist_p2_c2.max()}")
print()

is_wenner = (dist_c1_p1 == dist_p1_p2) & (dist_p1_p2 == dist_p2_c2)
wenner_count = int(is_wenner.sum())
total_count = int(len(data))

print(f"قياسات تتوافق مع Wenner: {wenner_count} من {total_count}")

if wenner_count == total_count:
    print("جميع القياسات تتوافق مع ترتيب Wenner!")
else:
    diff = total_count - wenner_count
    print(f"تحذير: {diff} قياس لا يتوافق مع Wenner!")

print()

print("فحص القيم المشبوهة:")
print("-" * 40)

neg_voltage = int((data["voltage_mV"] < 0).sum())
zero_voltage = int((data["voltage_mV"] == 0).sum())
neg_current = int((data["current_mA"] <= 0).sum())

print(f"قيم جهد سالبة: {neg_voltage}")
print(f"قيم جهد صفرية: {zero_voltage}")
print(f"قيم تيار <= 0: {neg_current}")
print()

print("=" * 50)
print("   ملخص الفحص")
print("=" * 50)

bad_count = neg_voltage + zero_voltage
good_count = total_count - bad_count
bad_percent = round(bad_count / total_count * 100, 1)

if bad_count > 0:
    status = "تحتاج تنظيف"
else:
    status = "سليمة"

print(f"الحالة العامة: {status}")
print(f"إجمالي القياسات: {total_count}")
print(f"قياسات سليمة: {good_count}")
print(f"قياسات مشبوهة: {bad_count}")
print(f"نسبة القياسات المشبوهة: {bad_percent}%")
