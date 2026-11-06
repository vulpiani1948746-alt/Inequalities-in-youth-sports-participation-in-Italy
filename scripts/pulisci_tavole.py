"""Converte le tavole ISTAT "La pratica sportiva in Italia - Anno 2024" in CSV ordinati.

Uso: python scripts/pulisci_tavole.py data/tavole_sport_2024.xls data/clean
Fonte: indagine "I cittadini e il tempo libero" 2024, valori per 100 persone di 3 anni e più.
"""
import sys
from pathlib import Path

import pandas as pd
import xlrd

ETA = ["3-5", "6-10", "11-14", "15-17", "18-19", "20-24", "25-34", "35-44",
       "45-54", "55-59", "60-64", "65-74", "75 e più", "Totale"]
RIPARTIZIONI = {"Nord-ovest", "Nord-est", "Centro", "Sud", "Isole"}
TIPO_COMUNE = {"Comune centro dell'area metropolitana", "Periferia dell'area metropolitana",
               "Fino a 2.000 abitanti", "Da 2.001 a 10.000 abitanti",
               "Da 10.001 a 50.000 abitanti", "50.001 abitanti e più"}
SESSI = ["Maschi", "Femmine", "Totale"]


def righe(sheet):
    for r in range(sheet.nrows):
        yield [c.strip() if isinstance(c, str) else c for c in sheet.row_values(r)]


def per_eta(sheet, indicatori):
    """Tavole con classi di età in riga e blocchi Maschi/Femmine/Totale in colonna."""
    out = []
    for v in righe(sheet):
        if v[0] not in ETA:
            continue
        numeri = [x for x in v[1:] if x != ""]
        for i, ind in enumerate(indicatori):
            for j, sesso in enumerate(SESSI):
                out.append({"eta": v[0], "sesso": sesso, "indicatore": ind,
                            "valore": numeri[i * 3 + j]})
    return pd.DataFrame(out)


def per_territorio(sheet, indicatori):
    """Tavole con regioni, ripartizioni e tipo di comune in riga."""
    out = []
    for v in righe(sheet):
        numeri = [x for x in v[1:] if x != ""]
        if not v[0] or len(numeri) != len(indicatori) or not all(isinstance(x, float) for x in numeri):
            continue
        livello = ("ripartizione" if v[0] in RIPARTIZIONI else
                   "tipo_comune" if v[0] in TIPO_COMUNE else
                   "italia" if v[0] == "Italia" else
                   "provincia_autonoma" if v[0] in ("Bolzano/Bozen", "Trento") else "regione")
        out.append({"territorio": v[0], "livello": livello, **dict(zip(indicatori, numeri))})
    return pd.DataFrame(out)


def motivi(sheet):
    """Tavola 9: motivi per cui non si pratica sport (risposte multiple, righe > 100)."""
    rows = list(righe(sheet))
    header = next(v for v in rows if v[1] == "Mancanza di tempo")
    cols = [c for c in header[1:] if c]
    out, gruppo = [], None
    for v in rows:
        if v[0] in ("SESSO", "CLASSI DI ETÀ", "RIPARTIZIONI GEOGRAFICHE"):
            gruppo = v[0].lower()
            continue
        if gruppo and isinstance(v[1], float):
            for c, x in zip(cols, v[1:]):
                out.append({"gruppo": gruppo, "categoria": v[0], "motivo": c, "valore": x})
    return pd.DataFrame(out)


def main(src, dst):
    wb = xlrd.open_workbook(src)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)

    eta = pd.concat([
        per_eta(wb.sheet_by_name("tavola1"), ["pratica_sport"]),
        per_eta(wb.sheet_by_name("tavola7"), ["ex_praticanti", "mai_praticato"]),
        per_eta(wb.sheet_by_name("tavola10"), ["solo_attivita_fisica", "sedentari"]),
    ])
    eta.to_csv(dst / "sport_per_eta_sesso_2024.csv", index=False)

    terr = (per_territorio(wb.sheet_by_name("tavola2"), ["pratica_sport"])
            .merge(per_territorio(wb.sheet_by_name("tavola8"), ["ex_praticanti", "mai_praticato"]),
                   on=["territorio", "livello"])
            .merge(per_territorio(wb.sheet_by_name("tavola11"), ["solo_attivita_fisica", "sedentari"]),
                   on=["territorio", "livello"]))
    terr.to_csv(dst / "sport_per_territorio_2024.csv", index=False)

    motivi(wb.sheet_by_name("tavola9")).to_csv(dst / "motivi_non_pratica_2024.csv", index=False)

    for f in sorted(dst.glob("*.csv")):
        print(f.name, len(pd.read_csv(f)), "righe")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
