"""Conta gli impianti sportivi mappati in OpenStreetMap per regione (fonte "big data").

Uso: python scripts/scarica_osm.py
Output: data/raw/osm/<data>/<codice_regione>.json   (risposte originali di Overpass, per riproducibilità)
        data/processed/osm_impianti_regioni.csv     (una riga per regione)

Fonte: OpenStreetMap tramite Overpass API (overpass-api.de, con un server alternativo di riserva), dati © OpenStreetMap contributors, licenza ODbL.
Ogni elemento (punto, area o relazione) con il tag indicato conta come un impianto.
Le piscine (leisure=swimming_pool) sono escluse: in OSM sono in gran parte piscine private di case e hotel.
"""
import csv
import json
import subprocess
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = [  # server Overpass pubblici: se il primo è sovraccarico si prova il successivo
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
AGENTE = "BDS-chiara (progetto universitario Big Data for Official Statistics)"

# nomi come nel dataset AVQ -> codice ISO 3166-2 della regione
REGIONI = {
    "Piemonte": "IT-21", "Valle d'Aosta": "IT-23", "Lombardia": "IT-25",
    "Trentino-Alto Adige": "IT-32", "Veneto": "IT-34", "Friuli-Venezia Giulia": "IT-36",
    "Liguria": "IT-42", "Emilia-Romagna": "IT-45", "Toscana": "IT-52", "Umbria": "IT-55",
    "Marche": "IT-57", "Lazio": "IT-62", "Abruzzo": "IT-65", "Molise": "IT-67",
    "Campania": "IT-72", "Puglia": "IT-75", "Basilicata": "IT-77", "Calabria": "IT-78",
    "Sicilia": "IT-82", "Sardegna": "IT-88",
}
# nome della colonna -> tag OSM
CATEGORIE = {
    "campi": "pitch",                 # campi da calcio, tennis, basket, ...
    "centri_sportivi": "sports_centre",
    "palestre": "fitness_centre",
    "stadi": "stadium",
    "piste": "track",                 # piste di atletica, ciclismo, ...
}


def interroga(iso):
    conteggi = "".join(f'nwr["leisure"="{tag}"](area.a);out count;' for tag in CATEGORIE.values())
    query = f'[out:json][timeout:180];area["ISO3166-2"="{iso}"]["admin_level"="4"]->.a;{conteggi}'
    # si usa curl perché il Python di sistema di macOS (LibreSSL) non completa la connessione TLS con Overpass
    for tentativo in range(6):
        server = SERVER[tentativo % len(SERVER)]
        comando = ["curl", "-sS", "--fail", "-m", "240", "-A", AGENTE, "--data-urlencode", f"data={query}", server]
        try:
            return json.loads(subprocess.run(comando, capture_output=True, text=True, check=True).stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as errore:  # 429 / 50x se il server è carico
            attesa = 30 * (tentativo + 1)
            messaggio = str(getattr(errore, "stderr", errore)).strip()[:200]
            print(f"  {iso} ({server.split('/')[2]}): {messaggio}, nuovo tentativo tra {attesa}s", flush=True)
            time.sleep(attesa)
    raise RuntimeError(f"Overpass non risponde per {iso}")


def main():
    oggi = date.today().isoformat()
    cartella = ROOT / "data" / "raw" / "osm" / oggi
    cartella.mkdir(parents=True, exist_ok=True)
    righe = []
    for regione, iso in REGIONI.items():
        file = cartella / f"{iso}.json"
        if not file.exists():  # se lo script si interrompe, riparte dalle regioni mancanti
            file.write_text(json.dumps(interroga(iso), indent=1))
            time.sleep(5)  # rispetto per il server pubblico
        risposta = json.loads(file.read_text())
        totali = [int(e["tags"]["total"]) for e in risposta["elements"]]
        if len(totali) != len(CATEGORIE) or sum(totali) == 0:
            raise ValueError(f"Risposta inattesa per {regione}: {totali}")
        righe.append({"regione": regione, "iso": iso, **dict(zip(CATEGORIE, totali)),
                      "data_osm": risposta["osm3s"]["timestamp_osm_base"]})
        print(f"{regione:22s} " + "  ".join(f"{k}={v}" for k, v in zip(CATEGORIE, totali)), flush=True)

    out = ROOT / "data" / "processed" / "osm_impianti_regioni.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=righe[0].keys())
        w.writeheader()
        w.writerows(righe)
    print(f"\nSalvato {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
