import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import re
from io import StringIO
import numpy as np

# Configuración estética
plt.style.use('seaborn')
sns.set_palette("husl")
COLORES = ['#3498db', '#e74c3c']


def limpiar_y_procesar(archivo):
    """Limpia y procesa archivos CSV con formato especial"""
    with open(archivo, 'r') as f:
        contenido = f.read()

    # Procesamiento especial para tu formato
    lineas_limpias = []
    for linea in contenido.split('\n'):
        # Eliminar corchetes y comillas
        linea_limpia = re.sub(r"[\[\]']", "", linea)
        # Dividir por comas y tomar solo los primeros 5 elementos
        elementos = [elem.strip() for elem in linea_limpia.split(',') if elem.strip()]
        if len(elementos) >= 5:  # Asegurarnos que tenga las columnas necesarias
            lineas_limpias.append(','.join(elementos[:5]))

    return '\n'.join(lineas_limpias)


def cargar_datos(patron):
    archivos = glob.glob(patron)
    if not archivos:
        print(f"No se encontraron archivos para: {patron}")
        return None

    datos = []
    for archivo in archivos:
        try:
            contenido_limpio = limpiar_y_procesar(archivo)
            # Leer con pandas usando solo las columnas necesarias
            df = pd.read_csv(
                StringIO(contenido_limpio),
                header=None,
                names=["Pasajero", "tiempo_espera", "tiempo_viaje", "tiempo_transbordo", "tiempo_total"],
                usecols=[0, 1, 2, 3, 4]
            )
            datos.append(df)
        except Exception as e:
            print(f"Error procesando {archivo}: {str(e)}")
            continue

    return pd.concat(datos, ignore_index=True) if datos else None


def generar_comparacion():
    print("Procesando archivos básicos...")
    df_basico = cargar_datos("results/basico_*.csv")

    print("\nProcesando archivos BDI...")
    df_bdi = cargar_datos("results/bdi_*.csv")

    if df_basico is None or df_bdi is None:
        print("\nError: No se pudieron cargar todos los datos necesarios")
        return

    # Convertir a numérico
    cols_numericas = ["tiempo_espera", "tiempo_viaje", "tiempo_transbordo", "tiempo_total"]
    df_basico[cols_numericas] = df_basico[cols_numericas].apply(pd.to_numeric, errors='coerce')
    df_bdi[cols_numericas] = df_bdi[cols_numericas].apply(pd.to_numeric, errors='coerce')

    # Análisis comparativo
    analisis = pd.DataFrame({
        'Métrica': [
            'Tiempo medio de espera',
            'Tiempo medio de viaje',
            'Tiempo medio total',
            '% con transbordo',
            'Máximo tiempo total'
        ],
        'Básico': [
            df_basico['tiempo_espera'].mean(),
            df_basico['tiempo_viaje'].mean(),
            df_basico['tiempo_total'].mean(),
            (df_basico['tiempo_transbordo'] > 0).mean() * 100,
            df_basico['tiempo_total'].max()
        ],
        'BDI': [
            df_bdi['tiempo_espera'].mean(),
            df_bdi['tiempo_viaje'].mean(),
            df_bdi['tiempo_total'].mean(),
            (df_bdi['tiempo_transbordo'] > 0).mean() * 100,
            df_bdi['tiempo_total'].max()
        ]
    })

    # Calcular diferencia porcentual
    analisis['Diferencia (%)'] = round(
        (analisis['BDI'] - analisis['Básico']) / analisis['Básico'] * 100, 2)

    print("\nResultado del análisis comparativo:")
    print(analisis)

    # Guardar resultados
    analisis.to_csv("results/comparacion_final.csv", index=False)
    print("\nResultados guardados en: results/comparacion_final.csv")


