import pandas as pd
data=pd.read_csv("../data/ert_500_wenner.csv", comment="#")
original_count = int(len(data))
print("=" * 50)
print("ERT Data Cleaning Report")
print("=" * 50)
print()
print(f"البيانات الخام: {original_count} قياس")
print()
neg_mask=data["voltage_mV"]<0
neg_count=int(neg_mask.sum())
data = data[~neg_mask]
print(f"الخطوة 1 - حذف القيم السالبة:")
print(f"  عدد القيم السالبة: {neg_count}")
print(f"  القياسات المتبقية: {int(len(data))}")
print()
zero_mask=data["voltage_mV"]==0
zero_count=int(zero_mask.sum())
data = data[~zero_mask]
print(f"الخطوة 2 - حذف القيم الصفرية:")
print(f"  عدد القيم الصفرية: {zero_count}")
print(f"  القياسات المتبقية: {int(len(data))}")
print()
Q1 = float(data["voltage_mV"].quantile(0.25))
Q3 = float(data["voltage_mV"].quantile(0.75))
IQR = Q3 - Q1
lower_bound=Q1-1.5*IQR
upper_bound=Q3+1.5*IQR
print(f"الخطوة 3 - حذف القيم الشاذة (IQR):")
print(f"  Q1 = {round(Q1, 2)}")
print(f"  Q3 = {round(Q3, 2)}")
print(f"  IQR = {round(IQR, 2)}")
print(f"  الحد الأدنى = {round(lower_bound, 2)}")
print(f"  الحد الأقصى = {round(upper_bound, 2)}")
outlier_mask=(data["voltage_mV"] < lower_bound) | (data["voltage_mV"] > upper_bound)
outlier_count=int(outlier_mask.sum())
data = data[~outlier_mask]
print(f"  عدد القيم الشاذة: {outlier_count}")
print(f"  القياسات المتبقية: {int(len(data))}")
print()
data=data.reset_index(drop=True)
data.to_csv("ert_500_clean.csv", index=False)
clean_count = int(len(data))
total_removed = original_count - clean_count
removed_percent = round(total_removed / original_count * 100, 1)

print("=" * 50)
print("   ملخص التنظيف")
print("=" * 50)
print(f"القياسات الأصلية: {original_count}")
print(f"القياسات المحذوفة: {total_removed}")
print(f"  - قيم سالبة: {neg_count}")
print(f"  - قيم صفرية: {zero_count}")
print(f"  - قيم شاذة: {outlier_count}")
print(f"القياسات النظيفة: {clean_count}")
print(f"نسبة الحذف: {removed_percent}%")
print()

if removed_percent < 5:
    print("الحكم: نسبة الحذف مقبولة (< 5%)")
elif removed_percent < 15:
    print("الحكم: نسبة الحذف مرتفعة قليلاً، تحقق من جودة المسح")
else:
    print("الحكم: نسبة الحذف عالية جداً! راجع بيانات الميدان")

print()
print("تم حفظ البيانات النظيفة في: ert_500_clean.csv")

