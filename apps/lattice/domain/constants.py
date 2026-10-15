"""Domain constants: the vocabulary of the dataset. No framework or ML imports here."""

TOPOLOGIES = {
    "Honeycomb": "Honeycomb",
    "Auxetic_Honeycomb": "Auxetic honeycomb",
    "Chiral": "Chiral",
    "Star_Reentrant": "Star re-entrant",
}
# Angles actually present in the dataset for each topology (the model cannot be trusted elsewhere).
ANGLES = {"Honeycomb": [0], "Auxetic_Honeycomb": [-20, -15], "Chiral": [0, 15], "Star_Reentrant": [-15]}

# default nozzle temperature and fibre content come from the material; E/nu are typical bulk values
# used ONLY for the ANSYS template. Replace them with your own coupon data.
MATERIALS = {
    "PLA":    {"label": "PLA",                "nozzle": 210, "fibre_wt": 0,  "E": 3500, "nu": 0.36},
    "PLA_CF": {"label": "PLA + carbon fibre", "nozzle": 210, "fibre_wt": 15, "E": 6500, "nu": 0.34},
    "ABS":    {"label": "ABS",                "nozzle": 230, "fibre_wt": 0,  "E": 2200, "nu": 0.35},
    "CF_ABS": {"label": "ABS + carbon fibre", "nozzle": 230, "fibre_wt": 15, "E": 4500, "nu": 0.33},
}

# (min, max, step) of each continuous input, taken from the dataset coverage
RANGES = {
    "cell_size": (5, 25, 1),
    "wall_thickness": (0.5, 1.5, 0.1),
    "layer_thickness": (0.1, 0.3, 0.05),
    "nozzle_temp": (200, 240, 5),
}

# key -> (dataset column, label, unit, log-transform during training)
TARGETS = {
    "E":   ("Elastic_Modulus_MPa", "Elastic modulus", "MPa", True),
    "UTS": ("UTS_MPa", "Tensile strength (UTS)", "MPa", True),
    "CPS": ("Compressive_Peak_Stress_MPa", "Compressive peak stress", "MPa", True),
    "NU":  ("Poisson_Ratio", "Poisson ratio", "", False),
    "SEA": ("Specific_Energy_Absorption_Jg", "Energy absorption (SEA)", "J/g", False),
    "RHO": ("Relative_Density_pct", "Relative density", "%", False),
}

# model input columns, in the order the pipelines expect them
NUMERIC_FEATURES = ["Cell_Size_L_mm", "Wall_Thickness_T_mm", "Reentrant_Angle_deg", "Layer_Thickness_mm", "Nozzle_Temp_C"]
CATEGORICAL_FEATURES = ["Topology_Type", "Material"]
DEPLOYED_MODEL = "SVR(RBF)"
