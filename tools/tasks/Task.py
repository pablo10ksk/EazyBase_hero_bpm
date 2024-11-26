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
                # ("Fecha de alta", "ALTA_DT"),
            ],
        }

    @staticmethod
    def get_view_from_concept(
        concept_name: str | None,
    ) -> list[tuple[str, str]]:
        res = Task.get_views().get(concept_name, []) if concept_name is not None else []

        task_view = [
            ("Nombre de la tarea", "TAREA_DS"),
            ("Nombre de tarea actual", "currTask"),
            ("Nombre de fase actual", "currPhase"),
        ]
        res.extend(task_view)
        return res
