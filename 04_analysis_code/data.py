"""Aggregates extracted from the 5 Airedale competition datasets (3,000 units, serials verified aligned).
Extracted in-browser from Canvas files; every figure below is a direct count or sum from the raw rows."""

FAC = ["Facility 1", "Facility 2", "Facility 3", "Facility 4"]
SUP = ["Supplier A", "Supplier B", "Supplier C"]

# by field failure description: n, warranty $, repair $, downtime h, sum days_to_failure, service h,
# rework labor h, rework material $, EOLT rework h
BY_DESC = {
    "Loose Power Wiring":      (1744, 947516, 473344, 21906, 216120, 21890, 5683.0, 459630, 3667.2),
    "Service Valve Leak":      (270, 2007242, 1003551, 3469, 34355, 3284, 797.0, 74445, 536.3),
    "Suction Leak":            (268, 1955509, 977693, 3391, 34236, 3659, 859.1, 69152, 595.9),
    "Refrigerant Leak":        (250, 1821674, 910774, 3072, 31226, 3079, 802.3, 69694, 528.5),
    "Condenser Fan Backwards": (185, 136427, 68171, 2315, 22943, 2592, 615.1, 49899, 371.2),
    "Communication Fault":     (143, 375631, 187780, 1633, 18407, 1778, 447.9, 35003, 287.7),
    "Sensor Fault":            (140, 409478, 204708, 1825, 17924, 1820, 453.4, 36561, 287.3),
}
DESC_CAT = {"Loose Power Wiring": "Wiring", "Condenser Fan Backwards": "Wiring",
            "Service Valve Leak": "Leak", "Suction Leak": "Leak", "Refrigerant Leak": "Leak",
            "Communication Fault": "Controls", "Sensor Fault": "Controls"}

# units per facility x supplier, and failure category counts per facility x supplier
FAC_SUP_N = {("Facility 1", "Supplier A"): 271, ("Facility 1", "Supplier B"): 221, ("Facility 1", "Supplier C"): 256,
             ("Facility 2", "Supplier A"): 264, ("Facility 2", "Supplier B"): 248, ("Facility 2", "Supplier C"): 272,
             ("Facility 3", "Supplier A"): 264, ("Facility 3", "Supplier B"): 212, ("Facility 3", "Supplier C"): 276,
             ("Facility 4", "Supplier A"): 240, ("Facility 4", "Supplier B"): 213, ("Facility 4", "Supplier C"): 263}
FAC_SUP_LEAK = {("Facility 1", "Supplier A"): 0, ("Facility 1", "Supplier B"): 123, ("Facility 1", "Supplier C"): 0,
                ("Facility 2", "Supplier A"): 153, ("Facility 2", "Supplier B"): 142, ("Facility 2", "Supplier C"): 137,
                ("Facility 3", "Supplier A"): 0, ("Facility 3", "Supplier B"): 112, ("Facility 3", "Supplier C"): 0,
                ("Facility 4", "Supplier A"): 0, ("Facility 4", "Supplier B"): 121, ("Facility 4", "Supplier C"): 0}
FAC_SUP_LEAK_WC = {("Facility 1", "Supplier B"): 921423, ("Facility 3", "Supplier B"): 800010,
                   ("Facility 4", "Supplier B"): 865595, ("Facility 2", "Supplier A"): 1138201,
                   ("Facility 2", "Supplier C"): 993734, ("Facility 2", "Supplier B"): 1065462}

# controls revision
REV_N = {"Rev A": 894, "Rev B": 1041, "Rev C": 1065}
REV_CONTROLS = {"Rev A": 283, "Rev B": 0, "Rev C": 0}
REV_CONTROLS_BY_FAC = {"Facility 1": 70, "Facility 2": 39, "Facility 3": 83, "Facility 4": 91}

# shift
SHIFT_N = {"Day": 1801, "Night": 1199}
FAN_BY_SHIFT = {"Day": 0, "Night": 185}
FAN_NIGHT_BY_FAC = {"Facility 1": 74, "Facility 2": 23, "Facility 3": 42, "Facility 4": 46}
FAC_SHIFT_N = {("Facility 1", "Day"): 437, ("Facility 1", "Night"): 311, ("Facility 2", "Day"): 487,
               ("Facility 2", "Night"): 297, ("Facility 3", "Day"): 445, ("Facility 3", "Night"): 307,
               ("Facility 4", "Day"): 432, ("Facility 4", "Night"): 284}
FAN_EOLT_ALL_NIGHT = 181      # EOLT "Fan Rotation Error": all night shift
FAN_REPAIR_ALL_NIGHT = 366    # Rework "Fan Rotation Correction": all night shift
LOOSE_WIRING_BY_FAC = {"Facility 1": 481, "Facility 2": 290, "Facility 3": 515, "Facility 4": 458}
FAC_N = {"Facility 1": 748, "Facility 2": 784, "Facility 3": 752, "Facility 4": 716}

