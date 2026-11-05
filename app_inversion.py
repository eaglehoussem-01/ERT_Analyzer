import matplotlib

matplotlib.use("Agg")
import streamlit as st
import pygimli as pg
from pygimli.physics import ert
import matplotlib.pyplot as plt
import numpy as np
st.title("ERT 2D Inversion")
st.write("الانعكاس ثنائي الأبعاد لبيانات المقاومية الكهربائية")
st.sidebar.header("إعدادات المسح")
num_electrodes=st.sidebar.slider("عدد الأقطاب", 8, 24, 12, step=2)
spacing=st.sidebar.slider("تباعد الأقطاب (م)", 2.0, 10.0, 5.0, step=1.0)
st.sidebar.header("النموذج الحقيقي")
rho_top=st.sidebar.number_input("مقاومية الطبقة العليا", 10, 5000, 500)
rho_bottom=st.sidebar.number_input("مقاومية الطبقة السفلى", 10, 5000, 50)
depth_interface=st.sidebar.slider("عمق الحد الفاصل (م)", 2, 20, 10)
st.sidebar.header("إعدادات الانعكاس")
noise_level=st.sidebar.slider("مستوى الضوضاء (%)", 0, 20, 5)
lam=st.sidebar.number_input("معامل التنعيم (lambda)", 1, 200, 20)
if st.button("تشغيل المحاكاة والانعكاس"):
    with st.spinner("جاري العمل..."):
        max_x = (num_electrodes - 1) * spacing
        electrodes = pg.Vector(
            [i * spacing for i in range(num_electrodes)]
        )
        scheme = ert.createData(
            elecs=electrodes, schemeName="wa"
        )
        mesh_fwd = pg.createGrid(
            x=pg.utils.grange(-10, max_x + 10, n=80),
            y=pg.utils.grange(-30, 2, n=30)
        )
        res_true = []
        for cell in mesh_fwd.cells():
            y_c = cell.center()[1]
            if y_c > -depth_interface:
                res_true.append(float(rho_top))
            else:
                res_true.append(float(rho_bottom))

        mgr_fwd = ert.ERTManager(scheme)
        synth = mgr_fwd.simulate(
            mesh_fwd, res=res_true, verbose=False
        )
        rhoa_clean = np.array(synth["rhoa"])
        noise = np.random.normal(0, noise_level / 100.0, len(rhoa_clean))
        rhoa_noisy = rhoa_clean * (1 + noise)

        data = pg.DataContainerERT(scheme)
        data["rhoa"] = rhoa_noisy
        data["err"] = np.abs(noise) + 0.01

        st.write(f"عدد القياسات: {data.size()}")
        st.write(f"الضوضاء المضافة: {noise_level}%")
        mgr_inv = ert.ERTManager(data)

        mesh_inv = mgr_inv.createMesh(
            data=data,
            quality=32.5,
            paraDX=0.5,
            paraDepth=30.0
        )

        model = mgr_inv.invert(
            mesh=mesh_inv,
            lam=lam,
            verbose=False
        )

        rms = mgr_inv.inv.relrms()
        chi2 = mgr_inv.inv.chi2()

        st.success(f"تم الانعكاس بنجاح!")
        st.write(f"**RMS Error:** {rms:.2f}%")
        st.write(f"**Chi-squared:** {chi2:.2f}")

        if rms < 5:
            st.write("التقييم: انعكاس ممتاز")
        elif rms < 10:
            st.write("التقييم: انعكاس جيد")
        elif rms < 20:
            st.write("التقييم: انعكاس مقبول")
        else:
            st.write("التقييم: انعكاس ضعيف - راجع المعاملات")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        pg.show(
            mesh_fwd, res_true, ax=ax1,
            cMin=min(rho_top, rho_bottom),
            cMax=max(rho_top, rho_bottom),
            logScale=True, cMap="jet",
            label="True Resistivity (Ohm.m)"
        )
        ax1.set_title("True Model (Input)", fontsize=12)
        ax1.set_xlabel("Distance (m)")
        ax1.set_ylabel("Depth (m)")
        st.subheader("1. النموذج الحقيقي")
        st.pyplot(fig1)
        plt.close(fig1)


        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ert.showData(
            data, ax=ax2,
            logScale=True, cMap="jet",
            label="Apparent Resistivity (Ohm.m)"
        )
        ax2.set_title("Noisy Data (Pseudosection)", fontsize=12)
        st.subheader("2. البيانات المدخلة (مع ضوضاء)")
        st.pyplot(fig2)
        plt.close(fig2)


        fig3, ax3 = plt.subplots(figsize=(10, 4))
        pg.show(
            mesh_inv, model, ax=ax3,
            cMin=min(rho_top, rho_bottom),
            cMax=max(rho_top, rho_bottom),
            logScale=True, cMap="jet",
            label="Inverted Resistivity (Ohm.m)"
        )
        ax3.set_title(f"Inverted Model (RMS={rms:.1f}%)", fontsize=12)
        ax3.set_xlabel("Distance (m)")
        ax3.set_ylabel("Depth (m)")
        st.subheader("3. النموذج المعكوس (النتيجة)")
        st.pyplot(fig3)
        plt.close(fig3)
        st.subheader("مقارنة سريعة")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("المقاومية الحقيقية (العليا)", f"{rho_top} Ohm.m")
            st.metric("المقاومية الحقيقية (السفلى)", f"{rho_bottom} Ohm.m")
        with col2:
            model_arr = np.array(model)
            st.metric("المقاومية المعكوسة (المتوسط العلوي)",
                      f"{np.mean(model_arr[model_arr > np.median(model_arr)]):.0f} Ohm.m")
            st.metric("المقاومية المعكوسة (المتوسط السفلي)",
                      f"{np.mean(model_arr[model_arr <= np.median(model_arr)]):.0f} Ohm.m")
