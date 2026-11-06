"""Storico degli impianti sportivi in OpenStreetMap per regione, 2010-2026 (API ohsome).

Uso: python scripts/scarica_ohsome.py
Input:  data/raw/confini_istat/Reg01012025_g/Reg01012025_g_WGS84.shp  (confini regionali ISTAT generalizzati)
Output: data/raw/ohsome/<codice_regione>.json      (risposte originali)
        data/processed/ohsome_impianti_storico.csv (regione, anno, categoria, n_elementi)

ohsome (HeiGIT, https://api.ohsome.org) ricostruisce lo stato di OSM a qualsiasi data passata:
qui si conta, al 1° gennaio di ogni anno, quanti elementi con ciascun tag `leisure` esistevano in ogni regione.
Serve a capire se la crescita degli impianti in OSM riflette nuovi impianti o solo più mappatura.
Dati © OpenStreetMap contributors, licenza ODbL.
"""
import csv
import json
import subprocess
import time
from pathlib import Path

import shapefile
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SHP = ROOT / "data" / "raw" / "confini_istat" / "Reg01012025_g" / "Reg01012025_g_WGS84"
URL = "https://api.ohsome.org/v1/elements/count/groupBy/tag"
CATEGORIE = {"pitch": "campi", "sports_centre": "centri_sportivi", "fitness_centre": "palestre",
             "stadium": "stadi", "track": "piste"}
PERIODO = "2010-01-01/2026-01-01/P1Y"

# i file ISTAT "WGS84" sono in proiezione UTM 32N (EPSG:32632): servono longitudine e latitudine
UTM_A_LONLAT = Transformer.from_crs("EPSG:32632", "EPSG:4326", always_xy=True)


def poligono_lonlat(forma):
    geo = forma.__geo_interface__
    converti = lambda anello: [list(UTM_A_LONLAT.transform(x, y)) for x, y in anello]
    if geo["type"] == "Polygon":
        coords = [converti(a) for a in geo["coordinates"]]
    else:  # MultiPolygon: regioni con isole
        coords = [[converti(a) for a in p] for p in geo["coordinates"]]
    return {"type": geo["type"], "coordinates": coords}


def interroga(nome, geometria, file):
    bpolys = json.dumps({"type": "FeatureCollection", "features": [
        {"type": "Feature", "id": nome, "properties": {}, "geometry": geometria}]})
    file.with_suffix(".geojson").write_text(bpolys)  # curl legge il poligono da file (troppo grande per la riga di comando)
    comando = ["curl", "-sS", "--fail", "-m", "600", "--data-urlencode", f"bpolys@{file.with_suffix('.geojson')}",
               "--data-urlencode", "filter=leisure=*", "--data-urlencode", "groupByKey=leisure",
               "--data-urlencode", "groupByValues=" + ",".join(CATEGORIE),
               "--data-urlencode", f"time={PERIODO}", URL]
    for tentativo in range(4):
        try:
            risposta = json.loads(subprocess.run(comando, capture_output=True, text=True, check=True).stdout)
            file.with_suffix(".geojson").unlink()
            return risposta
        except (subprocess.CalledProcessError, json.JSONDecodeError) as errore:
            attesa = 30 * (tentativo + 1)
            print(f"  {nome}: {str(getattr(errore, 'stderr', errore)).strip()[:200]}, nuovo tentativo tra {attesa}s",
                  flush=True)
            time.sleep(attesa)
    raise RuntimeError(f"ohsome non risponde per {nome}")


def main():
    cartella = ROOT / "data" / "raw" / "ohsome"
    cartella.mkdir(parents=True, exist_ok=True)
    lettore = shapefile.Reader(str(SHP))
    righe = []
    for record, forma in zip(lettore.records(), lettore.shapes()):
        nome, codice = record["DEN_REG"], record["COD_REG"]
        file = cartella / f"{codice:02d}.json"
        if not file.exists():  # se lo script si interrompe, riparte dalle regioni mancanti
            file.write_text(json.dumps(interroga(nome, poligono_lonlat(forma), file), indent=1))
        for gruppo in json.loads(file.read_text())["groupByResult"]:
            tag = gruppo["groupByObject"].split("=")[-1]
            if tag not in CATEGORIE:  # "remainder": altri valori di leisure
                continue
            for punto in gruppo["result"]:
                righe.append({"regione": nome, "anno": int(punto["timestamp"][:4]),
                              "categoria": CATEGORIE[tag], "n_elementi": int(punto["value"])})
        ultimo = {r["categoria"]: r["n_elementi"] for r in righe if r["regione"] == nome and r["anno"] == 2026}
        print(f"{nome:22s} 2026: " + "  ".join(f"{k}={v}" for k, v in ultimo.items()), flush=True)

    out = ROOT / "data" / "processed" / "ohsome_impianti_storico.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=righe[0].keys())
        w.writeheader()
        w.writerows(righe)
    print(f"\nSalvato {out.relative_to(ROOT)} ({len(righe)} righe)")


if __name__ == "__main__":
    main()
