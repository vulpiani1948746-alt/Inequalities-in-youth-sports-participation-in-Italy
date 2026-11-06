"""English versions of the project's charts, sized for the presentation slides.

Usage: python scripts/figure_inglese.py
Input:  the tables in results/ and data/ produced by the notebooks (no model is re-estimated here)
Output: figures/en/*.png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapefile
from matplotlib.patches import Polygon
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RES, OUT = ROOT / "results", ROOT / "figures" / "en"
OUT.mkdir(parents=True, exist_ok=True)

SURFACE, INK, INK_2, GRID = "#fbfbf8", "#14213d", "#4a5568", "#e2e1dc"
BLUE, ORANGE, AQUA, YELLOW, MAGENTA = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.15,
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "font.size": 14, "axes.titlesize": 15, "axes.labelsize": 14, "xtick.labelsize": 13, "ytick.labelsize": 13,
    "text.color": INK, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.9,
    "lines.linewidth": 2.6, "legend.frameon": False, "legend.fontsize": 13,
})
SEX = {"Maschio": "Boys / men", "Femmina": "Girls / women"}
SEX_COLOR = {"Maschio": BLUE, "Femmina": ORANGE}
AREA = {"Nord": "North", "Centro": "Centre", "Mezzogiorno": "South & Islands"}
AREA_COLOR = {"Nord": BLUE, "Centro": AQUA, "Mezzogiorno": ORANGE}


def save(fig, name):
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    print("saved", name)


def end_labels(ax, x, values, texts, gap, dx=0.25, colors=None):
    order = np.argsort(values)
    pos = np.array(values, dtype=float)[order]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    for j, i in enumerate(order):
        ax.annotate(texts[i], (x, values[i]), xytext=(x + dx, pos[j]), textcoords="data", va="center",
                    fontsize=13, color=(colors[i] if colors else INK), fontweight="bold")


def weighted_share(df):
    v = df[df.pratica_sport.notna()]
    return 100 * np.average(v.pratica_sport.astype(float), weights=v.peso)


dati = pd.read_parquet(ROOT / "data" / "processed" / "avq_sport_2014_2024.parquet")
dati = dati[dati.eta_classe != "0-2"]

# 1. Trend by sex -------------------------------------------------------------------------
t = pd.read_csv(RES / "trend_pratica_sesso.csv")
total = dati.groupby("anno").apply(weighted_share, include_groups=False)
fig, ax = plt.subplots(figsize=(11, 5.4))
labels, vals, cols = [], [], []
for s, g in t.groupby("sesso", sort=False):
    ax.fill_between(g.anno, g.ic_basso, g.ic_alto, color=SEX_COLOR[s], alpha=0.15, linewidth=0)
    ax.plot(g.anno, g.quota, color=SEX_COLOR[s], marker="o", markersize=6)
    labels.append(f"{SEX[s]} {g.quota.iloc[-1]:.1f}%"); vals.append(g.quota.iloc[-1]); cols.append(SEX_COLOR[s])
ax.plot(total.index, total.values, color=INK_2, linestyle="--", linewidth=2)
labels.append(f"Total {total.iloc[-1]:.1f}%"); vals.append(total.iloc[-1]); cols.append(INK_2)
end_labels(ax, 2024, vals, labels, gap=2.2, colors=cols)
ax.axvspan(2020.6, 2021.4, color=GRID, alpha=0.8, linewidth=0)
ax.text(2021, 25.3, "COVID", ha="center", fontsize=12, color=INK_2)
ax.set_xticks(range(2014, 2025)); ax.set_xlim(2013.6, 2026.9); ax.set_ylim(24.5, 46)
ax.set_ylabel("Practise sport (%), age 3+")
save(fig, "e01_trend_sex")

# 2. Age profile ---------------------------------------------------------------------------
e = pd.read_csv(RES / "pratica_eta_sesso_2022_2024.csv")
ages = list(dict.fromkeys(e.eta_classe))
fig, ax = plt.subplots(figsize=(11, 5.4))
x = np.arange(len(ages))
for s, g in e.groupby("sesso", sort=False):
    g = g.set_index("eta_classe").loc[ages]
    ax.fill_between(x, g.ic_basso, g.ic_alto, color=SEX_COLOR[s], alpha=0.15, linewidth=0)
    ax.plot(x, g.quota, color=SEX_COLOR[s], marker="o", markersize=6, label=SEX[s])
ax.axvspan(1.5, 6.5, color=GRID, alpha=0.6, linewidth=0)
ax.text(4, 3, "ages 11-24", ha="center", fontsize=12, color=INK_2)
ax.set_xticks(x, ages, fontsize=12)
ax.set_xlabel("Age group"); ax.set_ylabel("Practise sport (%)")
ax.legend(loc="upper right")
save(fig, "e02_age_profile")

# 3. Reasons for not doing sport (youth) --------------------------------------------------
m = pd.read_csv(ROOT / "data" / "clean" / "motivi_non_pratica_2024.csv")
REASONS = {"Mancanza di interesse": "Lack of interest", "Mancanza di tempo": "Lack of time",
           "Stanchezza, pigrizia": "Tiredness, laziness", "Mancanza di impianti,orari scomodi": "No facilities, bad hours",
           "Motivi economici": "Cost", "Timidezza, disagio": "Shyness, discomfort",
           "Motivi di salute/disabilità": "Health, disability", "Motivi familiari": "Family reasons"}
m = m[(m.gruppo == "classi di età") & m.categoria.isin(["11-14", "15-17", "18-19", "20-24"]) & m.motivo.isin(REASONS)]
m = m.pivot(index="motivo", columns="categoria", values="valore").rename(index=REASONS).sort_values("15-17")
FASCE = {"11-14": BLUE, "15-17": ORANGE, "20-24": AQUA}
OFF = {"11-14": 0.17, "15-17": 0, "20-24": -0.17}
fig, ax = plt.subplots(figsize=(11, 5.4))
y = np.arange(len(m))
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
for f, c in FASCE.items():
    ax.scatter(m[f], y + OFF[f], s=90, color=c, edgecolor=SURFACE, linewidth=2, zorder=3, label=f"Age {f}")
for yi, r in zip(y[-2:], m.index[-2:]):
    for f in FASCE:
        ax.annotate(f"{m.loc[r, f]:.0f}", (m.loc[r, f], yi + OFF[f]), xytext=(0, 9), textcoords="offset points",
                    ha="center", fontsize=12, color=INK_2)
ax.set_yticks(y, m.index); ax.set_xlim(0, 56); ax.set_ylim(-0.6, len(m) - 0.2)
ax.set_xlabel("% of non-practitioners of the same age (multiple answers)")
ax.legend(loc="lower right")
save(fig, "e03_reasons_youth")

# 4. Regions --------------------------------------------------------------------------------
r = pd.read_csv(RES / "pratica_regioni.csv").sort_values("quota")
fig, ax = plt.subplots(figsize=(7.6, 7.6))
y = np.arange(len(r))
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
ax.hlines(y, r.quota_2014_2016, r.quota, color=GRID, linewidth=2.5)
ax.scatter(r.quota_2014_2016, y, color=SURFACE, edgecolor=INK_2, s=45, zorder=3, label="2014-2016")
ax.scatter(r.quota, y, color=BLUE, s=60, zorder=4, edgecolor=SURFACE, linewidth=2, label="2022-2024")
for yi, q, q0 in zip(y, r.quota, r.quota_2014_2016):
    ax.annotate(f"{q:.0f}%", (max(q, q0), yi), xytext=(7, 0), textcoords="offset points", va="center",
                fontsize=11, color=INK_2)
ax.set_yticks(y, r.regione, fontsize=12)
ax.set_xlabel("Practise sport (%), age 3+")
ax.legend(loc="lower right")
save(fig, "e04_regions")

# 5. Odds ratios -----------------------------------------------------------------------------
o = pd.read_csv(RES / "modelloA_odds_ratio.csv", index_col=0)
o = o[~o.index.str.contains("anno_f|Intercept|:")]
NAMES = {"sesso[T.Femmina]": "Female (vs male)",
         "eta_classe[T.14-15]": "Age 14-15", "eta_classe[T.16-17]": "Age 16-17",
         "eta_classe[T.18-19]": "Age 18-19", "eta_classe[T.20-24]": "Age 20-24",
         "ripartizione[T.Nord-est]": "North-East", "ripartizione[T.Centro]": "Centre",
         "ripartizione[T.Sud]": "South", "ripartizione[T.Isole]": "Islands",
         "titolo_max_famiglia[T.Diploma]": "Family: upper secondary",
         "titolo_max_famiglia[T.Licenza media]": "Family: lower secondary",
         "titolo_max_famiglia[T.Licenza elementare o nessun titolo]": "Family: primary or none",
         "risorse[T.Scarse o insufficienti]": "Scarce economic resources"}
o = o.loc[list(NAMES)].rename(index=NAMES)
fig, ax = plt.subplots(figsize=(10, 6.4))
y = np.arange(len(o))[::-1]
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
ax.axvline(1, color=INK_2, linewidth=1.2)
ax.hlines(y, o.IC_basso, o.IC_alto, color=BLUE, linewidth=2.6)
ax.scatter(o.OR, y, color=BLUE, s=60, zorder=3, edgecolor=SURFACE, linewidth=2)
for yi, (_, row) in zip(y, o.iterrows()):
    ax.annotate(f"{row.OR:.2f}", (row.IC_alto, yi), xytext=(7, 0), textcoords="offset points", va="center",
                fontsize=12, color=INK_2)
ax.set_yticks(y, o.index)
ax.set_xscale("log")
ax.set_xticks([0.2, 0.3, 0.5, 0.7, 1, 1.5], ["0.2", "0.3", "0.5", "0.7", "1", "1.5"])
ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.set_xlabel("Odds ratio, 95% CI (log scale). Ref.: male, 11-13, North-West, degree in family")
save(fig, "e05_odds_ratios")

# 6. Predicted probability by sex and age -----------------------------------------------------
p = pd.read_csv(RES / "modelloA_prob_sesso_eta.csv")
ages = list(dict.fromkeys(p.eta_classe))
fig, ax = plt.subplots(figsize=(10, 5.6))
x = np.arange(len(ages))
for s, g in p.groupby("sesso", sort=False):
    g = g.set_index("eta_classe").loc[ages]
    ax.fill_between(x, g.IC_basso, g.IC_alto, color=SEX_COLOR[s], alpha=0.15, linewidth=0)
    ax.plot(x, g.prob, color=SEX_COLOR[s], marker="o", markersize=7, label=SEX[s])
piv = p.pivot(index="eta_classe", columns="sesso", values="prob").loc[ages]
for xi, (_, row) in zip(x, piv.iterrows()):
    ax.annotate(f"−{row.Maschio - row.Femmina:.0f} pp", (xi, (row.Maschio + row.Femmina) / 2), ha="center",
                va="center", fontsize=13, color=INK, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc=SURFACE, ec=GRID))
ax.set_xticks(x, ages); ax.set_xlabel("Age group")
ax.set_ylabel("Predicted probability (%)")
ax.legend(loc="upper right")
save(fig, "e06_gender_gap_age")

# 7. Predicted probability: territory and family ---------------------------------------------
q = pd.read_csv(RES / "modelloA_prob_territorio_famiglia.csv")
LEVELS = {"Nord-ovest": "North-West", "Nord-est": "North-East", "Centro": "Centre", "Sud": "South",
          "Isole": "Islands", "Laurea e post-laurea": "Degree or higher", "Diploma": "Upper secondary",
          "Licenza media": "Lower secondary", "Licenza elementare o nessun titolo": "Primary or none",
          "Ottime o adeguate": "Good or adequate", "Scarse o insufficienti": "Scarce or insufficient"}
GROUPS = {"Ripartizione": "Area", "Titolo più alto in famiglia": "Highest education in family",
          "Risorse economiche": "Family economic resources"}
fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharex=True, gridspec_kw={"width_ratios": [5, 4, 2.2]})
for ax, (gname, d) in zip(axes, q.groupby("gruppo", sort=False)):
    yy = np.arange(len(d))[::-1]
    ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
    ax.hlines(yy, d.IC_basso, d.IC_alto, color=BLUE, linewidth=2.6)
    ax.scatter(d.prob, yy, color=BLUE, s=60, zorder=3, edgecolor=SURFACE, linewidth=2)
    for yi, v in zip(yy, d.prob):
        ax.annotate(f"{v:.0f}%", (v, yi), xytext=(0, 10), textcoords="offset points", ha="center",
                    fontsize=12, color=INK_2)
    ax.set_yticks(yy, [LEVELS[l] for l in d.livello])
    ax.set_ylim(-0.7, len(d) - 0.3)
    ax.set_title(GROUPS[gname], loc="left", fontsize=14, fontweight="bold", color=INK)
axes[0].set_xlim(30, 78)
fig.tight_layout(w_pad=3)
save(fig, "e07_territory_family")

# 8. Tutoring: nested models -----------------------------------------------------------------
b = pd.read_csv(RES / "modelloB_ripetizioni.csv", index_col=0)
b.index = ["1. Sex, age, year", "2. + Area", "3. + Family education & resources"]
fig, ax = plt.subplots(figsize=(10, 3.8))
yy = np.arange(len(b))[::-1]
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
ax.axvline(1, color=INK_2, linewidth=1.2)
ax.hlines(yy, b.IC_basso, b.IC_alto, color=ORANGE, linewidth=2.8)
ax.scatter(b.OR, yy, color=ORANGE, s=75, zorder=3, edgecolor=SURFACE, linewidth=2)
for yi, (_, row) in zip(yy, b.iterrows()):
    ax.annotate(f"OR {row.OR:.2f}", (row.IC_alto, yi), xytext=(8, 0), textcoords="offset points", va="center",
                fontsize=13, color=INK, fontweight="bold")
ax.set_yticks(yy, b.index); ax.set_xlim(0.9, 2.15); ax.set_ylim(-0.5, 2.5)
ax.set_xlabel("Odds ratio of practising sport, with vs without remedial tutoring (1 = no association)")
save(fig, "e08_tutoring")

# 9. OSM facilities vs participation (1 January 2024, same period as the survey) ---------------
reg = pd.read_csv(RES / "osm_vs_pratica_regioni.csv", index_col="regione")
hist = pd.read_csv(RES / "ohsome_impianti_per_anno.csv", index_col="regione")
reg["fac24"] = hist["2024"] / reg.popolazione * 10_000
rr, _ = stats.pearsonr(reg.fac24, reg.pratica_sport)
fig, ax = plt.subplots(figsize=(10.5, 6.4))
ax.grid(axis="x", visible=True)
for a, c in AREA_COLOR.items():
    d = reg[reg.area == a]
    ax.scatter(d.fac24, d.pratica_sport, s=85, color=c, edgecolor=SURFACE, linewidth=2, zorder=3, label=AREA[a])
# crowded centre of the cloud: labels placed by hand (data coordinates), some with a leader line
PLACE = {"Lazio": (15.2, 39.3, "right", False), "Emilia-Romagna": (16.7, 42.4, "right", False),
         "Lombardia": (17.95, 44.3, "center", False), "Liguria": (18.3, 35.9, "right", False),
         "Toscana": (18.3, 40.9, "right", True), "Piemonte": (19.3, 33.6, "center", True),
         "Marche": (21.1, 40.6, "left", False), "Umbria": (21.4, 38.4, "left", False),
         "Abruzzo": (21.95, 36.0, "left", False)}
for name, row in reg.iterrows():
    if name in PLACE:
        tx, ty, ha, leader = PLACE[name]
        ax.annotate(name, (row.fac24, row.pratica_sport), xytext=(tx, ty), textcoords="data", fontsize=11,
                    color=INK_2, ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=INK_2, linewidth=0.8, shrinkA=2, shrinkB=4) if leader else None)
    else:
        ax.annotate(name, (row.fac24, row.pratica_sport), xytext=(7, 5), textcoords="offset points",
                    fontsize=11, color=INK_2)
k = np.polyfit(reg.fac24, reg.pratica_sport, 1)
xs = np.linspace(reg.fac24.min(), reg.fac24.max(), 50)
ax.plot(xs, np.polyval(k, xs), color=INK_2, linewidth=1.3, linestyle="--", zorder=2)
ax.set_xlabel("Sports facilities mapped in OSM per 10,000 inhabitants (1 Jan 2024)")
ax.set_ylabel("Practise sport (%), 2022-2024")
ax.legend(loc="lower right")
ax.text(0.01, 0.97, f"Pearson r = {rr:.2f}", transform=ax.transAxes, fontsize=14, fontweight="bold", va="top")
save(fig, "e09_osm_vs_participation")

# 10. OSM history vs participation -------------------------------------------------------------
years = [str(a) for a in range(2010, 2027)]
by_area = hist[years].groupby(reg.area).sum()
idx = by_area.div(by_area["2014"], axis=0) * 100
part = dati.groupby("anno").apply(weighted_share, include_groups=False)
part_idx = part / part[2014] * 100
fig, ax = plt.subplots(figsize=(11, 5.4))
labels, vals, cols = [], [], []
for a, c in AREA_COLOR.items():
    ax.plot([int(y) for y in years], idx.loc[a].values, color=c, marker="o", markersize=4.5)
    labels.append(f"OSM {AREA[a]}"); vals.append(idx.loc[a].iloc[-1]); cols.append(c)
ax.plot(part_idx.index, part_idx.values, color=INK_2, linestyle="--", marker="s", markersize=4.5)
ax.annotate("Sport participation (ISTAT)", (2024, part_idx.iloc[-1]), xytext=(2024.3, part_idx.iloc[-1] - 18),
            fontsize=13, color=INK_2, fontweight="bold")
end_labels(ax, 2026, vals, labels, gap=18, dx=0.3, colors=cols)
ax.axhline(100, color=GRID, linewidth=1.2)
ax.set_xticks(range(2010, 2027, 2)); ax.set_xlim(2009.5, 2031)
ax.set_ylabel("Index, 2014 = 100")
save(fig, "e10_osm_history")

# 11. ML model comparison and 12. variable importance -----------------------------------------
v = pd.read_csv(RES / "ml_confronto_modelli.csv", index_col="modello")
v.index = ["Baseline", "Logistic regression", "Random forest", "Gradient boosting"]
fig, ax = plt.subplots(figsize=(7.6, 4.4))
yy = np.arange(len(v))[::-1]
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
ax.barh(yy, v.AUC - 0.5, left=0.5, height=0.55, color=[GRID if i == 0 else BLUE for i in range(len(v))])
for yi, a in zip(yy, v.AUC):
    ax.annotate(f"{a:.3f}", (a, yi), xytext=(7, 0), textcoords="offset points", va="center", fontsize=13,
                fontweight="bold")
ax.set_yticks(yy, v.index); ax.set_xlim(0.5, 0.74)
ax.set_xlabel("AUC on 2023-2024 test set (0.5 = random)")
save(fig, "e11_ml_auc")

imp = pd.read_csv(RES / "ml_importanza_variabili.csv", index_col=0).sort_values("calo_AUC")
VARS = {"titolo_max_famiglia": "Family education", "sesso": "Sex", "eta_classe": "Age", "regione": "Region",
        "n_componenti": "Household size", "risorse_economiche": "Economic resources", "anno": "Year"}
fig, ax = plt.subplots(figsize=(7.6, 4.4))
yy = np.arange(len(imp))
ax.grid(axis="y", visible=False); ax.grid(axis="x", visible=True)
ax.barh(yy, imp.calo_AUC, xerr=imp.dev_std, height=0.55, color=BLUE,
        error_kw=dict(ecolor=INK_2, elinewidth=1.2, capsize=3))
ax.set_yticks(yy, [VARS[i] for i in imp.index])
ax.set_xlabel("Drop in AUC when the variable is shuffled")
save(fig, "e12_ml_importance")

# 13. Cluster map ----------------------------------------------------------------------------
prof = pd.read_csv(RES / "cluster_profili.csv", index_col=0)
CL = {"Molti impianti per abitante": ("Many facilities per capita", BLUE),
      "Famiglie più istruite, meno impianti": ("More educated families, fewer facilities", AQUA),
      "Bassa pratica (Mezzogiorno)": ("Low participation (South)", ORANGE)}
group_of = {reg_name.strip(): g for g, row in prof.iterrows() for reg_name in row.regioni.split(",")}
shp = shapefile.Reader(str(ROOT / "data" / "raw" / "confini_istat" / "Reg01012025_g" / "Reg01012025_g_WGS84"))
fig, ax = plt.subplots(figsize=(6.4, 7.2))
ax.set_aspect("equal"); ax.axis("off")
for rec, shape in zip(shp.records(), shp.shapes()):
    colour = CL[group_of[rec["DEN_REG"]]][1]
    parts = list(shape.parts) + [len(shape.points)]
    for a, b2 in zip(parts[:-1], parts[1:]):
        ax.add_patch(Polygon(shape.points[a:b2], closed=True, facecolor=colour, edgecolor=SURFACE, linewidth=0.9))
ax.autoscale_view()
for g, (label, colour) in CL.items():
    ax.scatter([], [], color=colour, s=110, marker="s", label=f"{label} ({int(prof.loc[g, 'n_regioni'])})")
ax.legend(loc="lower left", fontsize=12, bbox_to_anchor=(-0.02, -0.08))
save(fig, "e13_cluster_map")
