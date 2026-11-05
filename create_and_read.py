import pandas as pd
import random
import math

num_electrodes = 57
spacing = 5.0
current_base_mA = 200.0

rho_layer1 = 500.0
rho_layer2 = 50.0
depth_interface = 10.0

c1_list = []
p1_list = []
p2_list = []
c2_list = []
current_list = []
voltage_list = []

n_level = 1
total = 0

while total < 500:
    s = n_level * spacing
    max_in_level = num_electrodes - 3 * n_level

    if max_in_level <= 0:
        break

    for i in range(max_in_level):
        if total >= 500:
            break

        c1 = i * spacing
        p1 = c1 + s
        p2 = p1 + s
        c2 = p2 + s

        pseudo_depth = 0.519 * s

        if pseudo_depth < depth_interface:
            rho_app = rho_layer1
        else:
            weight = min((pseudo_depth - depth_interface) / 20.0, 0.9)
            rho_app = rho_layer1 * (1 - weight) + rho_layer2 * weight

        noise = random.uniform(-0.05, 0.05)
        rho_app = rho_app * (1 + noise)

        K = 2 * math.pi * s
        I_amps = current_base_mA / 1000.0
        V_volts = rho_app * I_amps / K
        V_mV = V_volts * 1000.0

        I_actual = current_base_mA + random.uniform(-3, 3)

        c1_list.append(round(c1, 1))
        p1_list.append(round(p1, 1))
        p2_list.append(round(p2, 1))
        c2_list.append(round(c2, 1))
        current_list.append(round(I_actual, 1))
        voltage_list.append(round(V_mV, 2))

        total = total + 1

    n_level = n_level + 1


voltage_list[10] = -abs(voltage_list[10])
voltage_list[55] = -abs(voltage_list[55])
voltage_list[120] = -abs(voltage_list[120])
voltage_list[250] = -abs(voltage_list[250])
voltage_list[400] = -abs(voltage_list[400])

voltage_list[30] = voltage_list[30] * 15
voltage_list[180] = voltage_list[180] * 15
voltage_list[350] = voltage_list[350] * 15

voltage_list[75] = 0.0
voltage_list[300] = 0.0

data = pd.DataFrame({
    "C1_x": c1_list,
    "P1_x": p1_list,
    "P2_x": p2_list,
    "C2_x": c2_list,
    "current_mA": current_list,
    "voltage_mV": voltage_list
})

with open("../data/ert_500_wenner.csv", "w") as f:
    f.write("# ERT Survey - Wenner Array (Synthetic)\n")
    f.write("# Electrode Spacing: 5.0 m\n")
    f.write("# Number of Electrodes: 57\n")
    f.write("# Model: 2-layer (500 over 50 Ohm.m, interface at 10m)\n")
    f.write("# WARNING: Contains intentional bad data for training\n")
    data.to_csv(f, index=False)

print("=== تم إنشاء الملف بنجاح! ===")
print(f"عدد القياسات: {len(data)}")
print(f"عدد المستويات: {n_level - 1}")
print()

loaded = pd.read_csv("../data/ert_500_wenner.csv", comment="#")

print("أول 5 صفوف:")
print(loaded.head())
print()

print("آخر 5 صفوف:")
print(loaded.tail())
print()

print("إحصاءات وصفية:")
print(loaded.describe())
print()

neg_count = (loaded["voltage_mV"] < 0).sum()
zero_count = (loaded["voltage_mV"] == 0).sum()
print(f"قيم جهد سالبة: {neg_count}")
print(f"قيم جهد صفرية: {zero_count}")