def generar_graficos(df_basico, df_bdi):
    """Genera todos los gráficos comparativos"""
    fig, axs = plt.subplots(3, 2, figsize=(18, 18))

    # 1. Comparación de distribuciones (Boxplot)
    datos_espera = pd.concat([
        df_basico['tiempo_espera'].rename('Básico'),
        df_bdi['tiempo_espera'].rename('BDI')
    ], axis=1)

    sns.boxplot(data=datos_espera, ax=axs[0, 0], width=0.6)
    axs[0, 0].set_title('Distribución Tiempos de Espera')
    axs[0, 0].set_ylabel('Segundos')

    # 2. Comparación de tiempos totales (KDE)
    sns.kdeplot(df_basico['tiempo_total'], label='Básico', ax=axs[0, 1], fill=True, alpha=0.3)
    sns.kdeplot(df_bdi['tiempo_total'], label='BDI', ax=axs[0, 1], fill=True, alpha=0.3)
    axs[0, 1].set_title('Distribución Tiempos Totales')
    axs[0, 1].set_xlabel('Segundos')
    axs[0, 1].legend()

    # 3. Porcentaje con transbordo (Barras)
    transbordo_data = pd.DataFrame({
        'Modelo': ['Básico', 'BDI'],
        'Porcentaje': [
            (df_basico['tiempo_transbordo'] > 0).mean() * 100,
            (df_bdi['tiempo_transbordo'] > 0).mean() * 100
        ]
    })
    sns.barplot(x='Modelo', y='Porcentaje', data=transbordo_data, ax=axs[1, 0])
    axs[1, 0].set_title('Porcentaje de Pasajeros con Transbordo')
    axs[1, 0].set_ylim(0, 100)

    # 4. Relación espera-viaje (Scatter)
    axs[1, 1].scatter(df_basico['tiempo_espera'], df_basico['tiempo_viaje'], alpha=0.5, label='Básico')
    axs[1, 1].scatter(df_bdi['tiempo_espera'], df_bdi['tiempo_viaje'], alpha=0.5, label='BDI')
    axs[1, 1].set_title('Relación Tiempo Espera vs Tiempo Viaje')
    axs[1, 1].set_xlabel('Tiempo Espera (s)')
    axs[1, 1].set_ylabel('Tiempo Viaje (s)')
    axs[1, 1].legend()

    # 5. Comparación de percentiles (Lineplot)
    percentiles = np.arange(0, 100, 5)
    axs[2, 0].plot(
        percentiles,
        np.percentile(df_basico['tiempo_total'], percentiles),
        label='Básico', marker='o'
    )
    axs[2, 0].plot(
        percentiles,
        np.percentile(df_bdi['tiempo_total'], percentiles),
        label='BDI', marker='o'
    )
    axs[2, 0].set_title('Percentiles de Tiempo Total')
    axs[2, 0].set_xlabel('Percentil')
    axs[2, 0].set_ylabel('Tiempo (s)')
    axs[2, 0].legend()
    axs[2, 0].grid(True)

    # 6. Diferencia de medias (Barras horizontales)
    metricas = ['tiempo_espera', 'tiempo_viaje', 'tiempo_total']
    diferencias = {
        'Métrica': metricas,
        'Diferencia (BDI - Básico)': [
            df_bdi[metrica].mean() - df_basico[metrica].mean()
            for metrica in metricas
        ]
    }
    sns.barplot(
        x='Diferencia (BDI - Básico)',
        y='Métrica',
        data=pd.DataFrame(diferencias),
        ax=axs[2, 1]
    )
    axs[2, 1].set_title('Diferencia de Medias entre Modelos')
    axs[2, 1].axvline(0, color='gray', linestyle='--')

    plt.tight_layout()
    plt.savefig('results/comparacion_graficos.png', dpi=300, bbox_inches='tight')
    plt.close()


