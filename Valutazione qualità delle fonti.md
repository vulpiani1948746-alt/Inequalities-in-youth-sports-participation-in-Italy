---
progetto: BDS-chiara
corso: Big Data for Official Statistics
tags: [official-statistics, data-quality, big-data]
creato: 2026-10-26
---

# Valutazione della qualità delle fonti: ISTAT AVQ e OpenStreetMap

Il progetto usa due fonti molto diverse:
- **ISTAT, Aspetti della vita quotidiana (AVQ)**: indagine campionaria ufficiale, file ad uso pubblico 2014-2024 (~490 mila persone);
- **OpenStreetMap (OSM)**: mappa costruita da volontari, da cui contiamo gli impianti sportivi per regione (fotografia di oggi con Overpass, storico 2010-2026 con ohsome).

Questa nota le valuta con gli strumenti del corso (cap. 1 e 2, [[01 - Courses/2-I. BDOS/1. Official Statistics and Crucial Definitions · From Data Quality to Representation|appunti cap. 1]], [[01 - Courses/2-I. BDOS/2. Big Data in Official Statistics · Opportunities and Criticisms|appunti cap. 2]]): la griglia della qualità, gli errori, le cinque famiglie di sfide e il processo KDD.

---

## 1. La griglia della qualità

Le quattro dimensioni di [[02 - Concepts/Official Statistics/Quality of Official Statistics|qualità della statistica ufficiale]], applicate alle due fonti.

