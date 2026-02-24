import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TECO - Calculadora PROINMO", layout="centered")

# --- INYECCIÓN DE ADN VISUAL (iOS Style) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400&family=Poppins:wght@600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        background-color: #eeeeee !important;
    }
    
    h1, h2, h3, .stHeader {
        font-family: 'Poppins', sans-serif !important;
        color: #1e1e1e !important;
    }

    /* Tarjetas Tipo iOS */
    .ios-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        border: 1px solid #f0f0f0;
    }

    /* Botones Naranja TECO Premium */
    div.stButton > button {
        background-color: #ee8c21 !important;
        color: #ffffff !important;
        border: none !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        width: 100%;
        transition: all 0.3s ease;
    }

    /* Input Fields */
    .stNumberInput input {
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
    }

    /* Métricas de Alto Impacto */
    [data-testid="stMetricValue"] {
        font-family: 'Poppins', sans-serif !important;
        color: #ee8c21 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO ---
if 'view' not in st.session_state:
    st.session_state.view = 'calc'

# --- FUNCIONES DE FORMATO ---
def fmt(v): return f"$ {v:,.0f}".replace(",", ".")
def p_fmt(v): return f"{v:.2%}".replace(".", ",")

# --- VISTA: CALCULADORA PRINCIPAL ---
def show_calculator():
    st.image("https://images.squarespace-cdn.com/content/v1/64b564344d32e259e2f6943c/1e07b5a8-4c12-4f1b-9d41-3b79412e873a/Logo+Teco+Negro.png", width=150)
    st.title("Calculadora PROINMO")
    
    tab1, tab2, tab3 = st.tabs(["📋 ENTRADAS", "⚙️ OPERACIÓN", "📊 EVALUACIÓN"])

    with tab1:
        # Bloque 1: Inmueble
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.write("### 🏢 Activo Principal")
        precio_c = st.number_input("Precio de Compra", value=550000000, step=1000000)
        area_c = st.number_input("Área Construida (m2)", value=107, step=1)
        st.markdown('</div>', unsafe_allow_html=True)

        # Bloque 2: Apalancamiento
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.write("### 🔗 Apalancamiento Bancario")
        usa_banco = st.toggle("¿Financiar proyecto?", value=True)
        if usa_banco:
            pct_f = st.slider("% Financiación", 0.0, 0.9, 0.7, 0.05)
            tasa = st.number_input("Tasa Interés Anual (%)", value=12.0)
            plazo = st.number_input("Plazo (Años)", value=20)
        else:
            pct_f, tasa, plazo = 0.0, 0, 0
        st.markdown('</div>', unsafe_allow_html=True)

        # Bloque 3: Transformación
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.write("### 🛠️ Transformación")
        remod_df = st.data_editor(pd.DataFrame({
            "Concepto": ["Demolición", "Obra Nueva"],
            "$/m2": [100000, 2400000],
            "m2": [90, 358]
        }), use_container_width=True)
        
        st.write("**Amoblamiento**")
        col_a1, col_a2 = st.columns(2)
        p_pack = col_a1.number_input("Precio Pack Muebles", value=5000000)
        c_packs = col_a2.number_input("Cantidad Unidades", value=15)
        
        st.write("**Costos Indirectos**")
        pct_ind = st.slider("% Indirectos (ARQ, Licencias, etc.)", 0, 50, 10) / 100
        st.markdown('</div>', unsafe_allow_html=True)

    # --- LÓGICA FINANCIERA INTERNA ---
    notaria = precio_c * 0.025
    v_banco = precio_c * pct_f
    c_inicial = precio_c - v_banco
    costo_obra = (remod_df["$/m2"] * remod_df["m2"]).sum()
    costo_amob = p_pack * c_packs
    v_indirectos = (costo_obra + costo_amob) * pct_ind
    total_remod = costo_obra + costo_amob + v_indirectos
    inversion_cash = c_inicial + notaria + total_remod
    capex_total = precio_c + total_remod + notaria

    with tab2:
        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.write("### 📈 Modelo de Rentas")
        rentas_df = st.data_editor(pd.DataFrame({
            "Unidad": ["Apartamento 1", "Apartamento 2"],
            "Cant": [15, 0],
            "$/Mes": [700000, 0]
        }), use_container_width=True)
        renta_bruta = (rentas_df["Cant"] * rentas_df["$/Mes"]).sum()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="ios-card">', unsafe_allow_html=True)
        st.write("### ⚙️ Escenario Operativo")
        opex_pct = st.select_slider("Gastos Promedio Anual (%)", options=list(range(0, 55, 5)), value=15) / 100
        vac_pct = st.slider("Vacancia (%)", 0, 100, 7) / 100
        val_pct = st.select_slider("Valorización (%)", options=list(range(0, 65, 5)), value=20) / 100
        st.markdown('</div>', unsafe_allow_html=True)

    # --- CÁLCULOS DE SALIDA ---
    gastos_totales = renta_bruta * (opex_pct + vac_pct)
    noi = renta_bruta - gastos_totales
    m_rate = (tasa/100)/12
    n_p = plazo * 12
    cuota = v_banco * (m_rate * (1+m_rate)**n_p) / ((1+m_rate)**n_p - 1) if v_banco > 0 else 0
    cash_flow = noi - cuota
    roi_renta = (cash_flow * 12) / inversion_cash if inversion_cash > 0 else 0
    precio_v = capex_total * (1 + val_pct)
    roi_venta = ((precio_v - capex_total) + (cash_flow * 12)) / inversion_cash if inversion_cash > 0 else 0

    with tab3:
        # HEADER IMPACTANTE
        color_b = "#d1e7dd" if cash_flow > 0 else "#f8d7da"
        st.markdown(f"""
            <div style="background-color:{color_b}; padding:30px; border-radius:20px; text-align:center; border: 1px solid rgba(0,0,0,0.05)">
                <h2 style="margin:0; color:#333">ESTADO DEL PROYECTO</h2>
                <p style="font-size:24px; font-weight:bold">{"FLUJO POSITIVO ✅" if cash_flow > 0 else "FLUJO NEGATIVO ⚠️"}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("CASH NECESARIO", fmt(inversion_cash))
        with c2: st.metric("FLUJO MENSUAL", fmt(cash_flow))
        with c3: st.metric("ROI ANUAL", p_fmt(roi_renta))

        with st.expander("🔍 Ver Análisis de Sensibilidad"):
            st.write("**Escenarios de Vacancia**")
            sens_data = [{"Vacancia": f"{v}%", "Flujo": fmt((renta_bruta*(1-opex_pct-(v/100)))-cuota)} for v in [5, 10, 15, 20]]
            st.table(pd.DataFrame(sens_data))

        st.divider()
        if st.button("⚖️ VALIDAR CON CALIFICACIÓN TECO"):
            st.session_state.results = {
                "calif": "POSITIVA" if (renta_bruta-cuota >=0 and renta_bruta*0.7-cuota >= 0) else "NEGATIVA",
                "roi_r": roi_renta, "roi_v": roi_venta, "rb_pct": renta_bruta/inversion_cash
            }
            st.session_state.view = 'verdict'
            st.rerun()

    # --- FOOTER ---
    st.write("")
    col_l1, col_l2 = st.columns(2)
    with col_l1: 
        if st.button("🔒 Propiedad Intelectual"): st.info("Fórmulas propiedad de Tejido Colectivo.")
    with col_l2:
        if st.button("⚠️ Descargo"): st.warning("Proyecciones no vinculantes.")
    st.markdown("<center><small>© 2026 TEJIDO COLECTIVO | Derechos Reservados</small></center>", unsafe_allow_html=True)

# --- VISTA: VERDICTO FINAL (LIMPIEZA DE PANTALLA) ---
def show_verdict():
    # RITUAL DE CARGA
    placeholder = st.empty()
    with placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.write("## 🛡️ ANALIZANDO VIABILIDAD...")
        bar = st.progress(0)
        frases = ["Analizando normativa urbana...", "Calculando retorno de inversión...", "Validando estándar TECO..."]
        for i in range(100):
            if i % 33 == 0: st.subheader(f"_{frases[i//34]}_")
            bar.progress(i + 1)
            time.sleep(0.08)
    
    placeholder.empty()
    st.balloons()
    
    res = st.session_state.results
    st.markdown(f"""
        <div style="background-color:white; padding:50px; border-radius:30px; border: 6px solid #ee8c21; text-align:center; box-shadow: 0 20px 50px rgba(0,0,0,0.1)">
            <h1 style="color:#ee8c21; font-size:50px">PROYECTO {res['calif']}</h1>
            <hr style="border: 1px solid #f0f0f0">
            <div style="text-align:left; font-size:20px; padding:20px">
                <p><b>Métrica Viable:</b> {"CUMPLE ✅" if res['rb_pct'] >= 0.007 else "BAJA ⚠️"}</p>
                <p><b>Rentabilidad Renta:</b> {p_fmt(res['roi_r'])} Anual</p>
                <p><b>Rentabilidad Capitalización:</b> {p_fmt(res['roi_v'])} (Año 1)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 REALIZAR NUEVO ANÁLISIS"):
        st.session_state.view = 'calc'
        st.rerun()

# --- NAVEGACIÓN ---
if st.session_state.view == 'calc': show_calculator()
else: show_verdict()
