import matplotlib
matplotlib.use("Agg")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.interpolate import griddata
import io

st.set_page_config(
    page_title="ERT Analyzer",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ ERT Data Analyzer & 2D Subsurface Modeler")
st.write("أداة تحليل بيانات المقاومية الكهربائية والنمذجة ثنائية الأبعاد")

st.sidebar.header("الإعدادات")

data_source = st.sidebar.radio(
    "مصدر البيانات",
    ["رفع ملف", "بيانات تجريبية"]
)

st.sidebar.markdown("---")
st.sidebar.header("إعدادات التنظيف")
remove_negative = st.sidebar.checkbox("حذف القيم السالبة", value=True)
remove_zero = st.sidebar.checkbox("حذف القيم الصفرية", value=True)
remove_outliers = st.sidebar.checkbox("حذف القيم الشاذة (IQR)", value=True)

st.sidebar.markdown("---")
st.sidebar.header("إعدادات الانعكاس")
run_inversion = st.sidebar.checkbox("تشغيل الانعكاس", value=False)
lam = st.sidebar.slider("معامل التنعيم (lambda)", 1, 200, 20)


data = None

if data_source == "رفع ملف":
    uploaded_file = st.file_uploader(
        "ارفع ملف بيانات (CSV)",
        type=["csv"]
    )
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file, comment="#")

elif data_source == "بيانات تجريبية":
    st.info("استخدام بيانات تجريبية (500 قياس Wenner - بيانات اصطناعية)")

    num_electrodes = 57
    spacing = 5.0
    rho1, rho2, depth_int = 500.0, 50.0, 10.0

    c1_l, p1_l, p2_l, c2_l = [], [], [], []
    cur_l, vol_l = [], []
    total = 0
    n_level = 1

    while total < 500:
        s = n_level * spacing
        max_in = num_electrodes - 3 * n_level
        if max_in <= 0:
            break
        for i in range(max_in):
            if total >= 500:
                break
            c1 = i * spacing
            p1 = c1 + s
            p2 = p1 + s
            c2 = p2 + s
            pd_depth = 0.519 * s

            if pd_depth < depth_int:
                rho_a = rho1
            else:
                w = min((pd_depth - depth_int) / 20.0, 0.9)
                rho_a = rho1 * (1 - w) + rho2 * w

            rho_a *= (1 + np.random.uniform(-0.05, 0.05))

            K = 2 * np.pi * s
            I_a = 0.2
            V_v = rho_a * I_a / K

            c1_l.append(round(c1, 1))
            p1_l.append(round(p1, 1))
            p2_l.append(round(p2, 1))
            c2_l.append(round(c2, 1))
            cur_l.append(round(200 + np.random.uniform(-3, 3), 1))
            vol_l.append(round(V_v * 1000, 2))
            total += 1
        n_level += 1

    vol_l[10] = -abs(vol_l[10])
    vol_l[55] = -abs(vol_l[55])
    vol_l[120] = -abs(vol_l[120])
    vol_l[75] = 0.0
    vol_l[300] = 0.0
    vol_l[30] = vol_l[30] * 15
    vol_l[180] = vol_l[180] * 15

    data = pd.DataFrame({
        "C1_x": c1_l, "P1_x": p1_l,
        "P2_x": p2_l, "C2_x": c2_l,
        "current_mA": cur_l, "voltage_mV": vol_l
    })

