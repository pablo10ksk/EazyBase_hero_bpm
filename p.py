# Archivo provisional para transformar un doKeenMagic a
# un prompt (más adelante debería transformarse a un json schema...)

r = {
    "data": [
        {
            "controltype": "C",
            "options": ["4065$< 1.000 euros", "4066$> 1.000 euros"],
            "tag": "IMPORTE_ANTICIPO_CD",
            "tipodescri": "168",
            "title": "Importe anticipo",
        },
        {
            "controltype": "C",
            "options": [
                "796$01 - Enero",
                "797$02 - Febrero",
                "798$03 - Marzo",
                "799$04 - Abril",
                "800$05 - Mayo",
                "801$06 - Junio",
                "802$07 - Julio",
                "803$08 - Agosto",
                "804$09 - Septiembre",
                "805$10 - Octubre",
                "806$11 - Noviembre",
                "807$12 - Diciembre",
            ],
            "tag": "MONTH_CD",
            "tipodescri": "86",
            "title": "Mes",
        },
        {
            "controltype": "N",
            "options": [],
            "tag": "YEAR_NM",
            "tipodescri": "85",
            "title": "Año",
        },
        {
            "controltype": "Per",
            "options": [],
            "tag": "EMPLEADO",
            "tipodescri": "39",
            "title": "Empleado",
        },
        {
            "controltype": "C",
            "options": [
                "113$A CORUÑA",
                "95$ALICANTE",
                "711$BADAJOZ",
                "513$BARCELONA",
                "29964$BARCELONA BICING",
                "512$BARCELONA Transporte",
                "570$BILBAO",
                "670$CORDOBA",
                "691$GIJON",
                "112$GRANADA",
                "712$JEREZ",
                "115$MADRID",
                "632$MADRID CONSORCIO (CAM)",
                "488978$MADRID WELLINGTON",
                "671$MALAGA",
                "692$OVIEDO",
                "488976$SANTANDER",
                "100$SERVICIOS CENTRALES",
                "713$SEVILLA",
                "4167$TODAS",
                "130$VALENCIA",
                "137$VALLADOLID",
                "135$VIGO",
                "140$ZARAGOZA",
                "25002$ZARAGOZA SMARTBIKE",
            ],
            "tag": "Sucursal",
            "tipodescri": "20",
            "title": "Sucursal",
        },
        {
            "controltype": "C",
            "options": [
                "23653$Direccion General",
                "767$Dpto. Comercial",
                "768$Dpto. Desarrollo",
                "771$Dpto. Finanzas",
                "508584$Dpto. Legal",
                "3165$Dpto. Marketing",
                "8776$Dpto. Nuevos Proyectos",
                "766$Dpto. Operaciones y Calidad",
                "769$Dpto. Organizacion",
                "16833$Dpto. Patrimonio y Oferta",
                "770$Dpto. Presidencia",
                "499046$Dpto. RRHH",
                "3163$Dpto. Sistemas",
                "23651$Dpto. Smartbike",
                "25088$Dpto. Venta Local",
            ],
            "tag": "Departamento",
            "tipodescri": "57",
            "title": "Depto Solicitante",
        },
    ]
}

r = r["data"]
for d in r:
    name = d["tag"]
    opciones = d["options"]
    ops = []
    for op in opciones:
        k = ""
        if "$" in op:
            ops.append(op.split("$")[1].strip())
        else:
            ops.append(op.strip())

    ops = [f"'{o}'" for o in ops]
    if ops:
        print(f"- **{name}**: " + ", ".join(ops))
    else:
        print(f"- **{name}**.")
