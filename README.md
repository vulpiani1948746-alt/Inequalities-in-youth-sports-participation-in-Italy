---
corso: Big Data for Official Statistics
tema: Vita quotidiana – pratica sportiva in Italia
titolo: "Inequalities in Youth Sports Participation in Italy: Gender, Family Background and Territory"
creato: 2026-10-19
---

# Inequalities in Youth Sports Participation in Italy: Gender, Family Background and Territory

Progetto per *Big Data for Official Statistics*: tema "vita quotidiana", fonte ISTAT.

## Domanda di ricerca (bozza)
Chi pratica sport in Italia, chi smette e perché? Divari per età, sesso, territorio e titolo di studio, con attenzione ai giovani (11-24 anni) e al ruolo di studio/scuola.

> Nota: ISTAT non misura la "rigidità della scuola". L'indicatore più vicino è il motivo "mancanza di tempo" (tavole). Nei microdati AVQ non c'è una variabile "studente" (`CONDMi` = occupato / in cerca / inattivo); possibili proxy: età scolare, `LEZPR` (lezioni private di recupero scolastico), `HHSCLA`/`MMSCLA` (tempo per andare a scuola o al lavoro).

## Struttura della cartella
```
BDS-chiara/
├── README.md                     ← questa nota
├── Valutazione qualità delle fonti.md ← griglia della qualità ISTAT vs OSM (schema del corso)
├── data/
│   ├── tavole_sport_2024.xls     ← tavole ISTAT "La pratica sportiva in Italia 2024"
│   ├── pratica_sportiva_2024.pdf ← report + nota metodologica
│   ├── clean/                    ← CSV ordinati ricavati dalle tavole
│   └── raw/
│       ├── microdati_avq/<anno>/ ← microdati AVQ (file ad uso pubblico)
│       ├── osm/<data>/           ← risposte originali di Overpass, una per regione
│       ├── ohsome/               ← risposte originali di ohsome, una per regione
│       └── confini_istat/        ← confini regionali ISTAT 2025 (generalizzati, UTM 32N)
│   └── processed/                ← dataset AVQ armonizzato 2014-2024
├── notebooks/
│   ├── 01_analisi_esplorativa.ipynb ← stime pesate e grafici
│   ├── 02_regressione_logistica.ipynb ← modelli logistici pesati
│   ├── 03_osm_impianti.ipynb      ← impianti OpenStreetMap vs pratica sportiva, storico OSM
│   └── 04_machine_learning.ipynb  ← random forest vs logistica, clustering delle regioni
├── figures/                      ← grafici PNG generati dal notebook
├── results/                      ← tabelle CSV generate dal notebook
├── requirements.txt              ← pacchetti Python
└── scripts/
    ├── pulisci_tavole.py         ← tavole .xls → CSV in data/clean
    ├── costruisci_avq.py         ← microdati AVQ 2014-2024 → data/processed
    ├── scarica_osm.py            ← conteggi impianti OSM per regione, oggi (Overpass API)
    ├── scarica_ohsome.py         ← storico impianti OSM per regione 2010-2026 (API ohsome)
    └── figure_inglese.py         ← grafici in inglese per le slide → figures/en/
```

## Fonti

