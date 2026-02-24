import streamlit as st
import pandas as pd
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO TECO ---
st.set_page_config(page_title="TECO - Calculadora PROINMO", layout="wide", page_icon="🏢")

# Inyección de fuentes Google y Estilo Personalizado
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300&family=Poppins:wght@700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #eeeeee;
        color: #333333;
    }
    
    h1, h2, h3, .stHeader {
        font-family: 'Poppins', sans-serif;
        color: #1e1e1e;
    }
    
    /* Botones Naranja TECO */
    div.stButton > button:first-child {
        background-color: #ee8c21;
        color: white;
        border: none;
        font-weight: bold;
        padding: 10px 24px;
        border-radius: 8px;
    }
    
    /* Campos en Blanco */
    div[data-baseweb="input"] {
        background-color: white !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #ffffff;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    /* Indicadores */
    [data-testid="stMetricValue"] {
        font-size: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE FORMATO ---
def format_currency(value):
    return f"$ {value:,.0f}".replace(",", ".")

def format_percent(value):
    return f"{value:.2%}".replace(".", ",")

# --- LÓGICA DE AMORTIZACIÓN ---
def calc_amortization(principal, annual_rate, years):
    if principal <= 0 or annual_rate <= 0:
        return 0, pd.DataFrame()
    monthly_rate = (annual_rate / 100) / 12
    n_payments = int(years * 12)
    payment = principal * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
    
    data = []
    balance = principal
    for i in range(1, n_payments + 1):
        interest = balance * monthly_rate
        capital = payment - interest
        balance -= capital
        data.append([i, payment, capital, interest, balance])
    
    df = pd.DataFrame(data, columns=["Mes", "Cuota", "Capital", "Interés", "Saldo"])
    return payment, df

# --- PANTALLA PRINCIPAL ---
st.title("🏗️ TECO - Calculadora de Propiedades")
st.caption("Arquitectura Rentable · Consultoría Financiera")

tab1, tab2, tab3 = st.tabs(["📋 1. Entradas", "⚙️ 2. Operación", "📊 3. Evaluación"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos del Inmueble")
        precio_compra = st.number_input("Precio de Compra", value=550000000, step=1000000, format="%d")
        area_construida = st.number_input("Área Construida (m2)", value=107, step=1)
        
        st.divider()
        st.subheader("🔗 Apalancamiento Bancario")
        usa_banco = st.toggle("¿Aplicar financiamiento?", value=True)
        if usa_banco:
            pct_financiar = st.slider("% a Financiar", 0.0, 0.9, 0.7, 0.05)
            tasa_anual = st.number_input("Tasa Interés Anual (%)", value=12.0, step=0.1)
            plazo_anos = st.number_input("Plazo (Años)", value=20, step=1)
        else:
            pct_financiar = 0.0
            tasa_anual = 0.0
            plazo_anos = 0

    with col2:
        st.subheader("Costos Adicionales")
        # Costos Indirectos con detalle en texto
        st.write("**Costos Indirectos** (ARQ, Licencias, Conexiones, Imprevistos)")
        pct_indirectos = st.slider("% Indirectos", 0, 50, 10) / 100
        
        st.divider()
        st.subheader("🛠️ Remodelación y Amoblamiento")
        
        # Tabla Remodelación (Solo Obra)
        remod_data = {
            "Concepto": ["Demolición", "Obra Nueva"],
            "Precio m2": [100000, 2400000],
            "Área": [90, 358]
        }
        df_remod = st.data_editor(pd.DataFrame(remod_data), num_rows="dynamic")
        total_remod_obra = (df_remod["Precio m2"] * df_remod["Área"]).sum()
        
        st.write("**Amoblamiento (Separado)**")
        col_amob1, col_amob2 = st.columns(2)
        precio_amob_unit = col_amob1.number_input("Precio Pack Amoblado", value=5000000)
        cant_amob = col_amob2.number_input("Cantidad Unidades", value=15)
        total_amob = precio_amob_unit * cant_amob

    # Cálculos Internos Base
    gastos_notariales = precio_compra * 0.025
    valor_financiado = precio_compra * pct_financiar
    cuota_inicial = precio_compra - valor_financiado
    costos_indirectos_val = (total_remod_obra + total_amob) * pct_indirectos
    total_remodelacion_full = total_remod_obra + total_amob + costos_indirectos_val
    
    total_invertir_cash = cuota_inicial + gastos_notariales + total_remodelacion_full
    capex_proyecto = precio_compra + total_remodelacion_full + gastos_notariales

with tab2:
    st.header("Análisis de Operación")
    
    col_r1, col_r2 = st.columns([1.5, 1])
    
    with col_r1:
        st.subheader("Modelo de Rentas (Unidades)")
        rentas_data = {
            "Tipo": ["Apartamento 1", "Apartamento 2"],
            "Cantidad": [15, 0],
            "Precio Unitario": [700000, 0]
        }
        df_rentas = st.data_editor(pd.DataFrame(rentas_data), num_rows="dynamic", use_container_width=True)
        renta_bruta_total = (df_rentas["Cantidad"] * df_rentas["Precio Unitario"]).sum()
        
    with col_r2:
        st.metric("Renta Bruta Total", format_currency(renta_bruta_total))
        st.metric("Total Invertir (Caja)", format_currency(total_invertir_cash))

    st.divider()
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        pct_opex = st.select_slider("Gastos Promedio Anual (OPEX %)", options=list(range(0, 55, 5)), value=15) / 100
    with col_s2:
        pct_vacancia = st.slider("Vacancia (%)", 0, 100, 7) / 100
    with col_s3:
        pct_valorizacion = st.select_slider("Valorización Anual (%)", options=list(range(0, 65, 5)), value=20) / 100

    # Cálculos Operativos
    valor_gastos_vacancia = renta_bruta_total * (pct_opex + pct_vacancia)
    noi_mensual = renta_bruta_total - valor_gastos_vacancia
    
    cuota_mensual, df_amort = calc_amortization(valor_financiado, tasa_anual, plazo_anos)
    flujo_caja_mensual = noi_mensual - cuota_mensual

    # --- 1. TERMÓMETRO DE OPORTUNIDAD (Propuesta IA) ---
    st.subheader("🌡️ Termómetro de Oportunidad")
    renta_tradicional = precio_compra * 0.004 # Un estándar de mercado tradicional 0.4%
    comp_data = pd.DataFrame({
        "Modelo": ["Tradicional (0.4%)", "Modelo TECO"],
        "Renta Mensual": [renta_tradicional, renta_bruta_total]
    })
    st.bar_chart(comp_data.set_index("Modelo"), color="#ee8c21")

with tab3:
    st.header("Evaluación y Resultados")
    
    # KPIs Grandes
    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric("Flujo de Caja Mensual", format_currency(flujo_caja_mensual))
        st.metric("Precio de Compra", format_currency(precio_compra))
    with k2:
        st.metric("Flujo de Caja Anual", format_currency(flujo_caja_mensual * 12))
        precio_venta_est = capex_proyecto * (1 + pct_valorizacion)
        st.metric("Precio Venta Est. (Año 1)", format_currency(precio_venta_est))
    with k3:
        roi_neto_anual = (flujo_caja_mensual * 12) / total_invertir_cash if total_invertir_cash > 0 else 0
        st.metric("ROI Rentas Anual (Neto)", format_percent(roi_neto_anual))
        profit_venta = precio_venta_est - capex_proyecto
        roi_venta_1 = (profit_venta + (flujo_caja_mensual * 12)) / total_invertir_cash if total_invertir_cash > 0 else 0
        st.metric("ROI al Vender (Año 1)", format_percent(roi_venta_1))

    st.divider()
    
    # Otros datos solicitados
    c_eval1, c_eval2 = st.columns(2)
    with c_eval1:
        st.write(f"**Valor Renta Bruta:** {format_currency(renta_bruta_total)}")
        st.write(f"**Gastos + Vacancia:** {format_currency(valor_gastos_vacancia)}")
        st.write(f"**Cuota Bancaria:** {format_currency(cuota_mensual)}")
    with c_eval2:
        rent_bruta_mensual = renta_bruta_total / total_invertir_cash if total_invertir_cash > 0 else 0
        st.write(f"**Rentabilidad Bruta Mensual:** {format_percent(rent_bruta_mensual)}")
        st.write(f"**Rentabilidad Bruta Anual:** {format_percent(rent_bruta_mensual * 12)}")

    # --- 2. ANÁLISIS DE SENSIBILIDAD ---
    with st.expander("📉 Ver Análisis de Sensibilidad (Escenarios)"):
        s_data = []
        for v in [0.05, 0.1, 0.2]: # Diferentes niveles de vacancia
            flow = (renta_bruta_total * (1 - pct_opex - v)) - cuota_mensual
            s_data.append([f"{v:.0%}", format_currency(flow)])
        st.table(pd.DataFrame(s_data, columns=["Nivel de Vacancia", "Flujo de Caja Mensual"]))

    # --- BOTONES DE ACCIÓN ---
    st.divider()
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    # 8. BOTÓN CALIFICACIÓN TECO
    if col_btn1.button("⚖️ Obtener Calificación TECO"):
        with st.spinner("Analizando viabilidad bajo el estándar de arquitectura rentable TECO..."):
            time.sleep(8)
            
            # Lógica de Fórmulas
            # 1. Metrica Viable
            if rent_bruta_mensual >= 0.007: mv = "CUMPLE ✅"
            elif 0.004 <= rent_bruta_mensual < 0.007: mv = "BAJA ⚠️"
            else: mv = "MUY BAJA ❌"
            
            # 2. Calificación
            cond1 = (renta_bruta_total - cuota_mensual) >= 0
            cond2 = (renta_bruta_total * 0.7 - cuota_mensual) >= 0
            calif_final = "POSITIVA" if (cond1 and cond2) else "NEGATIVA"
            
            # 3. Rentabilidad Renta
            if calif_final == "NEGATIVA": rr = "NO SIRVE"
            elif roi_neto_anual < 0.04: rr = "MUY BAJA"
            elif 0.04 <= roi_neto_anual < 0.065: rr = "BAJA"
            elif 0.065 <= roi_neto_anual < 0.085: rr = "BUENA"
            elif 0.085 <= roi_neto_anual < 0.11: rr = "ALTA"
            else: rr = "MUY ALTA"
            
            # 4. Rentabilidad Capitalizar
            if calif_final == "NEGATIVA": rc = "NO SIRVE"
            elif roi_venta_1 < 0.06: rc = "MUY BAJA"
            elif 0.06 <= roi_venta_1 < 0.08: rc = "BAJA"
            elif 0.08 <= roi_venta_1 < 0.12: rc = "BUENA"
            else: rc = "ALTA"
            
            st.success(f"### Veredicto TECO: {calif_final}")
            st.info(f"1. **Métrica Viable:** {mv}")
            st.info(f"2. **Rentabilidad Renta:** {rr}")
            st.info(f"3. **Rentabilidad Capitalización (Año 1):** {rc}")

    # 9. BOTÓN PLAN DE PAGOS
    if usa_banco:
        if col_btn2.button("📅 Ver Plan de Pagos"):
            st.write("### Tabla de Amortización")
            st.dataframe(df_amort.style.format({
                "Cuota": "$ {:,.0f}", "Capital": "$ {:,.0f}", 
                "Interés": "$ {:,.0f}", "Saldo": "$ {:,.0f}"
            }))

    # 10. BOTÓN
