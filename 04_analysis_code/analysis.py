import itertools, json
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu
from data import *

out = {}
# ---------- integrity checks ----------
cells_n = sum(v[0] for v in CELLS.values()); cells_wc = sum(v[1] for v in CELLS.values())
assert cells_n == 3000, cells_n
assert abs(cells_wc - TOTAL["warranty"]) < 5, cells_wc
assert sum(v[0] for v in BY_DESC.values()) == 3000
assert sum(FAC_SUP_N.values()) == 3000
out["checks"] = "cells sum to 3000 units and $%d warranty" % cells_wc

# ---------- quality metrics ----------
cat = {}
for d, v in BY_DESC.items():
    c = cat.setdefault(DESC_CAT[d], [0, 0, 0, 0, 0])
    c[0] += v[0]; c[1] += v[1]; c[2] += v[6]; c[3] += v[7]; c[4] += v[8]
LABOR_RATE = 45.0  # assumption: fully burdened $/h for rework + EOLT rework labor
metrics = {}
for k, (n, wc, lab, mat, eh) in cat.items():
    rework = (lab + eh) * LABOR_RATE + mat
    metrics[k] = dict(units=n, share_units=n / 3000, dpmo=round(n / 3000 * 1e6), warranty=wc,
                      warranty_share=wc / TOTAL["warranty"], warranty_per_unit=wc / n,
                      internal_rework_cost=round(rework), total_cost=round(wc + rework))
out["metrics_by_category"] = metrics
out["overall"] = dict(fpy_eolt=0.0, dpu=1.0, dpmo_3_opps=round(3000 / (3000 * 3) * 1e6),
                      warranty=TOTAL["warranty"],
                      internal_rework=round((TOTAL["labor_h"] + TOTAL["eolt_h"]) * LABOR_RATE + TOTAL["material"]),
                      repair_cost_is_half_of_warranty=round(TOTAL["repair"] / TOTAL["warranty"], 4))

# ---------- root cause 1: leaks = Supplier B (everywhere) + Facility 2 (any supplier) ----------
def rate(num, den): return num / den
nonF2 = [f for f in FAC if f != "Facility 2"]
b_nonF2 = (sum(FAC_SUP_LEAK[(f, "Supplier B")] for f in nonF2), sum(FAC_SUP_N[(f, "Supplier B")] for f in nonF2))
ac_nonF2 = (sum(FAC_SUP_LEAK[(f, s)] for f in nonF2 for s in ["Supplier A", "Supplier C"]),
            sum(FAC_SUP_N[(f, s)] for f in nonF2 for s in ["Supplier A", "Supplier C"]))
ac_F2 = (FAC_SUP_LEAK[("Facility 2", "Supplier A")] + FAC_SUP_LEAK[("Facility 2", "Supplier C")],
         FAC_SUP_N[("Facility 2", "Supplier A")] + FAC_SUP_N[("Facility 2", "Supplier C")])
b_F2 = (FAC_SUP_LEAK[("Facility 2", "Supplier B")], FAC_SUP_N[("Facility 2", "Supplier B")])
leak = dict(
    supplierB_outside_F2=dict(leaks=b_nonF2[0], units=b_nonF2[1], rate=rate(*b_nonF2)),
    supplierAC_outside_F2=dict(leaks=ac_nonF2[0], units=ac_nonF2[1], rate=rate(*ac_nonF2)),
    supplierAC_at_F2=dict(leaks=ac_F2[0], units=ac_F2[1], rate=rate(*ac_F2)),
    supplierB_at_F2=dict(leaks=b_F2[0], units=b_F2[1], rate=rate(*b_F2)),
    by_cell={f"{f}|{s}": round(FAC_SUP_LEAK[(f, s)] / FAC_SUP_N[(f, s)], 3) for f in FAC for s in SUP},
)
leak["fisher_B_vs_AC_outsideF2_p"] = fisher_exact([[b_nonF2[0], b_nonF2[1] - b_nonF2[0]],
                                                   [ac_nonF2[0], ac_nonF2[1] - ac_nonF2[0]]])[1]
leak["fisher_F2_vs_other_for_AC_p"] = fisher_exact([[ac_F2[0], ac_F2[1] - ac_F2[0]],
                                                    [ac_nonF2[0], ac_nonF2[1] - ac_nonF2[0]]])[1]
leak["warranty_supplierB_all"] = sum(v for (f, s), v in FAC_SUP_LEAK_WC.items() if s == "Supplier B")
leak["warranty_F2_supplierAC"] = FAC_SUP_LEAK_WC[("Facility 2", "Supplier A")] + FAC_SUP_LEAK_WC[("Facility 2", "Supplier C")]
leak["warranty_F2_all"] = sum(v for (f, s), v in FAC_SUP_LEAK_WC.items() if f == "Facility 2")
leak["warranty_total"] = sum(FAC_SUP_LEAK_WC.values())
out["leak"] = leak

# ---------- root cause 2: controls = Rev A ----------
ctab = [[REV_CONTROLS["Rev A"], REV_N["Rev A"] - REV_CONTROLS["Rev A"]],
        [0, REV_N["Rev B"] + REV_N["Rev C"]]]
out["controls"] = dict(revA_rate=283 / 894, revBC_rate=0.0, fisher_p=fisher_exact(ctab)[1],
                       warranty=BY_DESC["Sensor Fault"][1] + BY_DESC["Communication Fault"][1],
                       eolt_label="Sensor Miswire (all 283)", repair="Sensor Rewire (all 283)",
                       by_facility=REV_CONTROLS_BY_FAC)

# ---------- root cause 3: fan backwards = night shift ----------
ftab = [[185, 1199 - 185], [0, 1801]]
out["fan"] = dict(night_rate=185 / 1199, day_rate=0.0, fisher_p=fisher_exact(ftab)[1],
                  night_rate_by_fac={f: round(FAN_NIGHT_BY_FAC[f] / FAC_SHIFT_N[(f, "Night")], 3) for f in FAC},
                  warranty=BY_DESC["Condenser Fan Backwards"][1],
                  eolt_fan_errors_all_night=FAN_EOLT_ALL_NIGHT, fan_corrections_all_night=FAN_REPAIR_ALL_NIGHT)

# ---------- loose power wiring: plant-wide ----------
out["loose_wiring"] = dict(units=1744, warranty=BY_DESC["Loose Power Wiring"][1],
                           rework_labor_h=BY_DESC["Loose Power Wiring"][6], material=BY_DESC["Loose Power Wiring"][7],
                           by_fac_rate={f: round(LOOSE_WIRING_BY_FAC[f] / FAC_N[f], 3) for f in FAC},
                           note="present at every facility, shift, supplier, family: process-wide fastening issue")

# ---------- detection / test gaps ----------
st = np.array([[STATION_MODE[s][m] for m in ["Loose Terminal", "Refrigerant Leak", "Sensor Miswire", "Fan Rotation Error"]]
               for s in STATION_MODE])
chi2, p, dof, _ = chi2_contingency(st)
leak_by_station = {s: round(STATION_MODE[s]["Refrigerant Leak"] / sum(STATION_MODE[s].values()), 3) for s in STATION_MODE}
misdiag = DESC_VS_EOLT[("Loose Power Wiring", "Fan Rotation Error")] + DESC_VS_EOLT[("Condenser Fan Backwards", "Loose Terminal")]
out["detection"] = dict(station_vs_mode_chi2=round(chi2, 2), p=p, leak_share_by_station=leak_by_station,
                        leaks_caught_outside_leak_test=(788 - 206) / 788,
                        eolt_misdiagnosed_wiring_vs_fan=misdiag, misdiag_share_of_wiring=misdiag / 1929,
                        wrong_repair_loose_wiring_given_fan_fix=181)
d = DISPO
out["disposition"] = {k: {c: dict(n=v[0], wc_per_unit=round(v[1] / v[0])) for c, v in d[k].items()} for k in d}

# ---------- LegacyX ----------
out["legacyx"] = dict(warranty_per_unit=FAM_WC["LegacyX"] / FAM_N["LegacyX"],
                      others_per_unit=(sum(FAM_WC.values()) - FAM_WC["LegacyX"]) / (3000 - FAM_N["LegacyX"]),
                      leak_cost_per_unit=FAM_LEAK["LegacyX"][1] / FAM_LEAK["LegacyX"][0],
                      leak_cost_per_unit_others=sum(v[1] for k, v in FAM_LEAK.items() if k != "LegacyX") /
                                                sum(v[0] for k, v in FAM_LEAK.items() if k != "LegacyX"),
                      leak_share=FAM_LEAK["LegacyX"][0] / FAM_N["LegacyX"],
                      leak_share_others=sum(v[0] for k, v in FAM_LEAK.items() if k != "LegacyX") / (3000 - FAM_N["LegacyX"]),
                      total_warranty=FAM_WC["LegacyX"])

# ---------- ROI model ----------
# Each investment: cost, months to implement, warranty reduction by cell, rework (defect) reduction by cell
def is_(g): return lambda c: c[0] == g
def any_(*gs): return lambda c: c[0] in gs
ALL = lambda c: True
INV = [
 # id, name, cost, months, risk, [(warranty_rate, selector)], [(defect_rate, selector)], data_link
 (1, "Braze Process Training", 50_000, 2, "Low", [(0.05, is_("Leak"))], [(0.10, is_("Leak"))]),
 (2, "Smart Torque Tools", 100_000, 3, "Low", [(0.15, is_("LoosePower"))], [(0.30, is_("LoosePower"))]),
 (3, "Wiring Poka-Yoke", 125_000, 4, "Low", [(0.40, any_("Controls", "Fan"))], [(0.40, any_("Controls", "Fan"))]),
 (4, "Predictive Quality Dashboard", 150_000, 6, "Medium", [(0.15, ALL)], []),
 (5, "Enhanced Design Validation", 200_000, 6, "Medium", [(0.20, is_("Controls"))], [(0.20, is_("Controls"))]),
 (6, "Vision Inspection System", 275_000, 6, "Medium", [(0.35, any_("LoosePower", "Fan", "Controls"))], [(0.35, any_("LoosePower", "Fan", "Controls"))]),
 (7, "Automated Leak Detection", 350_000, 8, "Low", [(0.40, is_("Leak"))], []),
 (8, "Additional EOLT Station", 450_000, 8, "Medium", [(0.15, ALL)], []),
 (9, "Supplier Quality Program", 175_000, 4, "Medium", [(0.25, lambda c: c[0] == "Leak" and c[1] == "B")], [(0.25, lambda c: c[0] == "Leak" and c[1] == "B")]),
 (10, "LegacyX Product Refresh", 500_000, 12, "High", [(0.35, lambda c: c[2] == "Lx")], []),
]
BUDGET = 750_000