| Dimensione | Criterio | ISTAT AVQ | OpenStreetMap |
|---|---|---|---|
| **Solidità metodologica** | accuratezza e validità | Definizione standard di "pratica sportiva", stabile dal 1993. Dato **auto-dichiarato**: possibile distorsione verso risposte socialmente desiderabili. Le nostre stime 2024 coincidono con quelle pubblicate (37,7% contro 37,5%). | Nessuna definizione controllata: un "campo" può essere un campetto di quartiere o un campo privato; un centro sportivo contiene spesso campi già contati. Conta **gli impianti mappati**, non quelli esistenti. |
| | precisione e affidabilità | Campione probabilistico: l'errore si può calcolare (IC al 95% di circa ±0,5 punti a livello nazionale nel 2024, approssimato). | Nessun errore calcolabile: non è un campione, e non conosciamo la probabilità che un impianto sia mappato. |
| | riproducibilità | Microdati e metadati pubblici: chiunque può rifare le stime. | Riproducibile solo se si salva la data della fotografia: la mappa cambia ogni minuto. Noi salviamo le risposte originali (`data/raw/osm`, `data/raw/ohsome`). |
| **Integrità** | obiettività, trasparenza | Istituto pubblico indipendente, Codice delle statistiche europee, note metodologiche pubblicate. | Trasparente (ogni modifica è tracciata), ma senza un responsabile editoriale: chiunque può modificare, anche con errori o vandalismi. |
| **Servibilità** | pertinenza | Misura direttamente il fenomeno (chi fa sport). | Misura un fattore di contesto (l'offerta di impianti), utile per spiegare, non per misurare la pratica. |
| | tempestività | Tavole 2024 pubblicate a giugno 2025; file pubblico dei microdati 2024 aggiornato a luglio 2026: almeno sei mesi di ritardo rispetto al periodo osservato. | Aggiornamento continuo, dati disponibili in pochi minuti. |
| | comparabilità nel tempo | Serie dal 1993; per i microdati 2014-2024 abbiamo dovuto armonizzare nomi e codici delle variabili. | **Bassa**: tra il 2014 e il 2024 gli impianti mappati crescono del 166%, quasi tutto per effetto della mappatura (vedi §2). |
| | disaggregabilità | File pubblico: solo regione e ripartizione; regione oscurata per ~1% dei record. | Fino al singolo impianto, con coordinate: dettaglio territoriale molto superiore. |
| | parsimonia (costo) | Indagine costosa (~20 mila famiglie l'anno), gratuita per l'utente. | Gratuita per chi produce e per chi usa. |
| **Accessibilità** | usabilità | Download libero, senza registrazione; file di testo con tracciato e classificazioni. | Licenza aperta (ODbL), ma servono competenze tecniche (API, query, geometrie) e i server pubblici sono instabili. |

---

## 2. Gli errori

| Famiglia di errore | ISTAT AVQ | OpenStreetMap |
|---|---|---|
| **Errore di misura** (osservazione) | Errori di risposta: cosa conta come "sport", ricordo, desiderabilità sociale. Parte casuale e parte sistematica. | Errori di classificazione (tag sbagliati o generici), doppi conteggi tra categorie, impianti chiusi ancora presenti, piscine private (per questo escluse). |
| **Errore di campionamento** | Presente e **misurabile**: campione probabilistico con pesi noti. | Non definito: non c'è un disegno di campionamento. |
| **Errore di copertura** | Basso: la popolazione di riferimento è definita (famiglie residenti) e la lista di campionamento è anagrafica. | **Il problema principale.** Sono visibili solo gli impianti che qualche volontario ha mappato. È una forma di **auto-selezione** (cap. 1, campionamento per auto-selezione; cap. 2, sfida metodologica della copertura). |
| **Mancata risposta** | Presente, corretta dall'ISTAT con i pesi. | Equivalente: zone dove nessuno mappa. Non si può correggere perché non sappiamo dove sono. |

**Le prove raccolte nel progetto** (notebook 03, sezione 3):
- impianti mappati in Italia: **3.838 nel 2010, 38.280 nel 2014, 101.653 nel 2024**. Gli impianti reali non sono decuplicati: la crescita misura l'attività dei volontari;
- la copertura **cambia tra territori**: dal 2014 Centro e Mezzogiorno crescono più del Nord (indice 2024: 316 e 333 contro 229), cioè stanno recuperando un ritardo di mappatura;
- il caso **Sardegna**: tra il 2014 e il 2015 passa da 1.745 a 4.690 impianti mappati in un anno, poi resta quasi ferma. È il segno di un caricamento in blocco da una fonte esterna. Risultato: sembra avere tanti impianti quanti il Trentino-Alto Adige, ma una pratica sportiva molto più bassa, e nel clustering (notebook 04) finisce nel gruppo "molti impianti". **Un errore di copertura della fonte big data si trasmette fino alla classificazione finale.**
- le variazioni di OSM tra regioni non seguono quelle della pratica sportiva (r = 0,28, non significativo): OSM non è utilizzabile per misurare cambiamenti nel tempo.

![[19_osm_storico_vs_pratica.png]]

---

## 3. Le cinque famiglie di sfide, vissute nel progetto

| Sfida (cap. 2) | Cosa è successo nel progetto |
|---|---|
| **Tecnica** | I dati OSM non sono strutturati per la statistica: servono query, geometrie e conversioni di coordinate (i confini ISTAT sono in UTM 32N, ohsome vuole longitudine e latitudine). I server Overpass hanno dato errori 502/504 per ore; il Python di sistema del Mac non riusciva a connettersi (TLS). Abbiamo dovuto scrivere script che riprovano e riprendono da dove si erano fermati. |
| **Metodologica** | Copertura incompleta e variabile (§2); definizioni non controllate; impossibilità di calcolare un errore. Per i microdati: il file pubblico non contiene strati e unità primarie, quindi gli errori standard sono approssimati. |
| **Istituzionale** | OSM non ha un proprietario unico né un responsabile della qualità: nessuno garantisce completezza o continuità. L'ISTAT non può "ordinare" ai volontari di mappare il Sud. |
| **Legale** | Licenza ODbL: uso libero con attribuzione e condivisione dei derivati. I microdati ISTAT sono anonimizzati (regione oscurata per ~1% dei record) per proteggere la riservatezza. |
| **Formativa** | Il progetto ha richiesto le quattro figure del "data scientist" del corso: informatico (API, script), statistico (pesi, errori), narratore (grafici) e la domanda del "filosofo" su cosa misura davvero il dato. |

---

## 4. Il processo KDD applicato a OpenStreetMap

I cinque passi "dai segni ai dati" (Fayyad e colleghi, 1996; cap. 2.6):

1. **Selezione**: quali impianti? Tag `leisure` = pitch, sports_centre, fitness_centre, stadium, track; esclusa swimming_pool. Quali confini? Quelli ufficiali ISTAT 2025.
2. **Pre-elaborazione**: risposte dei server controllate (nessuna regione con zero impianti), salvate in originale; conversione dei confini da UTM 32N a longitudine/latitudine.
3. **Trasformazione**: conteggi per regione e anno, rapportati alla popolazione stimata dai pesi AVQ (impianti ogni 10.000 abitanti).
4. **Data mining**: correlazione e regressione con la pratica sportiva, clustering delle regioni.
5. **Interpretazione e valutazione**: confronto con lo storico (ohsome) e con la fonte ufficiale. È qui che scopriamo che la crescita di OSM è mappatura e che il caso Sardegna è un artefatto. Senza questo passo avremmo preso per conoscenza un difetto del dato.

---

## 5. Conclusione: che posto ha OSM accanto alla statistica ufficiale?

Il programma del corso distingue due usi dei big data: rendere le statistiche **più tempestive e più dettagliate** (es. nowcasting) oppure **aggiungere conoscenza** guardando il fenomeno da un'altra angolazione.

- **Tempestività e nowcasting: no.** OSM cresce per motivi che non hanno a che fare con lo sport, quindi le sue variazioni non anticipano quelle della pratica.
- **Un'altra angolazione: sì, con cautela.** In un dato momento OSM descrive bene le differenze di offerta tra regioni (r = 0,68 con la pratica sportiva, anche a parità di Nord-Sud), con un dettaglio territoriale che l'indagine non ha.
- **Condizione per usarlo:** una **validazione con una fonte censuaria**, come il censimento degli impianti sportivi di Sport e Salute, per stimare la copertura di OSM regione per regione e correggerla. È ciò che il corso chiama passare da dati "trovati" a statistiche **affidabili** ([[02 - Concepts/Official Statistics/Trusted Smart Statistics|Trusted Smart Statistics]]): l'istituto di statistica non produce più tutto il dato, ma ne certifica la qualità.
