from pathlib import Path

import joblib

from django.conf import settings


MODELS_DIR = settings.BASE_DIR / "ml_models"


def carregar_modelos():

    kmeans_path = MODELS_DIR / "kmeans.pkl"
    scaler_path = MODELS_DIR / "scaler.pkl"
    mapping_path = MODELS_DIR / "cluster_mapping.pkl"

    arquivos_faltando = []

    if not kmeans_path.exists():
        arquivos_faltando.append("kmeans.pkl")

    if not scaler_path.exists():
        arquivos_faltando.append("scaler.pkl")

    if not mapping_path.exists():
        arquivos_faltando.append("cluster_mapping.pkl")

    if arquivos_faltando:

        raise FileNotFoundError(
            (
                "Modelos não encontrados: "
                f"{', '.join(arquivos_faltando)}.\n"
                "Execute primeiro:\n"
                "python manage.py treinar_kmeans"
            )
        )

    kmeans = joblib.load(kmeans_path)
    scaler = joblib.load(scaler_path)
    cluster_mapping = joblib.load(mapping_path)

    return (
        kmeans,
        scaler,
        cluster_mapping
    )


def classificar_cliente(cliente):

    (
        kmeans,
        scaler,
        cluster_mapping
    ) = carregar_modelos()

    amostra = [[
        cliente.idade,
        float(cliente.renda_atual),
        float(cliente.aporte_mensal),
        int(cliente.reserva_de_emergencia),
        int(cliente.possui_dividas),
        cliente.tempo_estimado_retorno,
        float(cliente.valor_desejado_acumulado)
    ]]

    amostra_normalizada = scaler.transform(
        amostra
    )

    cluster = kmeans.predict(
        amostra_normalizada
    )[0]

    return cluster_mapping[
        cluster
    ]