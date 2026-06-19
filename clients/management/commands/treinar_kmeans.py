from pathlib import Path

import joblib
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from clients.models import Client


class Command(BaseCommand):

    help = "Treina o modelo KMeans"

    def handle(self, *args, **kwargs):

        clientes = Client.objects.all()

        if not clientes.exists():
            self.stdout.write(
                self.style.ERROR(
                    "Nenhum cliente encontrado."
                )
            )
            return

        dados = []

        for cliente in clientes:

            dados.append({
                "idade": cliente.idade,
                "renda_atual": float(cliente.renda_atual),
                "aporte_mensal": float(cliente.aporte_mensal),
                "reserva_de_emergencia": int(cliente.reserva_de_emergencia),
                "possui_dividas": int(cliente.possui_dividas),
                "tempo_estimado_retorno": cliente.tempo_estimado_retorno,
                "valor_desejado_acumulado": float(cliente.valor_desejado_acumulado)
            })

        df = pd.DataFrame(dados)

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(df)} clientes encontrados."
            )
        )

        scaler = StandardScaler()

        X = scaler.fit_transform(df)

        kmeans = KMeans(
            n_clusters=3,
            random_state=42,
            n_init=10
        )

        clusters = kmeans.fit_predict(X)

        df["cluster"] = clusters

        medias = (
            df
            .groupby("cluster")
            .mean(numeric_only=True)
        )

        self.stdout.write("\n=== MÉDIAS DOS CLUSTERS ===")
        self.stdout.write(str(medias))

        ranking_clusters = []

        for cluster in medias.index:

            ranking_clusters.append(
                (
                    cluster,
                    medias.loc[
                        cluster,
                        "aporte_mensal"
                    ]
                )
            )

        ranking_clusters.sort(
            key=lambda item: item[1]
        )

        cluster_mapping = {
            ranking_clusters[0][0]: "Conservador",
            ranking_clusters[1][0]: "Moderado",
            ranking_clusters[2][0]: "Agressivo"
        }

        self.stdout.write("\n=== MAPEAMENTO ===")
        self.stdout.write(str(cluster_mapping))

        clientes_list = list(clientes)

        for cliente in clientes_list:

            amostra = [[
                cliente.idade,
                float(cliente.renda_atual),
                float(cliente.aporte_mensal),
                int(cliente.reserva_de_emergencia),
                int(cliente.possui_dividas),
                cliente.tempo_estimado_retorno,
                float(cliente.valor_desejado_acumulado)
            ]]

            amostra = scaler.transform(
                amostra
            )

            cluster = kmeans.predict(
                amostra
            )[0]

            cliente.tipo_de_investidor = (
                cluster_mapping[cluster]
            )

        Client.objects.bulk_update(
            clientes_list,
            ["tipo_de_investidor"]
        )

        models_dir = settings.BASE_DIR / "ml_models"

        models_dir.mkdir(
            exist_ok=True
        )

        self.stdout.write(
            self.style.WARNING(
                f"Salvando modelos em: {models_dir}"
            )
        )

        joblib.dump(
            kmeans,
            models_dir / "kmeans.pkl"
        )

        joblib.dump(
            scaler,
            models_dir / "scaler.pkl"
        )

        joblib.dump(
            cluster_mapping,
            models_dir / "cluster_mapping.pkl"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nModelo treinado com sucesso!"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Arquivos criados em: {models_dir}"
            )
        )