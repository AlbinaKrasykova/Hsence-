"""Four interrelated health layers for precision recommendations."""

HEALTH_LAYERS = {
    "hormones": {
        "label": "Hormones & endocrine",
        "description": "Sex hormones, thyroid signals, cycle/anovulation patterns",
        "marker_keys": [
            "LH",
            "FSH",
            "LH:FSH ratio",
            "Total testosterone",
            "Free testosterone (calculated)",
            "SHBG",
            "Progesterone",
            "TSH",
            "Free T4",
        ],
    },
    "metabolic": {
        "label": "Metabolic & cardiovascular",
        "description": "Glucose, insulin, lipids, hepatic fat risk",
        "marker_keys": [
            "Fasting glucose",
            "Fasting insulin",
            "HOMA-IR (calculated)",
            "HbA1c",
            "LDL cholesterol",
            "HDL cholesterol",
            "Triglycerides",
            "Total cholesterol",
        ],
    },
    "cognition": {
        "label": "Cognition & recovery",
        "description": "Sleep, energy, iron, vitamin D, mood load",
        "marker_keys": [
            "Vitamin D (25-OH)",
            "Ferritin",
            "Vitamin B12",
            "Folate (serum)",
            "Haemoglobin",
        ],
    },
    "inflammation": {
        "label": "Inflammation & gut",
        "description": "CRP, inflammatory food triggers, recovery capacity",
        "marker_keys": ["CRP", "ESR", "Thyroid peroxidase antibodies"],
    },
}
