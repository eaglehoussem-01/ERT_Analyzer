import matplotlib
matplotlib.use("Agg")

import streamlit as st
import pygimli as pg
from pygimli.physics import ert
import matplotlib.pyplot as plt

st.title("ERT 2D Forward Modeling")
st.write("محاكاة أمامية لمسح كهربائي ثنائي الأبعاد")

st.sidebar.header("إعدادات المسح")

num_electrodes = st.sidebar.slider("عدد الأقطاب", 8, 24, 12, step=2)
spacing = st.sidebar.slider("تباعد الأقطاب (م)", 2.0, 10.0, 5.0, step=1.0)
array_type = st.sidebar.selectbox("نوع الترتيب", ["wa", "dd", "sl"])

st.sidebar.header("النموذج الأرضي")
rho_top = st.sidebar.number_input("مقاومية الطبقة العليا (Ohm.m)", 10, 5000, 500)
rho_bottom = st.sidebar.number_input("مقاومية الطبقة السفلى (Ohm.m)", 10, 5000, 50)
depth_interface = st.sidebar.slider("عمق الحد الفاصل (م)", 2, 20, 10)

if st.button("تشغيل المحاكاة"):

    with st.spinner("جاري المحاكاة..."):


        max_x = (num_electrodes - 1) * spacing
        electrodes = pg.Vector(
            [i * spacing for i in range(num_electrodes)]
        )

        scheme = ert.createData(
            elecs=electrodes,
            schemeName=array_type
        )

        st.write(f"عدد الأقطاب: {num_electrodes}")
        st.write(f"عدد القياسات: {scheme.size()}")


        mesh = pg.createGrid(
            x=pg.utils.grange(-10, max_x + 10, n=80),
            y=pg.utils.grange(-30, 2, n=30)
        )


        res = []
        for cell in mesh.cells():
            y_center = cell.center()[1]
            if y_center > -depth_interface:
                res.append(float(rho_top))
            else:
                res.append(float(rho_bottom))


        mgr = ert.ERTManager(scheme)
        synth = mgr.simulate(mesh, res=res, verbose=False)

        rhoa = synth["rhoa"]
        st.write(f"نطاق المقاومية الظاهرية: {min(rhoa):.1f} - {max(rhoa):.1f} Ohm.m")

        fig1, ax1 = plt.subplots(figsize=(12, 4))

        pg.show(
            mesh, res, ax=ax1,
            cMin=min(rho_top, rho_bottom),
            cMax=max(rho_top, rho_bottom),
            logScale=True, cMap="jet",
            label="True Resistivity (Ohm.m)"
        )
        ax1.set_title("True Resistivity Model", fontsize=13)
        ax1.set_xlabel("Distance (m)")
        ax1.set_ylabel("Depth (m)")

        st.subheader("النموذج الحقيقي (True Model)")
        st.pyplot(fig1)
        plt.close(fig1)


        fig2, ax2 = plt.subplots(figsize=(12, 4))

        ert.showData(
            synth, ax=ax2,
            cMin=min(rhoa) * 0.8,
            cMax=max(rhoa) * 1.2,
            logScale=True, cMap="jet",
            label="Apparent Resistivity (Ohm.m)"
        )
        ax2.set_title("Simulated Pseudosection", fontsize=13)

        st.subheader("Pseudosection المحسوب (Forward Response)")
        st.pyplot(fig2)
        plt.close(fig2)

        st.success("تمت المحاكاة بنجاح!")