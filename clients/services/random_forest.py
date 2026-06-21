import joblib
import pandas as pd
from pathlib import Path
from django.conf import settings


class InvestorPredictor:

    def __init__(self):

        base = Path(settings.BASE_DIR) / "ml_models"

        self.model = joblib.load(base / "rf_model.pkl")
        self.features = joblib.load(base / "features.pkl")
        self.encoders = joblib.load(base / "encoders.pkl")

    def _build_dataframe(self, cliente):

        exp_map = self.encoders["experiencia"]
        liq_map = self.encoders["liquidez"]
        obj_map = self.encoders["objetivo"]

        return pd.DataFrame([{
            "tolerancia_volatilidade": cliente.tolerancia_volatilidade,
            "aceitacao_perda": cliente.aceitacao_perda_percentual,
            "experiencia": exp_map.get(cliente.experiencia_em_investimentos, 0),
            "liquidez": liq_map.get(cliente.liquidez_necessaria, 0),
            "objetivo": obj_map.get(cliente.objetivo_de_vida, 0),
            "horizonte": cliente.tempo_estimado_retorno,
        }])

    # =========================
    # USADO NO SIGNAL (OBRIGATÓRIO)
    # =========================
    def predict(self, cliente):
        df = self._build_dataframe(cliente)
        return self.model.predict(df[self.features])[0]

    # =========================
    # OPCIONAL (DEBUG / API)
    # =========================
    def predict_proba(self, cliente):
        df = self._build_dataframe(cliente)

        proba = self.model.predict_proba(df[self.features])[0]

        return {
            self.model.classes_[i]: float(proba[i])
            for i in range(len(proba))
        }