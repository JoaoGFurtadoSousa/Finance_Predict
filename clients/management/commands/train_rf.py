from pathlib import Path
import joblib
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand

from sklearn.ensemble import RandomForestClassifier

from clients.models import Client


class Command(BaseCommand):

    help = "Treina RandomForest para classificar perfil de investidor"

    FEATURES = [
        "tolerancia_volatilidade",
        "aceitacao_perda",
        "experiencia",
        "liquidez",
        "objetivo",
        "horizonte"
    ]

    def handle(self, *args, **kwargs):

        clientes = Client.objects.all()

        if not clientes.exists():
            self.stdout.write(self.style.ERROR("Nenhum cliente encontrado."))
            return

        # =========================
        # ENCODINGS
        # =========================

        experiencia_map = {
            "Nenhuma": 0,
            "Iniciante": 1,
            "Intermediario": 2,
            "Avancado": 3
        }

        liquidez_map = {
            "Imediata": 0,
            "Curto_prazo": 1,
            "Medio_prazo": 2,
            "Longo_prazo": 3
        }

        objetivo_map = {
            "Preservacao": 0,
            "Aposentadoria": 1,
            "Imovel": 2,
            "Viagens": 3,
            "Renda_passiva": 4
        }

        # =========================
        # DATASET
        # =========================

        rows = []

        for c in clientes:

            rows.append({
                "tolerancia_volatilidade": c.tolerancia_volatilidade,
                "aceitacao_perda": c.aceitacao_perda_percentual,
                "experiencia": experiencia_map.get(c.experiencia_em_investimentos, 0),
                "liquidez": liquidez_map.get(c.liquidez_necessaria, 0),
                "objetivo": objetivo_map.get(c.objetivo_de_vida, 0),
                "horizonte": c.tempo_estimado_retorno,
                "target": c.tipo_de_investidor,
            })

        df = pd.DataFrame(rows)

        # =========================
        # LIMPEZA CRÍTICA DO TARGET
        # =========================

        # remove nulos
        df = df.dropna(subset=["target"])

        # remove strings vazias
        df = df[df["target"].astype(str).str.strip() != ""]

        # força string
        df["target"] = df["target"].astype(str)

        # =========================
        # DEBUG IMPORTANTE
        # =========================

        self.stdout.write("\n=== DISTRIBUIÇÃO DAS CLASSES ===")
        self.stdout.write(str(df["target"].value_counts()))

        # validação mínima de classes
        if df["target"].nunique() < 2:
            self.stdout.write(
                self.style.ERROR(
                    "Erro: o dataset precisa de pelo menos 2 classes para treinar."
                )
            )
            return

        # =========================
        # FEATURES E TARGET
        # =========================

        X = df[self.FEATURES]
        y = df["target"]

        # =========================
        # MODELO
        # =========================

        model = RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            random_state=42,
            class_weight="balanced"
        )

        model.fit(X, y)

        # =========================
        # IMPORTÂNCIA DAS FEATURES
        # =========================

        importancias = pd.DataFrame({
            "feature": self.FEATURES,
            "importance": model.feature_importances_
        }).sort_values(by="importance", ascending=False)

        self.stdout.write("\n=== IMPORTÂNCIA DAS FEATURES ===")
        self.stdout.write(str(importancias))

        # =========================
        # SALVAR MODELO
        # =========================

        models_dir = Path(settings.BASE_DIR) / "ml_models"
        models_dir.mkdir(exist_ok=True)

        joblib.dump(model, models_dir / "rf_model.pkl")
        joblib.dump(self.FEATURES, models_dir / "features.pkl")
        joblib.dump({
            "experiencia": experiencia_map,
            "liquidez": liquidez_map,
            "objetivo": objetivo_map
        }, models_dir / "encoders.pkl")

        self.stdout.write(self.style.SUCCESS("\nModelo treinado com sucesso!"))
        self.stdout.write(self.style.SUCCESS(f"Arquivos salvos em: {models_dir}"))