def calcular_metricas_avanzadas(df_basico, df_bdi):
    """Calcula métricas adicionales para la comparación"""
    metricas = {
        # Eficiencia del sistema
        'Eficiencia global (viaje/espera)': {
            'Básico': df_basico['tiempo_viaje'].sum() / df_basico['tiempo_espera'].sum(),
            'BDI': df_bdi['tiempo_viaje'].sum() / df_bdi['tiempo_espera'].sum()
        },

        # Consistencia
        'Desviación estándar tiempo total': {
            'Básico': df_basico['tiempo_total'].std(),
            'BDI': df_bdi['tiempo_total'].std()
        },

        # Equidad (variabilidad entre pasajeros)
        'Coeficiente de variación tiempo total': {
            'Básico': df_basico['tiempo_total'].std() / df_basico['tiempo_total'].mean(),
            'BDI': df_bdi['tiempo_total'].std() / df_bdi['tiempo_total'].mean()
        },

        # Robustez (outliers)
        'Porcentaje > 2x media total': {
            'Básico': (df_basico['tiempo_total'] > 2 * df_basico['tiempo_total'].mean()).mean() * 100,
            'BDI': (df_bdi['tiempo_total'] > 2 * df_bdi['tiempo_total'].mean()).mean() * 100
        }
    }

    return pd.DataFrame(metricas).T


def generar_reporte_completo(df_basico, df_bdi):
    """Genera todos los outputs del análisis"""
    # 1. Métricas básicas
    metricas_basicas = pd.DataFrame({
        'Métrica': [
            'Media tiempo espera (s)',
            'Media tiempo viaje (s)',
            'Media tiempo total (s)',
            'Mediana tiempo total (s)',
            '% con transbordo',
            'Media tiempo transbordo (s) | solo quienes transbordan'
        ],
        'Básico': [
            df_basico['tiempo_espera'].mean(),
            df_basico['tiempo_viaje'].mean(),
            df_basico['tiempo_total'].mean(),
            df_basico['tiempo_total'].median(),
            (df_basico['tiempo_transbordo'] > 0).mean() * 100,
            df_basico[df_basico['tiempo_transbordo'] > 0]['tiempo_transbordo'].mean()
        ],
        'BDI': [
            df_bdi['tiempo_espera'].mean(),
            df_bdi['tiempo_viaje'].mean(),
            df_bdi['tiempo_total'].mean(),
            df_bdi['tiempo_total'].median(),
            (df_bdi['tiempo_transbordo'] > 0).mean() * 100,
            df_bdi[df_bdi['tiempo_transbordo'] > 0]['tiempo_transbordo'].mean()
        ]
    })

    # 2. Métricas avanzadas
    metricas_avanzadas = calcular_metricas_avanzadas(df_basico, df_bdi)

    # 3. Exportar a Excel con múltiples hojas
    with pd.ExcelWriter('results/reporte_comparativo.xlsx') as writer:
        metricas_basicas.to_excel(writer, sheet_name='Métricas Básicas', index=False)
        metricas_avanzadas.to_excel(writer, sheet_name='Métricas Avanzadas')

        # Exportar percentiles
        pd.DataFrame({
            'Percentil': np.arange(0, 101, 5),
            'Básico': np.percentile(df_basico['tiempo_total'], np.arange(0, 101, 5)),
            'BDI': np.percentile(df_bdi['tiempo_total'], np.arange(0, 101, 5))
        }).to_excel(writer, sheet_name='Percentiles', index=False)

    # 4. Generar gráficos
    generar_graficos(df_basico, df_bdi)

    print("Análisis completado. Resultados guardados en:")
    print("- results/reporte_comparativo.xlsx")
    print("- results/comparacion_graficos.png")


if __name__ == "__main__":
    # Cargar datos (usando la función de procesamiento anterior)
    df_basico = cargar_datos("results/basico_*.csv")
    df_bdi = cargar_datos("results/bdi_*.csv")

    if df_basico is not None and df_bdi is not None:
        # Convertir a numérico
        cols_numericas = ["tiempo_espera", "tiempo_viaje", "tiempo_transbordo", "tiempo_total"]
        df_basico[cols_numericas] = df_basico[cols_numericas].apply(pd.to_numeric, errors='coerce')
        df_bdi[cols_numericas] = df_bdi[cols_numericas].apply(pd.to_numeric, errors='coerce')

        # Generar reporte completo
        generar_reporte_completo(df_basico, df_bdi)
    else:
        print("Error: No se pudieron cargar todos los datos necesarios")