# family
FAM_N = {"DC100": 739, "DC200": 771, "DC300": 924, "LegacyX": 566}
FAM_WC = {"DC100": 1765707, "DC200": 1847487, "DC300": 2127242, "LegacyX": 1913041}
FAM_LEAK = {"DC100": (200, 1367219), "DC200": (199, 1360374), "DC300": (247, 1625410), "LegacyX": (142, 1431422)}

# EOLT station x failure mode (counts)
STATION_MODE = {
    "Leak Test":       {"Loose Terminal": 435, "Refrigerant Leak": 206, "Sensor Miswire": 73, "Fan Rotation Error": 44},
    "Controls Test":   {"Loose Terminal": 421, "Refrigerant Leak": 204, "Sensor Miswire": 64, "Fan Rotation Error": 45},
    "Electrical Test": {"Loose Terminal": 434, "Refrigerant Leak": 176, "Sensor Miswire": 76, "Fan Rotation Error": 45},
    "Functional Test": {"Loose Terminal": 458, "Refrigerant Leak": 202, "Sensor Miswire": 70, "Fan Rotation Error": 47},
}
# field description vs EOLT failure mode / rework repair type (label reconciliation + misdiagnosis)
DESC_VS_EOLT = {("Loose Power Wiring", "Loose Terminal"): 1661, ("Loose Power Wiring", "Fan Rotation Error"): 83,
                ("Condenser Fan Backwards", "Fan Rotation Error"): 98, ("Condenser Fan Backwards", "Loose Terminal"): 87}
DESC_VS_REPAIR = {("Loose Power Wiring", "Rewire"): 1563, ("Loose Power Wiring", "Fan Rotation Correction"): 181,
                  ("Condenser Fan Backwards", "Fan Rotation Correction"): 185}

# disposition (n, warranty $) by category
DISPO = {"Rework Completed": {"Wiring": (939, 522310), "Leak": (397, 2970303), "Controls": (153, 435475)},
         "Use As Is":        {"Wiring": (990, 561633), "Leak": (391, 2814122), "Controls": (130, 349634)}}

# Unit cells for ROI: (group, supplierB?, LegacyX?, Facility2?) -> n, warranty $, rework labor h, material $, EOLT rework h
CELLS = {
 ("Controls","nB","nLx","nF2"):(175,443230,543.9,43605,348.5), ("LoosePower","nB","nLx","nF2"):(985,484553,3166.9,261579,2062.5),
 ("Controls","nB","nLx","F2"):(23,60884,69.5,6025,47.1), ("Leak","B","nLx","nF2"):(292,1941391,953,78376,623.3),
 ("LoosePower","B","nLx","nF2"):(190,87903,624.4,51146,420.4), ("LoosePower","B","nLx","F2"):(69,32626,240.6,19382,149.5),
 ("Controls","nB","Lx","F2"):(10,39657,36.8,2884,20.6), ("Controls","B","Lx","nF2"):(6,20129,18.2,1956,13.8),
 ("Fan","nB","nLx","nF2"):(110,78018,358.9,29584,215), ("LoosePower","nB","Lx","nF2"):(237,178094,779.7,62745,481.4),
 ("Leak","nB","nLx","F2"):(238,1603816,745.5,65020,509.1), ("Leak","nB","Lx","F2"):(52,528119,140.2,14452,108.8),
 ("Controls","B","nLx","F2"):(5,12297,14.2,507,10.5), ("LoosePower","nB","nLx","F2"):(159,81457,526.4,37347,347),
 ("Leak","B","Lx","nF2"):(64,645637,198.4,17806,136), ("LoosePower","nB","Lx","F2"):(42,35680,149.8,11752,97.9),
 ("Controls","B","nLx","nF2"):(29,78090,94.9,8380,57.3), ("Leak","B","Lx","F2"):(26,257666,75.7,7990,51.3),
 ("Fan","nB","Lx","nF2"):(29,27414,109.2,8832,63.2), ("Controls","nB","Lx","nF2"):(34,125697,120.6,7927,75.1),
 ("Fan","B","nLx","nF2"):(21,14665,66,5084,42), ("LoosePower","B","Lx","F2"):(20,15134,68,5060,33),
 ("LoosePower","B","Lx","nF2"):(42,32069,127,10619,76), ("Leak","B","nLx","F2"):(116,807796,346,29647,232),
 ("Fan","B","nLx","F2"):(10,6646,27,2371,21), ("Fan","B","Lx","F2"):(1,552,5,497,4),
 ("Fan","nB","nLx","F2"):(12,7064,43,2920,23), ("Fan","B","Lx","nF2"):(2,2068,7,611,4),
 ("Controls","B","Lx","F2"):(1,5125,3,280,2),
}
TOTAL = dict(n=3000, warranty=7653477, repair=3826021, downtime=37611, labor_h=9657.8, material=794384, eolt_h=6274.1)
