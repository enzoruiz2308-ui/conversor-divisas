# 💶 Conversor de Divisas (BCE)

Aplicación web hecha con Python y Streamlit para convertir divisas con los tipos de cambio de referencia del Banco Central Europeo.

## Funcionalidades
- Descarga automática del XML del BCE al abrir la aplicación (se guarda en caché durante 1 hora)
- Lectura del XML con `xml.etree.ElementTree`
- Conversión cruzada usando el euro como base
- Fecha de actualización de los datos
- Validación del importe introducido
- Gestión de errores de conexión y de lectura del XML
- Tabla de tipos de cambio y vista del XML recibido

## Instalación y ejecución
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fórmula de conversión
`cantidad_final = (importe / tasa_origen) * tasa_destino`

## Fuente de datos
https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml
