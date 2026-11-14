import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np
from data import *

R = json.load(open("results.json"))
S = json.load(open("sensitivity.json"))

# palette: one accent for the "problem", neutral for the rest
INK, MUTED, GRID = "#1f2933", "#7b8794", "#e4e7eb"
ACCENT, ACCENT2, GOOD = "#c2410c", "#2563eb", "#15803d"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 200, "text.parse_math": False})

def save(fig, name, title, subtitle=None, source=True):
    fig.suptitle(title, x=0.02, ha="left", fontsize=17, fontweight="bold", color=INK, y=0.985)
    if subtitle: fig.text(0.02, 0.905, subtitle, ha="left", fontsize=12, color=MUTED)
    if source: fig.text(0.02, -0.04, "Source: Airedale competition datasets 1 to 5 (3,000 units, 2025). Analysis: team init2winit.",
                        fontsize=9, color=MUTED)
    fig.savefig(f"charts/{name}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)

# 1. Pareto: where the warranty money goes
desc = sorted(BY_DESC.items(), key=lambda kv: kv[1][1])
fig, ax = plt.subplots(figsize=(11, 5.6)); fig.subplots_adjust(top=0.84)
cols = [ACCENT if DESC_CAT[d] == "Leak" else MUTED for d, _ in desc]
bars = ax.barh([d for d, _ in desc], [v[1] / 1e6 for _, v in desc], color=cols)
for b, (d, v) in zip(bars, desc):
    ax.text(b.get_width() + 0.03, b.get_y() + b.get_height() / 2,
            f"${v[1]/1e6:.2f}M  ({v[0]:,} units, ${v[1]/v[0]:,.0f}/unit)", va="center", fontsize=11, color=INK)
ax.set_xlim(0, 2.9); ax.set_xlabel("2025 warranty cost ($M)"); ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "01_warranty_pareto", "Leaks are 26% of failures but 76% of warranty cost",
     "Warranty cost by field failure type. Total $7.65M; leaks (orange) $5.78M.")

# 2. Leak heatmap facility x supplier
mat = np.array([[FAC_SUP_LEAK[(f, s)] / FAC_SUP_N[(f, s)] for s in SUP] for f in FAC])
fig, ax = plt.subplots(figsize=(9, 5.6)); fig.subplots_adjust(top=0.82)
im = ax.imshow(mat, cmap="Oranges", vmin=0, vmax=0.7)
ax.set_xticks(range(3), SUP); ax.set_yticks(range(4), FAC)
for i, f in enumerate(FAC):
    for j, s in enumerate(SUP):
        v = mat[i, j]
        ax.text(j, i, f"{v:.0%}\n({FAC_SUP_LEAK[(f, s)]}/{FAC_SUP_N[(f, s)]})", ha="center", va="center",
                fontsize=12, color="white" if v > 0.35 else INK, fontweight="bold" if v > 0.35 else "normal")
ax.spines[:] .set_visible(False); ax.tick_params(length=0)
save(fig, "02_leak_heatmap", "Two independent leak sources: Supplier B coils and Facility 2",
     "Leak rate by build facility and coil supplier. Supplier A/C coils never leak outside Facility 2.")

# 3. Controls by revision
fig, ax = plt.subplots(figsize=(9, 5)); fig.subplots_adjust(top=0.82)
revs = ["Rev A", "Rev B", "Rev C"]; vals = [REV_CONTROLS[r] / REV_N[r] for r in revs]
b = ax.bar(revs, vals, color=[ACCENT, MUTED, MUTED], width=0.55)
for bb, r, v in zip(b, revs, vals):
    ax.text(bb.get_x() + bb.get_width() / 2, v + 0.01, f"{v:.1%}\n{REV_CONTROLS[r]} of {REV_N[r]:,}", ha="center", fontsize=12)
ax.set_ylim(0, 0.42); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.set_ylabel("Controls failure rate")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "03_controls_revA", "Every controls failure is a Rev A unit ($785K)",
     "Sensor and communication faults by controls revision. EOLT flags all 283 as Sensor Miswire.")

