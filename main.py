import streamlit as st
import pandas as pd
import numpy as np

# Configuración de la página
st.set_page_config(page_title="TECO - Calculadora PROINMO", layout="wide")

# Estilo personalizado para que se vea premium
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1, h2, h3 { color: #1e1e1e; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ TECO - Calculadora de Propiedades")
st.subheader("Análisis de Arquitectura Rentable")

# --- SIDEBAR: PARÁMETROS FINANCIEROS GLOBALES ---
with st.sidebar:
    st.header("⚙️ Configuración Bancaria")
    tasa_anual = st.number_input("Tasa de Interés Anual (%)", value=12.0, step=0.1) / 100
    plazo_anos = st.number_input("Plazo del Crédito (Años)", value=20, step=1)
    valorizacion_anual = st.slider("% Valorización Estimada (1 año)", 0, 50, 30) / 100
    
    st.divider()
    st.info("Desarrollado por TECO (Tejido Colectivo)")

# --- COLUMNAS PRINCIPALES ---
col_inv, col_renta = st.columns([1, 1])

with col_inv:
    st.header("💰 Inversión y CAPEX")
    
    # Datos del Inmueble
    precio_compra = st.number_input("Precio de Compra (COP)", value=550000000, step=1000000)
    area_total = st.number_input("Área Construida (m2)", value=107, step=1)
    porcentaje_financiado = st.slider("% a Financiar", 0.0, 1.0, 0.7)
    pct_gastos_notariales = st.number_input("% Gastos Notariales", value=2.5) / 100

    # Cálculos Financieros
    valor_financiado = precio_compra * porcentaje_financiado
    cuota_inicial = precio_compra - valor_financiado
    gastos_notariales = precio_compra * pct_gastos_notariales

    st.subheader("🛠️ Presupuesto de Remodelación")
    
    # Tabla de Remodelación
    remod_data = {
        "Concepto": ["Demolición", "Obra Nueva", "Amoblamiento"],
        "Precio m2": [100000, 2400000, 5000000],
        "Área": [90, 358, 0]
    }
    df_remod = st.data_editor(pd.DataFrame(remod_data), num_rows="dynamic")
    
    costo_remod_total = (df_remod["Precio m2"] * df_remod["Área"]).sum()
    costos_indirectos = costo_remod_total * 0.07
    total_invertir = cuota_inicial + gastos_notariales + costo_remod_total + costos_indirectos

with col_renta:
    st.header("📈 Modelo de Rentas")
    
    # Tabla de Unidades
    rentas_data = {
        "Tipo": ["Apartamento 1", "Apartamento 2"],
        "Cantidad": [15, 0],
        "Precio Unitario": [700000, 0]
    }
    df_rentas = st.data_editor(pd.DataFrame(rentas_data), num_rows="dynamic")
    
    renta_bruta_mensual = (df_rentas["Cantidad"] * df_rentas["Precio Unitario"]).sum()
    
    # Gastos Operativos
    pct_opex = st.slider("% Gastos Operativos (Adm, Mtto)", 0, 50, 15) / 100
    pct_vacancia = st.slider("% Vacancia Estimada", 0, 20, 7) / 100
    
    noi_mensual = renta_bruta_mensual * (1 - pct_opex - pct_vacancia)

# --- CÁLCULO DE CUOTA BANCARIA (SISTEMA FRANCÉS) ---
tasa_mensual = tasa_anual / 12
n_pagos = plazo_anos * 12
if valor_financiado > 0:
    cuota_banco = valor_financiado * (tasa_mensual * (1 + tasa_mensual)**n_pagos) / ((1 + tasa_mensual)**n_pagos - 1)
else:
    cuota_banco = 0

# --- DASHBOARD DE RESULTADOS ---
st.divider()
st.header("📊 Resultados del Proyecto")

c1, c2, c3, c4 = st.columns(4)

cash_flow_mensual = noi_mensual - cuota_banco
roe_anual = (cash_flow_mensual * 12) / total_invertir if total_invertir > 0 else 0
precio_venta_est = total_invertir * (1 + valorizacion_anual)

with c1:
    st.metric("Inversión Inicial (Cash)", f"${total_invertir:,.0f}")
with c2:
    st.metric("Flujo de Caja Mensual", f"${cash_flow_mensual:,.0f}", delta=f"{noi_mensual:,.0f} NOI")
with c3:
    st.metric("ROE (Rentabilidad Anual)", f"{roe_anual:.2%}")
with c4:
    st.metric("Venta Estimada (1 año)", f"${precio_venta_est:,.0f}")

# Gráfico simple de distribución de costos
st.divider()
st.subheader("Distribución de Inversión")
chart_data = pd.DataFrame({
    "Categoría": ["Cuota Inicial", "Remodelación", "Gastos Legales"],
    "Monto": [cuota_inicial, costo_remod_total + costos_indirectos, gastos_notariales]
})
st.bar_chart(chart_data.set_index("Categoría"))

st.caption("Nota: Los resultados son estimaciones basadas en los inputs proporcionados. TECO no se hace responsable por decisiones de inversión.")
