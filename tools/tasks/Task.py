from datetime import date, datetime, time, timedelta
from typing import Optional

from pydantic import BaseModel, Field, create_model


class Task:

    @staticmethod
    def get_views():
        return {
            "Bpm de Proyecto": [
                ("Cliente", "CLIENTE_DS"),
                ("Institución", "INSTITUCION_DS"),
                ("Oportunidad", "OPORTUNIDAD_DS"),
                ("Código del Proyecto", "CODIGOPEDIDO_CD"),
                ("Tipo de Proyecto", "TIPOPROYECTO_DS"),
                ("Administrador", "ADMINISTRADOR_DS"),
                ("Estado", "IBPME_SITUACION_PROC_DS"),
                ("Importe Previsto (€)", "IMPORTEPREVISTO_NM"),
                ("Importe Total (€)", "IMPORTE_NM"),
                ("Descripción breve", "PEDIDO_DS"),
            ],
            "Proceso de Oportunidades": [
                ("Nombre", "OPORTUNIDAD_DS"),
                ("Código", "DEAL_CD"),
                ("Institución", "INSTITUCION_DS"),
                ("Cliente", "CLIENTE_DS"),
                ("Importe estimado", "IMPORTEESTIMADO_NM"),
                ("Descripción breve", "RESUMEN_DS"),
                ("Estado", "ESTADO_DS"),
                ("Fecha de alta", "ALTA_DT"),
            ],
        }

    @staticmethod
    def get_all_views_concepts() -> list[tuple[str, str]]:
        res = []
        views = Task.get_views()
        for value in views.values():
            res.extend(value)
        return res

    @staticmethod
    def get_all_filters() -> type[BaseModel]:
        # _DS, _CD are text fields -> add one field
        # _NM are number fields -> add two: min and max
        # _DT are date fields -> add two: min and max
        concepts = Task.get_all_views_concepts()
        fields = {}
        for _, field_name in concepts:
            if field_name.endswith("_DS") or field_name.endswith("_CD"):
                fields[field_name] = (Optional[str], None)
            elif field_name.endswith("_NM"):
                fields[field_name + "_min"] = (Optional[int], None)
                fields[field_name + "_max"] = (Optional[int], None)
            elif field_name.endswith("_DT"):
                fields[field_name + "_min"] = (Optional[date], None)
                fields[field_name + "_max"] = (Optional[date], None)
            else:
                raise ValueError(f"Unknown field type for {field_name}")
        return create_model("Filters", **fields)

    @staticmethod
    def get_view_from_concept(
        concept_name: str,
    ) -> Optional[list[tuple[str, str]]]:
        return Task.get_views().get(concept_name)