# 4. Fan backwards: night shift only
fig, ax = plt.subplots(figsize=(10, 5)); fig.subplots_adjust(top=0.82)
x = np.arange(4); w = 0.38
night = [FAN_NIGHT_BY_FAC[f] / FAC_SHIFT_N[(f, "Night")] for f in FAC]
ax.bar(x - w / 2, [0] * 4, w, color=MUTED, label="Day shift")
nb = ax.bar(x + w / 2, night, w, color=ACCENT, label="Night shift")
for bb, f, v in zip(nb, FAC, night):
    ax.text(bb.get_x() + bb.get_width() / 2, v + 0.006, f"{v:.0%}", ha="center", fontsize=12)
for xi in x: ax.text(xi - w / 2, 0.006, "0", ha="center", fontsize=12, color=MUTED)
ax.set_xticks(x, FAC); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.set_ylabel("Units with fan wired backwards"); ax.set_ylim(0, 0.3); ax.legend(frameon=False, loc="upper right")
ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "04_fan_night_shift", "Fans wired backwards: 185 of 185 on the night shift",
     "Condenser Fan Backwards field failures by facility and shift. Zero on day shift at every facility.")

# 5. EOLT detection: every station sees the same mix
modes = ["Loose Terminal", "Refrigerant Leak", "Sensor Miswire", "Fan Rotation Error"]
mcol = [MUTED, ACCENT, ACCENT2, "#a3b1bf"]
fig, ax = plt.subplots(figsize=(11, 5.6)); fig.subplots_adjust(top=0.78)
left = np.zeros(4); st = list(STATION_MODE)
for m, c in zip(modes, mcol):
    v = np.array([STATION_MODE[s][m] / sum(STATION_MODE[s].values()) for s in st])
    ax.barh(st, v, left=left, color=c, label=m)
    for i, (l, vv) in enumerate(zip(left, v)):
        if vv > 0.07: ax.text(l + vv / 2, i, f"{vv:.0%}", ha="center", va="center", color="white", fontsize=11)
    left += v
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.set_xlim(0, 1)
ax.legend(ncol=4, frameon=False, bbox_to_anchor=(0, 1.0), loc="lower left", fontsize=11)
save(fig, "05_eolt_detection", "The Leak Test catches leaks no better than any other station",
     "Failure mode mix by EOLT station (chi-square p = 0.91). 74% of leaks were found at a non-leak station.")

# 6. Portfolio: cost vs 3-yr savings per investment (standalone) + chosen set
single = {s["id"]: s for s in R["single_investments"]}
chosen = [1, 2, 7, 9]
order = sorted(single, key=lambda i: -single[i]["y3"] / single[i]["cost"])
fig, ax = plt.subplots(figsize=(11.5, 6)); fig.subplots_adjust(top=0.84)
names = [f"{single[i]['name']} (${single[i]['cost']/1000:.0f}K)" for i in order]
vals = [single[i]["y3"] / single[i]["cost"] for i in order]
b = ax.barh(names[::-1], vals[::-1], color=[GOOD if i in chosen else "#cbd2d9" for i in order[::-1]])
for bb, i in zip(b, order[::-1]):
    ax.text(bb.get_width() + 0.2, bb.get_y() + bb.get_height() / 2, f"{single[i]['y3']/single[i]['cost']:.1f}x", va="center", fontsize=11)
ax.set_xlabel("3-year savings per $1 invested (standalone, implementation time included)")
ax.xaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "06_investment_returns", "Our $675K pick: four investments, each aimed at a cause we found",
     "Green = recommended portfolio. Grey = not picked (see brief for why). Catalog benefit estimates on our 2025 cost base.")

# 7. Cumulative cash flow + sensitivity
from analysis_core import steady_ids
months = np.arange(0, 37)
fig, ax = plt.subplots(figsize=(11, 5.6)); fig.subplots_adjust(top=0.84)
for scale, c, lab in [(1.0, GOOD, "100% of catalog benefit"), (0.5, ACCENT2, "50%"), (0.25, MUTED, "25%")]:
    cum = [-675000]
    for m in range(36): cum.append(cum[-1] + steady_ids(chosen, m, scale) / 12)
    ax.plot(months, np.array(cum) / 1e6, color=c, lw=2.5, label=lab)