### 1. Tavole aggregate 2024
- ISTAT, *La pratica sportiva in Italia – Anno 2024* (30/06/2025), indagine "I cittadini e il tempo libero".
- [Comunicato](https://www.istat.it/comunicato-stampa/la-pratica-sportiva-in-italia/) · [Tavole .xls](https://www.istat.it/wp-content/uploads/2025/06/Tavole-allegate_statistica_today_sport_Anno2024.xls) · [Report PDF](https://www.istat.it/wp-content/uploads/2025/06/La-pratica-sportiva-in-Italia_2024.pdf)
- 11 tavole: pratica per età/sesso (T1), regione (T2), frequenza (T3), tipo di sport (T4), luogo (T5), motivi della pratica (T6), ex praticanti e mai praticato (T7-T8), **motivi per cui non si pratica** (T9), sedentarietà (T10-T11).
- CSV puliti in `data/clean/`:
  - `sport_per_eta_sesso_2024.csv` (eta, sesso, indicatore, valore)
  - `sport_per_territorio_2024.csv` (territorio, livello, 5 indicatori)
  - `motivi_non_pratica_2024.csv` (gruppo, categoria, motivo, valore; risposte multiple)
- Limite: i motivi della T9 riguardano **tutti** i non praticanti (ex + mai praticato), non solo chi ha smesso.

### 2. Microdati AVQ – Aspetti della vita quotidiana (file ad uso pubblico mIcro.STAT)
- Pagina: <https://www.istat.it/microdati/aspetti-della-vita-quotidiana/>
- Anni disponibili: **2013-2024**, download gratuito, **senza registrazione**.
- Link diretto (cambia solo l'anno):
  `https://www.istat.it/wp-content/themes/EGPbs5-child/microdata/download.php?file=%2F60%2F<ANNO>%2F01%2F01.zip&filename=AVQ_<ANNO>_IT.zip`
- **Tutti gli anni 2013-2024 sono in `data/raw/microdati_avq/<anno>/`** (zip originale + estratto, ~1,3 GB in totale). Per ogni anno:
  - `MICRODATI/AVQ_Microdati_<anno>.txt`: un individuo per riga, separato da tabulazione
  - `METADATI/AVQ_Tracciato_<anno>.html`: elenco delle variabili; `Classificazioni/` contiene i codici

| Anno | Righe | Colonne | Note |
|---|---|---|---|
| 2013 | 20.275 | 743 | nomi minuscoli, schema diverso (`eta` a 18 classi, `reg`, `peso`); nessun `FREQSPO` |
| 2014 | 44.974 | 828 | regione = `REGMif`; nessun `FREQSPO` |
| 2015 | 45.204 | 705 | regione = `REGMif`; nessun `FREQSPO` |
| 2016 | 43.360 | 623 | regione = `REGMif` |
| 2017 | 48.855 | 683 | regione = `REGMF`; nessun `LEZPR` |
| 2018 | 44.672 | 691 | regione = `REGMF`; nessun `LEZPR` |
| 2019 | 45.483 | 755 | |
| 2020 | 42.810 | 755 | regione = `REGMF`; anno COVID |
| 2021 | 45.597 | 735 | |
| 2022 | 42.022 | 741 | |
| 2023 | 41.750 | 708 | |
| 2024 | 45.005 | 736 | |

Totale: **~510 mila individui**. `SPOCON`, `SPOSAL`, `ATTFIS`, `ORESETSP`, `ETAMi`, `SESSO`, `ISTRMi`, `COEFIN` ci sono in tutti gli anni dal 2014 in poi. Nomi e codici vanno armonizzati con i tracciati di ciascun anno.

> Attenzione: `NOSPO1-8` **non** riguarda lo sport (è la soddisfazione per la raccolta rifiuti porta a porta).

- Variabili utili:
  - Sport: `SPOCON` (sport continuativo), `SPOSAL` (saltuario), `ATTFIS` (attività fisica), `FREQSPO`, `ORESETSP` (ore/settimana), `SPPAG` (luoghi a pagamento), `SPRIV` (corsi privati), `RETTA` (club), `SPSPO` (spettacoli sportivi)
  - Socio-demografiche: `ETAMi` (15 classi: 11-13, 14-15, 16-17, 18-19, 20-24…), `SESSO`, `ISTRMi` (titolo di studio), `CONDMi` (occupato / in cerca / inattivo, nessun codice studente), `LEZPR` (recupero scolastico), `REGMf`, `RIPMf`, `REDPRMi` (reddito), `CITTMi`
  - Peso campionario: `COEFIN` (dividere per 10.000), da usare **sempre** per le stime
- Non ci sono i motivi dell'abbandono: quelli stanno solo nell'indagine "I cittadini e il tempo libero" (tavole aggregate).

### 3. Dataset armonizzato AVQ 2014-2024
Creato da `python scripts/costruisci_avq.py` (circa 15 secondi).
- `data/processed/avq_sport_2014_2024.parquet` (da preferire) e `.csv.gz`: **489.732 individui × 27 colonne**, una riga per persona.
- `data/processed/controllo_stime_annuali.csv`: stime pesate per anno, persone di 3 anni e più.
- Colonne: `anno`, `id_famiglia`, `id_individuo` (solo dal 2018), `peso` (= COEFIN/10.000), `sesso`, `eta_classe` (15 classi), `regione`, `ripartizione`, `titolo_studio`, `titolo_max_famiglia` (titolo più alto tra i componenti di 25+ anni), `condizione`, `cittadinanza` (solo dal 2018), `fonte_reddito`, `n_componenti`, `risorse_economiche` (RISEC: ottime / adeguate / scarse / assolutamente insufficienti), `sport_continuativo`, `sport_saltuario`, `pratica_sport`, `attivita_fisica`, `livello_attivita` (sport continuativo / saltuario / solo attività fisica / sedentario, come nelle tavole ISTAT), `freq_sport` (dal 2016), `ore_sport_sett`, `sport_pagamento`, `corsi_sport`, `retta_club`, `spettacoli_sportivi`, `lezioni_recupero` (manca nel 2017-2018).
- Scelte di armonizzazione:
  - campo vuoto = non applicabile → NA (per esempio `attivita_fisica` è chiesta solo a chi non fa sport);
  - regione oscurata per riservatezza (444-888) o non disponibile (999) → NA, ma la ripartizione resta;
  - le domande su frequenza, ore, sport a pagamento e corsi sono rivolte solo a chi fa sport, quindi sono NA per gli altri.
- Controllo: pratica sportiva (3 anni e più) **31,8% nel 2014 → 37,7% nel 2024**; le tavole ISTAT 2024 (altra indagine) danno 37,5%.

| Anno | Sport continuativo % | Sport saltuario % | Pratica sport % |
|---|---|---|---|
| 2014 | 23,1 | 11,3 | 31,8 |
| 2016 | 25,2 | 13,1 | 34,9 |
| 2018 | 25,8 | 13,0 | 35,4 |
| 2020 | 27,1 | 13,1 | 36,6 |
| 2021 | 23,6 | 14,3 | 34,5 |
| 2022 | 26,3 | 11,3 | 34,6 |
| 2024 | 28,7 | 12,6 | 37,7 |

### Altre fonti da valutare
- **Indagine su bambini e ragazzi** (11-19 anni, 2021 e 2023, ~39-41 mila ragazzi), microdati pubblici con tempo libero ed esperienza scolastica: [link](https://www.istat.it/microdati/indagine-indagine-su-bambini-e-ragazzi-comportamenti-atteggiamenti-e-progetti-futuri-microstat/)
- File MFR per la ricerca: solo per ricercatori di enti riconosciuti, non per studenti in autonomia.

## Primi risultati (tavole 2024)
- Pratica sport il 37,5% della popolazione (M 43,4%, F 31,8%).
- Gli ex praticanti salgono con l'età: 9% a 11-14 anni, 16% a 15-17, 28% a 18-19. Tra le ragazze di 15-17 anni sono il 20,9%, tra i ragazzi l'11,9%.
- Perché i 15-17enni non fanno sport: mancanza di interesse 48,9%, mancanza di tempo 42,6%, impianti/orari 7,3%.
- Divario Nord-Sud: Trentino-AA 53,2% contro Calabria 22,9% e Campania 23,9%.

## Analisi esplorativa (notebook 01)
`notebooks/01_analisi_esplorativa.ipynb`: stime pesate con IC 95% approssimato (n effettivo di Kish: il file pubblico non ha strati e grappoli, quindi gli intervalli veri sono un po' più larghi).

![[01_trend_pratica_sesso.png]]
![[03_pratica_eta_sesso.png]]
![[04_trend_giovani.png]]
![[05_regioni.png]]

Risultati principali:
- Pratica sportiva 31,8% (2014) → 37,7% (2024); calo COVID nel 2021, soprattutto tra gli 11-15enni.
- Divario di genere stabile intorno ai 10 punti; tra i giovani è massimo a 16-19 anni (ragazze ~50%, ragazzi 65-70%).
- Le ragazze iniziano a smettere già a 11-15 anni.
- Nord-Sud: Trentino-AA 55% contro Calabria 22% (2022-2024); la Calabria è l'unica regione che peggiora.
- 25-64 anni: laureati 59% contro 10% con licenza elementare o nessun titolo.
- **Ripetizioni:** chi prende lezioni di recupero fa *più* sport; reddito e istruzione della famiglia ne spiegano solo una parte (vedi notebook 02). Questo proxy non supporta l'ipotesi "la scuola toglie tempo allo sport".
- **Motivi (sezione 7, tavole 2024):** tra gli 11-14enni che non fanno sport prevale la mancanza di interesse (47%, tempo 32%). Dalle superiori la mancanza di tempo sale a 43% (15-17), 44% (18-19) e 49% (20-24) e pareggia l'interesse. È l'indizio più diretto a favore dell'ipotesi "studio e impegni tolgono tempo allo sport". Limite: la domanda riguarda anche chi non ha mai fatto sport.

![[13_motivi_non_pratica_giovani.png]]

## Regressione logistica pesata (notebook 02)
`notebooks/02_regressione_logistica.ipynb`. Pesi campionari normalizzati, errori standard sandwich raggruppati per famiglia (calcolati a mano: `statsmodels` non li supporta del tutto con i pesi), risultati come odds ratio e probabilità predette standardizzate.

- **Modello A** (11-24 anni, n = 62.188): `pratica_sport ~ sesso × età + ripartizione + titolo_max_famiglia + risorse + anno`
  - divario di genere a parità del resto: da 12 punti (11-13 anni) a 20 punti (18-19 anni);
  - Sud e Isole circa 12 punti sotto il Centro-Nord anche a parità di famiglia;
  - titolo della famiglia: 71% (laurea) contro 37% (licenza elementare); risorse: 62% contro 56%;
  - 2021 unico anno nettamente più basso (OR 0,76).
- **Modello B** (11-19 anni, n = 32.363): l'OR delle ripetizioni scende da 1,70 a 1,49 aggiungendo territorio e famiglia, ma resta sopra 1 (69,5% contro 61,5%). Reddito e istruzione **non** bastano a spiegarlo.

![[10_modelloA_sesso_eta.png]]
![[12_modelloB_ripetizioni.png]]

## Fonte big data: OpenStreetMap (notebook 03)
- `scripts/scarica_osm.py` conta per regione gli elementi OSM con `leisure` = pitch (campi), sports_centre, fitness_centre (palestre), stadium, track. Le piscine sono escluse (in OSM sono soprattutto private). Snapshot del 19/10/2026, licenza ODbL. Le risposte originali sono salvate in `data/raw/osm/2026-10-19/`.
- Il server Overpass pubblico è instabile (errori 502/504): lo script riprova da solo e riparte dalle regioni mancanti. Usa `curl` perché il Python di sistema del Mac (LibreSSL) non riesce a connettersi via TLS.
- Popolazione regionale stimata con i pesi AVQ 2024; pratica sportiva 2022-2024.

Risultati (20 regioni):
- impianti ogni 10.000 abitanti e pratica sportiva sono correlati: r = 0,67 (Spearman 0,60); per gli 11-24enni r = 0,57;
- a parità di Mezzogiorno, +1 impianto ogni 10.000 abitanti ≈ +0,5 punti di pratica; R² da 0,64 (solo Nord-Sud) a 0,84;
- il divario del Mezzogiorno passa da −13,3 a −10,9 punti: gli impianti ne spiegano meno di un quinto;
- casi anomali: la Sardegna (tanti impianti mappati, pratica bassa), Lazio e Lombardia (pochi impianti per abitante, pratica alta).
- Limite principale: OSM misura sia gli impianti sia l'impegno di chi li mappa. Servirebbe una validazione con il censimento degli impianti di Sport e Salute.

![[14_osm_impianti_vs_pratica.png]]

### Storico OSM (notebook 03, sezione 3)
- `scripts/scarica_ohsome.py`: con l'API ohsome (HeiGIT) e i confini ufficiali ISTAT, conta gli impianti mappati al 1° gennaio di ogni anno dal 2010 al 2026.
- Impianti mappati in Italia: 3.838 (2010) → 38.280 (2014) → 101.653 (2024), **+166% in dieci anni** contro +19% della pratica sportiva: la crescita misura la **mappatura**, non nuovi impianti.
- Dal 2014 Centro e Mezzogiorno crescono più del Nord (recupero della mappatura): la copertura cambia nello spazio e nel tempo.
- **Sardegna**: da 1.745 a 4.690 impianti mappati tra il 2014 e il 2015, poi quasi ferma: caricamento in blocco. Spiega perché sembra piena di impianti.
- Con gli impianti mappati al 1/1/2024 (stesso periodo dell'indagine) il risultato regge: r = 0,68.
- Le variazioni di OSM non seguono quelle della pratica (r = 0,28, n.s.): OSM non serve per misurare cambiamenti nel tempo.

![[19_osm_storico_vs_pratica.png]]

## Machine learning (notebook 04)
**Supervisionato** (11-24 anni; addestramento 2014-2022, test 2023-2024; pesi campionari):
- regressione logistica, random forest e gradient boosting hanno la **stessa AUC (0,67)**: un modello più complesso non aggiunge nulla. A parità di prestazioni, per la statistica ufficiale conviene il modello interpretabile;
- importanza per permutazione: titolo di studio della famiglia > sesso > età > regione (come nel notebook 02);
- stime regionali dal modello: scarto medio di circa 3 punti da quelle dirette, maggiore in Calabria ed Emilia-Romagna;
- nota etica: un modello che "prevede" meno sport per ragazze e Sud riproduce le disuguaglianze se usato per decidere.

**Non supervisionato** (clustering gerarchico di Ward su 7 indicatori regionali):
- con 2 gruppi (silhouette 0,41) emerge solo il divario Mezzogiorno / resto d'Italia;
- con 3 gruppi: *molti impianti per abitante* (FVG, Piemonte, Sardegna, Toscana, TAA, VdA, Veneto), *famiglie più istruite, meno impianti* (Abruzzo, Emilia-Romagna, Lazio, Liguria, Lombardia, Marche, Molise, Umbria), *bassa pratica* (Basilicata, Calabria, Campania, Puglia, Sicilia);
- la Sardegna entra nel primo gruppo per l'import OSM del 2015: un difetto della fonte big data si trasmette alla classificazione.

![[18_cluster_mappa.png]]

## Qualità delle fonti
Vedi [[Valutazione qualità delle fonti]]: griglia della qualità del corso (solidità metodologica, integrità, servibilità, accessibilità), errori di misura e di non osservazione, le cinque famiglie di sfide vissute nel progetto, il processo KDD applicato a OSM e il ruolo di OSM accanto alla statistica ufficiale.

## Presentazione
- **Slide (20, in inglese, 15-20 minuti):** <https://claude.ai/artifact/MJXuv1t2rS4TC168fsCGeH>. Si scarica in .pptx o PDF dal menu della presentazione.
- Ogni slide ha le note per chi presenta, con i tempi indicativi (circa 50 secondi l'una).
- I grafici delle slide sono in `figures/en/`, generati da `scripts/figure_inglese.py` a partire dalle tabelle di `results/` (stessi numeri dei notebook).
- Da completare prima dell'esame: nome dello studente e data sulla copertina (`[Student name]`, `[Exam date]`).

## Prossimi passi
- [x] Scaricare i microdati AVQ 2013-2024 (~510 mila righe)
- [x] Script per leggere i microdati e armonizzare le variabili tra gli anni (`scripts/costruisci_avq.py`)
- [x] Stime pesate della pratica sportiva per anno, età, sesso, regione, titolo di studio (notebook 01)
- [x] Analisi esplorativa: trend, COVID, giovani, divari territoriali, `LEZPR`
- [x] Regressione logistica pesata: sesso, età, territorio, titolo di studio e risorse della famiglia (notebook 02)
- [x] Rapporto ripetizioni-sport tenendo conto di reddito e istruzione della famiglia (notebook 02, modello B)
- [x] Fonte big data: impianti sportivi da OpenStreetMap (notebook 03)
- [x] Storico OSM con ohsome: crescita della mappatura e verifica temporale (notebook 03)
- [x] Machine learning: supervisionato e clustering (notebook 04)
- [x] Valutazione della qualità delle fonti con la griglia del corso
- [x] Preparare la presentazione (20 slide in inglese, scaricabile in .pptx)
- [ ] Concordare il tema con la docente e inserire nome e data in copertina
- [ ] Provare la presentazione a voce cronometrando i tempi