def savings(selection, horizon_months=12, scale=1.0):
    """Annual-rate cost base = 2025 data. Benefits compound multiplicatively within each unit cell.
    Benefit accrues only after implementation: fraction of horizon after go-live."""
    total_w = total_r = 0.0
    for c, (n, wc, lab, mat, eh) in CELLS.items():
        rework = (lab + eh) * LABOR_RATE + mat
        rw_w = rw_r = 1.0
        for inv in selection:
            _, _, _, m, _, wr, dr = inv
            live = max(0, horizon_months - m) / horizon_months
            for r, sel in wr:
                if sel(c): rw_w *= (1 - r * scale * live)
            for r, sel in dr:
                if sel(c): rw_r *= (1 - r * scale * live)
        total_w += wc * (1 - rw_w); total_r += rework * (1 - rw_r)
    years = horizon_months / 12
    return (total_w + total_r) * years, total_w * years, total_r * years

def steady(selection, scale=1.0):  # full-run-rate annual savings after all live
    total = 0.0
    for c, (n, wc, lab, mat, eh) in CELLS.items():
        rework = (lab + eh) * LABOR_RATE + mat
        rw_w = rw_r = 1.0
        for inv in selection:
            for r, sel in inv[5]:
                if sel(c): rw_w *= (1 - r * scale)
            for r, sel in inv[6]:
                if sel(c): rw_r *= (1 - r * scale)
        total += wc * (1 - rw_w) + rework * (1 - rw_r)
    return total

def year_by_year(selection, scale=1.0):
    """Savings in each of years 1..3 accounting for go-live month (months 1..36)."""
    res = []
    for y in range(3):
        s = 0.0
        for month in range(12 * y, 12 * y + 12):
            live = [inv for inv in selection if month >= inv[3]]
            s += steady(live, scale) / 12
        res.append(s)
    return res

rows = []
for k in range(1, len(INV) + 1):
    for combo in itertools.combinations(INV, k):
        cost = sum(i[2] for i in combo)
        if cost > BUDGET: continue
        yy = year_by_year(combo)
        rows.append(dict(ids=[i[0] for i in combo], names=[i[1] for i in combo], cost=cost,
                         y1=yy[0], y3=sum(yy), run_rate=steady(combo),
                         roi_y1=(yy[0] - cost) / cost, roi_3y=(sum(yy) - cost) / cost,
                         payback_months=None))
rows.sort(key=lambda r: -(r["y3"] - r["cost"]))
out["n_portfolios_evaluated"] = len(rows)
out["top_by_3yr_net"] = [{k: (round(v) if isinstance(v, float) and k not in ("roi_y1", "roi_3y") else (round(v, 2) if isinstance(v, float) else v)) for k, v in r.items()} for r in rows[:8]]
rows_y1 = sorted(rows, key=lambda r: -(r["y1"] - r["cost"]))
out["top_by_y1_net"] = [{k: (round(v) if isinstance(v, float) and k not in ("roi_y1", "roi_3y") else (round(v, 2) if isinstance(v, float) else v)) for k, v in r.items()} for r in rows_y1[:5]]

# standalone value of each investment
single = []
for inv in INV:
    yy = year_by_year([inv])
    single.append(dict(id=inv[0], name=inv[1], cost=inv[2], months=inv[3], risk=inv[4],
                       run_rate=round(steady([inv])), y1=round(yy[0]), y3=round(sum(yy)),
                       roi_3y=round((sum(yy) - inv[2]) / inv[2], 2)))
out["single_investments"] = single
json.dump(out, open("results.json", "w"), indent=1, default=float)

# pretty print
print(json.dumps({k: out[k] for k in ["checks", "overall", "metrics_by_category", "leak", "controls", "fan",
                                      "loose_wiring", "detection", "disposition", "legacyx"]}, indent=1, default=float))
print("\nSINGLE INVESTMENTS")
for s in single: print(s)
print("\nPortfolios evaluated:", len(rows))
print("TOP BY 3-YEAR NET")
for r in rows[:8]:
    print(r["ids"], r["cost"], "y1=%d y3=%d run=%d roi3=%.2f" % (r["y1"], r["y3"], r["run_rate"], r["roi_3y"]))
print("TOP BY YEAR-1 NET")
for r in rows_y1[:5]:
    print(r["ids"], r["cost"], "y1=%d y3=%d run=%d roi1=%.2f" % (r["y1"], r["y3"], r["run_rate"], r["roi_y1"]))