ax.axhline(0, color=INK, lw=1)
ax.set_xlabel("Months after approval"); ax.set_ylabel("Cumulative net savings ($M)")
ax.legend(frameon=False, title="Benefit realized", loc="upper left"); ax.yaxis.grid(True, color=GRID); ax.set_axisbelow(True)
save(fig, "07_payback", "Pays back in month 9 and still pays back if only 25% of benefits arrive",
     "Cumulative net savings of the $675K portfolio; each investment counts only after its go-live month.")

# 8. Workflow diagram
fig = plt.figure(figsize=(13, 3.6)); ax = fig.add_axes([0, 0, 1, 0.86]); ax.axis("off"); ax.set_xlim(0, 13); ax.set_ylim(0, 3.2)
steps = [("1  Join", "5 datasets on\nSerial Number\n(3,000 = 3,000)"),
         ("2  Reconcile", "Leak = Brazing\nLoose Power =\nLoose Terminal"),
         ("3  Measure", "DPMO, cost per\nunit, rework\n& EOLT hours"),
         ("4  Root cause", "Rates by facility,\nsupplier, rev, shift\n(Fisher exact)"),
         ("5  Verify", "Confirmed vs\nsuspected, pilot\nbefore spending"),
         ("6  Optimize", "All 178 portfolios\nunder $750K,\ncompounded,\nstress-tested")]
for k, (h, t) in enumerate(steps):
    x0 = 0.15 + k * 2.15
    ax.add_patch(FancyBboxPatch((x0, 0.35), 1.85, 2.45, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#f5f7fa", ec=ACCENT if k in (3, 5) else GRID, lw=2))
    ax.text(x0 + 0.92, 2.45, h, ha="center", fontsize=13, fontweight="bold", color=INK)
    ax.text(x0 + 0.92, 1.35, t, ha="center", va="center", fontsize=10.5, color=INK)
    if k < 5: ax.annotate("", xy=(x0 + 2.12, 1.55), xytext=(x0 + 1.9, 1.55), arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.8))
save(fig, "08_workflow", "Our approach", None, source=False)

# 9. Robustness across scenarios
sc=["Base case","Rev A phased out","Poka-Yoke misses Rev A","Half the benefit","3-month ramp-up","Dashboard benefit halved"]
data={"Ours: Braze+Torque+Leak Det.+Supplier ($675K)":[8.16,8.16,8.16,4.04,7.87,8.16],
      "Torque+Poka-Yoke+Dashboard+Leak Det. ($725K)":[8.89,7.73,8.02,4.33,8.57,7.96],
      "Braze+Dashboard+Leak Det.+Supplier ($725K)":[8.78,8.48,8.78,4.57,8.46,7.89],
      "Torque+Poka-Yoke+Leak Det.+Supplier ($750K)":[8.75,7.76,7.76,4.21,8.43,8.75]}
best=[max(v[i] for v in data.values()) for i in range(len(sc))]
fig, ax = plt.subplots(figsize=(13, 5.8)); fig.subplots_adjust(top=0.80, left=0.33, bottom=0.25)
names=list(data)
M=np.array([[best[i]-data[n][i] for i in range(len(sc))] for n in names])
worst=M.max(axis=1)
ax.imshow(M, cmap="Reds", vmin=0, vmax=1.6, aspect="auto")
ax.set_xticks(range(len(sc)), sc, rotation=20, ha="right", fontsize=11); ax.set_yticks(range(len(names)), names, fontsize=11)
for i,n in enumerate(names):
    for j in range(len(sc)):
        ax.text(j,i,f"${data[n][j]:.2f}M"+("\n(best)" if M[i,j]<0.005 else f"\n-{M[i,j]:.2f}"),ha="center",va="center",fontsize=10,color=INK)
for i,w in enumerate(worst):
    ax.text(len(sc)-0.35+0.6,i,f"-{w:.2f}",ha="center",va="center",fontsize=13,fontweight="bold",color=GOOD if w==worst.min() else ACCENT)
ax.text(len(sc)+0.25,-0.75,"Worst gap",ha="center",fontsize=11,fontweight="bold",color=INK)
ax.set_xlim(-0.5,len(sc)+0.75)
ax.spines[:].set_visible(False); ax.tick_params(length=0)
save(fig,"09_robustness","Our pick never falls more than $0.73M behind the best option",
     "3-year net savings ($M) by scenario for the 4 strongest of 178 portfolios, and how far each is behind that scenario's best. We pick the smallest worst gap.")
print("ok")
