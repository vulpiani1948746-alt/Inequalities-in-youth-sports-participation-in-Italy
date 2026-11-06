"""Unisce i microdati AVQ 2014-2024 (file ad uso pubblico ISTAT) in un unico dataset armonizzato.

Uso: python scripts/costruisci_avq.py
Input:  data/raw/microdati_avq/<anno>/MICRODATI/AVQ_Microdati_<anno>.txt
Output: data/processed/avq_sport_2014_2024.parquet   (una riga per individuo)
        data/processed/avq_sport_2014_2024.csv.gz
        data/processed/controllo_stime_annuali.csv  (stime pesate per verificare il risultato)

Note sui microdati:
- i campi vuoti (" ") indicano "non applicabile" e diventano NA;
- COEFIN è il coefficiente di riporto all'universo moltiplicato per 10.000;
- i nomi di regione e ripartizione cambiano con l'anno (REGMif, REGMiF, REGMF, REGMf);
- titolo_max_famiglia = titolo più alto tra i componenti di 25 anni e più (codice ISTAT minore = titolo più alto);
- REG 444-888 = regione oscurata per riservatezza (resta nota solo la ripartizione), 999 = non disponibile.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "microdati_avq"
OUT = ROOT / "data" / "processed"
ANNI = range(2014, 2025)

# nome armonizzato -> possibili nomi nei file (il primo trovato vince)
VARIABILI = {
    "id_famiglia": ["PROFAM"],
    "id_individuo": ["PROIND"],
    "coefin": ["COEFIN"],
    "sesso": ["SESSO"],
    "eta_classe": ["ETAMi"],
    "regione": ["REGMif", "REGMiF", "REGMF", "REGMf"],
    "ripartizione": ["RIPMif", "RIPMiF", "RIPMF", "RIPMf"],
    "titolo_studio": ["ISTRMi"],
    "condizione": ["CONDMi"],
    "cittadinanza": ["CITTMi"],
    "fonte_reddito": ["REDPRMi"],
    "n_componenti": ["NCOMP"],
    "risorse_economiche": ["RISEC"],
    "spocon": ["SPOCON"],
    "sposal": ["SPOSAL"],
    "attfis": ["ATTFIS"],
    "freq_sport": ["FREQSPO"],
    "ore_sport_sett": ["ORESETSP"],
    "sport_pagamento": ["SPPAG"],
    "corsi_sport": ["SPRIV"],
    "retta_club": ["RETTA"],
    "spettacoli_sportivi": ["SPSPO"],
    "lezioni_recupero": ["LEZPR"],
}

ETA = {1: "0-2", 2: "3-5", 3: "6-10", 4: "11-13", 5: "14-15", 6: "16-17", 7: "18-19",
       8: "20-24", 9: "25-34", 10: "35-44", 11: "45-54", 12: "55-59", 13: "60-64",
       14: "65-74", 15: "75+"}
REGIONI = {10: "Piemonte", 20: "Valle d'Aosta", 30: "Lombardia", 40: "Trentino-Alto Adige",
           50: "Veneto", 60: "Friuli-Venezia Giulia", 70: "Liguria", 80: "Emilia-Romagna",
           90: "Toscana", 100: "Umbria", 110: "Marche", 120: "Lazio", 130: "Abruzzo",
           140: "Molise", 150: "Campania", 160: "Puglia", 170: "Basilicata", 180: "Calabria",
           190: "Sicilia", 200: "Sardegna"}
RIPARTIZIONI = {1: "Nord-ovest", 2: "Nord-est", 3: "Centro", 4: "Sud", 5: "Isole"}
TITOLO = {1: "Laurea e post-laurea", 7: "Diploma", 9: "Licenza media",
          10: "Licenza elementare o nessun titolo"}
CONDIZIONE = {1: "Occupato", 2: "In cerca di occupazione", 3: "Inattivo"}
CITTADINANZA = {1: "Italiana", 3: "Straniera"}
REDDITO = {1: "Lavoro dipendente", 2: "Lavoro autonomo", 3: "Pensione",
           4: "Indennità e provvidenze", 5: "Redditi patrimoniali", 6: "Mantenimento famiglia"}
ATTFIS = {1: "No", 2: "Almeno una volta a settimana", 3: "Almeno una volta al mese",
          4: "Più raramente"}
FREQ = {1: "5+ volte a settimana", 2: "3-4 volte a settimana", 3: "2 volte a settimana",
        4: "1 volta a settimana", 5: "2-3 volte al mese", 6: "1 volta al mese",
        7: "Qualche volta l'anno"}
ORE = {1: "0 ore", 2: "Fino a 2 ore", 3: "2-4 ore", 4: "4-6 ore", 5: "6-10 ore",
       6: "Più di 10 ore"}
SPETTACOLI = {1: "Mai", 2: "1-3 volte", 3: "4-6 volte", 4: "7-12 volte", 5: "Più di 12 volte"}
RISORSE = {1: "Ottime", 2: "Adeguate", 3: "Scarse", 4: "Assolutamente insufficienti"}
LEZPR = {1: "No", 2: "Alcuni mesi", 3: "Alcune settimane d'estate", 4: "Tutto l'anno"}


def leggi_anno(anno):
    path = RAW / str(anno) / "MICRODATI" / f"AVQ_Microdati_{anno}.txt"
    header = pd.read_csv(path, sep="\t", nrows=0, encoding="latin-1").columns.str.strip()
    usecols, rinomina = [], {}
    for nuovo, candidati in VARIABILI.items():
        trovato = next((c for c in candidati if c in header), None)
        if trovato:
            usecols.append(trovato)
            rinomina[trovato] = nuovo
    df = pd.read_csv(path, sep="\t", usecols=usecols, dtype=str, encoding="latin-1")
    df = df.rename(columns=rinomina)
    df = df.apply(lambda s: pd.to_numeric(s.str.strip().replace("", np.nan), errors="coerce"))
    for nuovo in VARIABILI:  # variabile assente in quell'anno -> colonna vuota
        if nuovo not in df:
            df[nuovo] = np.nan
    df.insert(0, "anno", anno)
    return df[["anno", *VARIABILI]]


def sì_no(s):
    return s.map({1: False, 2: True}).astype("boolean")


def categorie(s, mappa, ordinate=False):
    return pd.Categorical(s.map(mappa), categories=list(dict.fromkeys(mappa.values())),
                          ordered=ordinate)


def armonizza(df):
    out = pd.DataFrame({
        "anno": df["anno"].astype("int16"),
        "id_famiglia": df["id_famiglia"].astype("Int64"),
        "id_individuo": df["id_individuo"].astype("Int64"),
        "peso": df["coefin"] / 10_000,
        "sesso": categorie(df["sesso"], {1: "Maschio", 2: "Femmina"}),
        "eta_classe": categorie(df["eta_classe"], ETA, ordinate=True),
        "regione": categorie(df["regione"], REGIONI),
        "ripartizione": categorie(df["ripartizione"], RIPARTIZIONI),
        "titolo_studio": categorie(df["titolo_studio"], TITOLO, ordinate=True),
        "condizione": categorie(df["condizione"], CONDIZIONE),
        "cittadinanza": categorie(df["cittadinanza"], CITTADINANZA),
        "fonte_reddito": categorie(df["fonte_reddito"], REDDITO),
        "n_componenti": df["n_componenti"].astype("Int8"),
        "risorse_economiche": categorie(df["risorse_economiche"], RISORSE, ordinate=True),
        "sport_continuativo": sì_no(df["spocon"]),
        "sport_saltuario": sì_no(df["sposal"]),
        "attivita_fisica": categorie(df["attfis"], ATTFIS),
        "freq_sport": categorie(df["freq_sport"], FREQ, ordinate=True),
        "ore_sport_sett": categorie(df["ore_sport_sett"], ORE, ordinate=True),
        "sport_pagamento": sì_no(df["sport_pagamento"]),
        "corsi_sport": sì_no(df["corsi_sport"]),
        "retta_club": sì_no(df["retta_club"]),
        "spettacoli_sportivi": categorie(df["spettacoli_sportivi"], SPETTACOLI, ordinate=True),
        "lezioni_recupero": categorie(df["lezioni_recupero"], LEZPR),
    })
    # stessa classificazione delle tavole ISTAT: sport > solo attività fisica > sedentario
    cont, salt = out["sport_continuativo"], out["sport_saltuario"]
    pratica = cont.fillna(False) | salt.fillna(False)
    out["pratica_sport"] = pratica.astype("boolean").mask(cont.isna() & salt.isna())
    out["livello_attivita"] = pd.Categorical(
        np.select(
            [cont.fillna(False), salt.fillna(False),
             df["attfis"].isin([2, 3, 4]), df["attfis"].eq(1)],
            ["Sport continuativo", "Sport saltuario", "Solo attività fisica", "Sedentario"],
            default=None),
        categories=["Sport continuativo", "Sport saltuario", "Solo attività fisica", "Sedentario"],
        ordered=True)
    # titolo di studio più alto tra gli adulti (25 anni e più) della stessa famiglia
    adulti = df["eta_classe"].ge(9) & df["titolo_studio"].isin(TITOLO.keys())
    codice_max = (df["titolo_studio"].where(adulti)
                  .groupby([df["anno"], df["id_famiglia"]]).transform("min"))
    out["titolo_max_famiglia"] = categorie(codice_max, TITOLO, ordinate=True)
    return out


def stima_pesata(g, col):
    validi = g[col].notna()
    return np.average(g.loc[validi, col].astype(float), weights=g.loc[validi, "peso"]) * 100


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    dati = pd.concat([armonizza(leggi_anno(a)) for a in ANNI], ignore_index=True)

    dati.to_parquet(OUT / "avq_sport_2014_2024.parquet", index=False)
    dati.to_csv(OUT / "avq_sport_2014_2024.csv.gz", index=False)

    tre_piu = dati[dati["eta_classe"] != "0-2"]
    controllo = tre_piu.groupby("anno").apply(lambda g: pd.Series({
        "n_individui": len(g),
        "popolazione_mln": g["peso"].sum() / 1e6,
        "sport_continuativo_%": stima_pesata(g, "sport_continuativo"),
        "sport_saltuario_%": stima_pesata(g, "sport_saltuario"),
        "pratica_sport_%": stima_pesata(g, "pratica_sport"),
    }), include_groups=False).round(1)
    controllo.to_csv(OUT / "controllo_stime_annuali.csv")

    print(f"{len(dati):,} individui, {dati.shape[1]} colonne")
    print(controllo.to_string())
    print("\nValori mancanti per colonna (%):")
    print((dati.isna().groupby(dati["anno"]).mean() * 100).round(0).T.to_string())


if __name__ == "__main__":
    main()