if data is not None:

    original_count = int(len(data))

    tab1, tab2, tab3, tab4 = st.tabs([
        "1. فحص البيانات",
        "2. التنظيف",
        "3. Pseudosection",
        "4. الانعكاس"
    ])

    with tab1:
        st.subheader("فحص البيانات الخام")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد القياسات", original_count)
        with col2:
            st.metric("عدد الأعمدة", int(data.shape[1]))
        with col3:
            cols_str = ", ".join(data.columns.tolist())
            st.write(f"**الأعمدة:** {cols_str}")

        st.write("**أول 5 صفوف:**")
        st.dataframe(data.head())

        st.write("**إحصاءات وصفية:**")
        st.dataframe(
            data.describe(
                percentiles=[0.25, 0.50, 0.75]
            ).round(2)
        )

        if "voltage_mV" in data.columns:
            neg = int((data["voltage_mV"] < 0).sum())
            zer = int((data["voltage_mV"] == 0).sum())
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("قيم جهد سالبة", neg)
            with col_b:
                st.metric("قيم جهد صفرية", zer)


    with tab2:
        st.subheader("تنظيف البيانات")

        clean = data.copy()
        removed_neg = 0
        removed_zero = 0
        removed_out = 0

        if remove_negative and "voltage_mV" in clean.columns:
            mask = clean["voltage_mV"] < 0
            removed_neg = int(mask.sum())
            clean = clean[~mask]

        if remove_zero and "voltage_mV" in clean.columns:
            mask = clean["voltage_mV"] == 0
            removed_zero = int(mask.sum())
            clean = clean[~mask]

        if remove_outliers and "voltage_mV" in clean.columns:
            Q1 = float(clean["voltage_mV"].quantile(0.25))
            Q3 = float(clean["voltage_mV"].quantile(0.75))
            IQR = Q3 - Q1
            low = Q1 - 1.5 * IQR
            high = Q3 + 1.5 * IQR
            mask = (clean["voltage_mV"] < low) | (clean["voltage_mV"] > high)
            removed_out = int(mask.sum())
            clean = clean[~mask]

        clean = clean.reset_index(drop=True)
        clean_count = int(len(clean))
        total_removed = original_count - clean_count

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("الأصلية", original_count)
        with col2:
            st.metric("المحذوفة", total_removed)
        with col3:
            st.metric("النظيفة", clean_count)
        with col4:
            pct = round(total_removed / original_count * 100, 1) if original_count > 0 else 0
            st.metric("نسبة الحذف", f"{pct}%")

        st.write(f"- سالبة: {removed_neg} | صفرية: {removed_zero} | شاذة: {removed_out}")

        # حساب المقاومية الظاهرية
        if all(c in clean.columns for c in ["C1_x", "P1_x", "P2_x", "C2_x", "current_mA", "voltage_mV"]):
            clean["current_A"] = clean["current_mA"] / 1000.0
            clean["voltage_V"] = clean["voltage_mV"] / 1000.0
            clean["a"] = clean["P1_x"] - clean["C1_x"]
            clean["K"] = 2.0 * np.pi * clean["a"]
            clean["rho_app"] = clean["K"] * clean["voltage_V"] / clean["current_A"]
            clean["x_center"] = (clean["C1_x"] + clean["C2_x"]) / 2.0
            clean["pseudo_depth"] = 0.519 * clean["a"]

            st.write("**إحصاءات المقاومية الظاهرية (Ohm.m):**")
            st.dataframe(clean["rho_app"].describe(percentiles=[0.25, 0.50, 0.75]).round(2))

    with tab3:
        st.subheader("Pseudosection - المقاومية الظاهرية")

        if "rho_app" in clean.columns:
            x = clean["x_center"].values
            y = clean["pseudo_depth"].values
            z = clean["rho_app"].values

            z_pos = z[z > 0]
            if len(z_pos) > 10:
                grid_x = np.linspace(x.min(), x.max(), 300)
                grid_y = np.linspace(y.min(), y.max(), 100)
                X, Y = np.meshgrid(grid_x, grid_y)

                Z = griddata((x, y), z, (X, Y), method="cubic")
                Z = np.where(Z <= 0, np.nan, Z)

                fig, ax = plt.subplots(figsize=(14, 5))

                levels = np.logspace(
                    np.log10(max(z_pos.min(), 0.1)),
                    np.log10(z_pos.max()),
                    20
                )

                cf = ax.contourf(
                    X, Y, Z,
                    levels=levels,
                    cmap="jet",
                    norm=LogNorm()
                )
                ax.scatter(x, y, c="black", s=2, alpha=0.2)
                ax.invert_yaxis()
                ax.set_xlabel("Distance (m)", fontsize=12)
                ax.set_ylabel("Pseudo-depth (m)", fontsize=12)
                ax.set_title("Apparent Resistivity Pseudosection", fontsize=13)

                cbar = plt.colorbar(cf, ax=ax)
                cbar.set_label("Apparent Resistivity (Ohm.m)")

                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)


                buf = io.BytesIO()
                fig_save, ax_save = plt.subplots(figsize=(14, 5))
                ax_save.contourf(X, Y, Z, levels=levels, cmap="jet", norm=LogNorm())
                ax_save.invert_yaxis()
                ax_save.set_xlabel("Distance (m)")
                ax_save.set_ylabel("Pseudo-depth (m)")
                ax_save.set_title("Apparent Resistivity Pseudosection")
                plt.colorbar(ax_save.contourf(X, Y, Z, levels=levels, cmap="jet", norm=LogNorm()), ax=ax_save).set_label("Ohm.m")
                plt.tight_layout()
                fig_save.savefig(buf, format="png", dpi=300, bbox_inches="tight")
                plt.close(fig_save)

                st.download_button(
                    label="تحميل Pseudosection (PNG)",
                    data=buf.getvalue(),
                    file_name="pseudosection.png",
                    mime="image/png"
                )
            else:
                st.warning("لا توجد بيانات كافية للرسم")
        else:
            st.warning("يجب تنظيف البيانات أولاً (التبويب 2)")


    with tab4:
        st.subheader("الانعكاس ثنائي الأبعاد")

        if not run_inversion:
            st.info("فعّل خيار 'تشغيل الانعكاس' من الشريط الجانبي")
        elif "rho_app" not in clean.columns:
            st.warning("يجب تنظيف البيانات أولاً")
        else:
            try:
                import pygimli as pg
                from pygimli.physics import ert as ert_mod

                with st.spinner("جاري الانعكاس (قد يستغرق 30-60 ثانية)..."):

                    x_vals = clean["x_center"].values
                    rho_vals = clean["rho_app"].values
                    a_vals = clean["a"].values

                    unique_a = np.unique(a_vals)
                    n_levels = len(unique_a)

                    n_elec = min(24, max(8, int(np.sqrt(len(clean)) * 1.5)))
                    max_x = x_vals.max()
                    elec_spacing = max_x / (n_elec - 1)
                    electrodes = pg.Vector(
                        [i * elec_spacing for i in range(n_elec)]
                    )

                    scheme = ert_mod.createData(
                        elecs=electrodes, schemeName="wa"
                    )

                    data_ert = pg.DataContainerERT(scheme)
                    rhoa_arr = np.array(scheme["rhoa"])
                    rhoa_arr[:] = np.median(rho_vals)
                    for i in range(min(len(rhoa_arr), len(rho_vals))):
                        rhoa_arr[i] = rho_vals[i]
                    data_ert["rhoa"] = rhoa_arr
                    data_ert["err"] = np.ones(len(rhoa_arr)) * 0.05

                    mgr = ert_mod.ERTManager(data_ert)
                    mesh_inv = mgr.createMesh(
                        data=data_ert,
                        quality=32.5,
                        paraDX=0.5,
                        paraDepth=30.0
                    )

                    model = mgr.invert(
                        mesh=mesh_inv,
                        lam=lam,
                        verbose=False
                    )

                    rms = mgr.inv.relrms()

                    st.success(f"تم الانعكاس! RMS = {rms:.2f}%")

                    fig, ax = plt.subplots(figsize=(12, 5))
                    pg.show(
                        mesh_inv, model, ax=ax,
                        logScale=True, cMap="jet",
                        label="Resistivity (Ohm.m)"
                    )
                    ax.set_title(
                        f"Inverted Resistivity Model (RMS={rms:.1f}%)",
                        fontsize=13
                    )
                    ax.set_xlabel("Distance (m)")
                    ax.set_ylabel("Depth (m)")
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close(fig)

            except ImportError:
                st.error("pyGIMLi غير مثبتة. ثبّتها من Settings → Python Interpreter → + → pygimli")
            except Exception as e:
                st.error(f"خطأ في الانعكاس: {str(e)}")

else:
    st.info("ارفع ملف بيانات أو اختر 'بيانات تجريبية' من الشريط الجانبي للبدء")