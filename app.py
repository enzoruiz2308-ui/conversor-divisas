"""Conversor de divisas con los tipos de cambio de referencia del BCE."""
import math
import xml.etree.ElementTree as ET

import requests
import streamlit as st

URL_BCE = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
# Namespace por defecto del XML: sin él no se encuentran las etiquetas Cube
NS = {"ecb": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}


# ---------- API ----------
@st.cache_data(ttl=3600)  # guarda el XML 1 hora para no descargarlo en cada clic
def descargar_xml():
    """Hace la petición GET y devuelve el XML en bytes."""
    respuesta = requests.get(URL_BCE, timeout=10)
    respuesta.raise_for_status()  # lanza un error si el código es 4xx o 5xx
    return respuesta.content


# ---------- XML ----------
def parsear_xml(contenido):
    """Devuelve la fecha y un diccionario {moneda: tasa}."""
    raiz = ET.fromstring(contenido)

    # El Cube que tiene el atributo 'time' contiene todas las monedas
    cubo_fecha = raiz.find(".//ecb:Cube[@time]", NS)
    if cubo_fecha is None:
        raise ValueError("El XML no tiene el formato esperado")

    fecha = cubo_fecha.get("time")
    tasas = {"EUR": 1.0}  # el euro es la base y no viene en el XML
    for cubo in cubo_fecha.findall("ecb:Cube", NS):
        tasas[cubo.get("currency")] = float(cubo.get("rate"))

    return fecha, tasas


# ---------- Lógica ----------
def validar_importe(texto):
    """Convierte el texto a número. Lanza ValueError si no es válido."""
    numero = float(texto.strip().replace(",", "."))  # admite coma decimal
    # float() también acepta "nan" e "inf", por eso se comprueba aparte
    if not math.isfinite(numero) or numero < 0:
        raise ValueError("Importe no válido")
    return numero


def convertir(importe, origen, destino, tasas):
    """Conversión cruzada: origen -> EUR -> destino."""
    en_euros = importe / tasas[origen]
    return en_euros * tasas[destino]


# ---------- Interfaz ----------
def main():
    st.set_page_config(page_title="Conversor de Divisas", page_icon="💶")
    st.title("💶 Conversor de Divisas (BCE)")
    st.write("Esta aplicación consume el **XML diario** del Banco Central Europeo.")

    # Carga automática al abrir la aplicación
    try:
        contenido = descargar_xml()
        fecha, tasas = parsear_xml(contenido)
    except requests.RequestException as error:
        st.error(f"Error al conectar con el BCE: {error}")
        st.stop()
    except (ET.ParseError, ValueError) as error:
        st.error(f"Error al procesar el XML: {error}")
        st.stop()

    with st.expander("🔍 Ver estructura XML recibida"):
        st.code(contenido.decode("utf-8"), language="xml")

    st.success(f"✅ Datos cargados. Fecha oficial: **{fecha}**")

    monedas = list(tasas)
    col1, col2, col3 = st.columns(3)
    # Se usa text_input para poder validar nosotros lo que escribe el usuario
    texto = col1.text_input("Cantidad", value="100")
    origen = col2.selectbox("De:", monedas, index=monedas.index("EUR"))
    destino = col3.selectbox(
        "A:", monedas, index=monedas.index("USD") if "USD" in monedas else 0
    )

    if st.button("Calcular conversión", type="primary"):
        try:
            importe = validar_importe(texto)
        except ValueError:
            st.error("Introduce un número válido, igual o mayor que 0.")
        else:
            resultado = convertir(importe, origen, destino, tasas)
            cambio = convertir(1, origen, destino, tasas)
            st.metric(f"Valor en {destino}", f"{resultado:.2f} {destino}")
            st.caption(f"Tipo de cambio: 1 {origen} = {cambio:.4f} {destino}")

    st.divider()
    st.subheader("📊 Tabla de tipos de cambio (base EUR)")
    st.dataframe(
        {"Moneda": monedas, "Tasa": list(tasas.values())},
        hide_index=True,
    )


if __name__ == "__main__":
    main()
