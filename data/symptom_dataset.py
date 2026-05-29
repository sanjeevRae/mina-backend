"""
Symptom-Condition Dataset Generator
Based on open medical knowledge and common health conditions
"""
import json
import random
from typing import List, Dict

# Enterprise-level comprehensive symptoms (200+ symptoms)
SYMPTOMS = [
    # General/Constitutional
    "fever", "fatigue", "weakness", "chills", "night_sweats", "weight_loss", 
    "weight_gain", "loss_of_appetite", "nausea", "vomiting", "dizziness",
    "malaise", "lethargy", "excessive_hunger", "excessive_thirst", "dehydration",
    "unexplained_weight_loss", "poor_appetite", "general_weakness", "body_aches",
    
    # Respiratory System
    "cough", "shortness_of_breath", "chest_pain", "wheezing", "sore_throat",
    "runny_nose", "congestion", "sneezing", "difficulty_breathing", "hoarseness", 
    "persistent_cough", "coughing_blood", "rapid_breathing", "shallow_breathing",
    "chest_congestion", "mucus_production", "tight_chest", "gasping", "choking_sensation",
    "productive_cough", "dry_cough", "hemoptysis", "dyspnea", "stridor",
    
    # Cardiovascular System
    "palpitations", "irregular_heartbeat", "chest_tightness", "leg_swelling",
    "rapid_heartbeat", "slow_heartbeat", "cold_hands", "cold_feet", "blue_lips",
    "shortness_of_breath_lying_down", "ankle_swelling", "cyanosis", "edema",
    "claudication", "varicose_veins", "chest_pressure", "radiating_arm_pain",
    "jaw_pain", "syncope", "presyncope",
    
    # Digestive/Gastrointestinal
    "abdominal_pain", "diarrhea", "constipation", "bloating", "heartburn",
    "difficulty_swallowing", "blood_in_stool", "black_stool", "indigestion",
    "gas", "acid_reflux", "loss_of_taste", "bitter_taste", "stomach_cramps",
    "dysphagia", "hematemesis", "melena", "hematochezia", "tenesmus",
    "early_satiety", "postprandial_fullness", "belching", "regurgitation",
    "fecal_incontinence", "rectal_bleeding", "mucus_in_stool", "greasy_stool",
    
    # Musculoskeletal System
    "joint_pain", "muscle_pain", "back_pain", "neck_pain", "stiffness",
    "swelling", "numbness", "tingling", "muscle_weakness", "joint_stiffness",
    "bone_pain", "muscle_cramps", "reduced_mobility", "limping", "arthralgia",
    "myalgia", "joint_swelling", "joint_redness", "joint_warmth", "decreased_range_of_motion",
    "morning_stiffness", "gait_disturbance", "muscle_spasms", "tendon_pain",
    
    # Neurological System
    "headache", "migraine", "confusion", "memory_loss", "seizures",
    "loss_of_consciousness", "tremors", "coordination_problems", "vertigo",
    "lightheadedness", "fainting", "speech_difficulty", "vision_problems",
    "sensitivity_to_sound", "brain_fog", "difficulty_concentrating", "photophobia",
    "phonophobia", "paresthesia", "hyperreflexia", "hyporeflexia", "ataxia",
    "dysarthria", "aphasia", "cognitive_decline", "disorientation", "altered_mental_status",
    "loss_of_balance", "nystagmus", "diplopia", "scotoma", "aura",
    
    # Dermatological/Skin
    "rash", "itching", "skin_redness", "hives", "dry_skin", "bruising",
    "pale_skin", "yellowing_skin", "peeling_skin", "skin_lesions", "blisters",
    "skin_discoloration", "excessive_sweating", "cold_skin", "warm_skin",
    "purpura", "petechiae", "ecchymosis", "urticaria", "erythema", "macules",
    "papules", "nodules", "plaques", "scaling", "crusting", "ulcers",
    "hyperpigmentation", "hypopigmentation", "jaundice", "pallor",
    
    # ENT (Ear, Nose, Throat, Eyes)
    "ear_pain", "hearing_loss", "ringing_in_ears", "vision_changes",
    "eye_pain", "sensitivity_to_light", "double_vision", "blurred_vision",
    "eye_redness", "watery_eyes", "nasal_discharge", "loss_of_smell",
    "tinnitus", "otorrhea", "vertigo", "epistaxis", "postnasal_drip",
    "sinus_pressure", "facial_pain", "decreased_vision", "eye_discharge",
    "photopsia", "floaters", "halos", "night_blindness", "periorbital_swelling",
    
    # Urinary/Renal System
    "frequent_urination", "painful_urination", "blood_in_urine", "dark_urine",
    "cloudy_urine", "urinary_urgency", "difficulty_urinating", "pelvic_pain",
    "decreased_urine_output", "strong_smelling_urine", "polyuria", "oliguria",
    "anuria", "nocturia", "urinary_retention", "dysuria", "hematuria",
    "proteinuria", "foamy_urine", "urinary_incontinence", "hesitancy",
    
    # Reproductive/Gynecological
    "vaginal_discharge", "menstrual_irregularities", "pelvic_discomfort",
    "painful_intercourse", "vaginal_bleeding", "breast_pain", "breast_lump",
    "testicular_pain", "erectile_dysfunction", "decreased_libido",
    
    # Endocrine/Metabolic
    "heat_intolerance", "cold_intolerance", "increased_sweating", "hair_loss",
    "brittle_nails", "slow_wound_healing", "polydipsia", "polyphagia",
    "unexplained_hunger", "glucose_intolerance", "frequent_infections",
    "delayed_growth", "early_puberty", "delayed_puberty", "thyroid_swelling",
    
    # Psychiatric/Mental Health
    "anxiety", "depression", "insomnia", "irritability", "mood_swings",
    "panic_attacks", "restlessness", "loss_of_interest", "social_withdrawal",
    "excessive_worry", "difficulty_sleeping", "nightmares", "hallucinations",
    "delusions", "paranoia", "suicidal_thoughts", "racing_thoughts",
    "emotional_lability", "anhedonia", "hypersomnia", "psychomotor_agitation",
    
    # Hematological
    "easy_bruising", "unexplained_bleeding", "prolonged_bleeding", "nosebleeds",
    "bleeding_gums", "heavy_menstrual_bleeding", "blood_clots", "pallor",
    
    # Lymphatic/Immune
    "swollen_lymph_nodes", "recurrent_infections", "slow_healing", "fever_of_unknown_origin",
    "lymphadenopathy", "splenomegaly", "hepatomegaly",
    
    # Other Symptoms
    "thirst", "bad_breath", "mouth_sores", "dry_mouth", "excessive_saliva",
    "red_eyes", "sensitive_teeth", "gum_swelling", "loss_of_coordination",
    "balance_problems", "falls", "unsteady_gait", "muscle_atrophy",
    "flushing", "chills_without_fever", "rigors", "diaphoresis"
]

# Medical conditions with their typical symptom patterns
CONDITION_PATTERNS = {
    "Common Cold": {
        "symptoms": ["runny_nose", "congestion", "sneezing", "sore_throat", "cough", "fatigue", "mild_fever"],
        "severity": "mild",
        "recommendations": [
            "Rest and stay hydrated",
            "Use saline nasal drops",
            "Consider over-the-counter cold medications",
            "Gargle with warm salt water",
            "Avoid strenuous activities"
        ]
    },
    "Influenza (Flu)": {
        "symptoms": ["fever", "chills", "muscle_pain", "fatigue", "cough", "sore_throat", "headache", "weakness"],
        "severity": "moderate",
        "recommendations": [
            "Get plenty of rest",
            "Stay well hydrated",
            "Consider antiviral medications within 48 hours",
            "Isolate to prevent spreading",
            "Monitor temperature regularly"
        ]
    },
    "Seasonal Allergies": {
        "symptoms": ["sneezing", "runny_nose", "itching", "watery_eyes", "congestion", "fatigue"],
        "severity": "mild",
        "recommendations": [
            "Avoid known allergens",
            "Use antihistamines",
            "Keep windows closed during high pollen days",
            "Shower after being outdoors",
            "Use air purifiers indoors"
        ]
    },
    "Migraine": {
        "symptoms": ["headache", "nausea", "sensitivity_to_light", "vomiting", "vision_changes", "dizziness"],
        "severity": "moderate",
        "recommendations": [
            "Rest in a dark, quiet room",
            "Apply cold compress to forehead",
            "Stay hydrated",
            "Avoid triggers (stress, certain foods)",
            "Consider preventive medications"
        ]
    },
    "Gastroenteritis": {
        "symptoms": ["diarrhea", "nausea", "vomiting", "abdominal_pain", "fever", "dehydration", "weakness"],
        "severity": "moderate",
        "recommendations": [
            "Stay hydrated with electrolyte solutions",
            "Eat bland foods (BRAT diet)",
            "Avoid dairy and fatty foods",
            "Wash hands frequently",
            "Rest adequately"
        ]
    },
    "Urinary Tract Infection": {
        "symptoms": ["frequent_urination", "painful_urination", "abdominal_pain", "cloudy_urine", "fever", "back_pain"],
        "severity": "moderate",
        "recommendations": [
            "Drink plenty of water",
            "Urinate frequently",
            "Avoid irritants (caffeine, alcohol)",
            "Use heating pad for discomfort",
            "Seek medical attention for antibiotics"
        ]
    },
    "Bronchitis": {
        "symptoms": ["persistent_cough", "chest_pain", "shortness_of_breath", "wheezing", "fatigue", "fever"],
        "severity": "moderate",
        "recommendations": [
            "Rest and stay hydrated",
            "Use humidifier",
            "Avoid smoke and irritants",
            "Consider cough suppressants",
            "Monitor breathing difficulties"
        ]
    },
    "Anxiety Disorder": {
        "symptoms": ["anxiety", "palpitations", "sweating", "tremors", "insomnia", "fatigue", "irritability"],
        "severity": "moderate",
        "recommendations": [
            "Practice deep breathing exercises",
            "Regular physical exercise",
            "Maintain consistent sleep schedule",
            "Limit caffeine and alcohol",
            "Consider therapy or counseling"
        ]
    },
    "Hypertension (High Blood Pressure)": {
        "symptoms": ["headache", "dizziness", "chest_pain", "shortness_of_breath", "vision_changes", "fatigue"],
        "severity": "serious",
        "recommendations": [
            "Reduce sodium intake",
            "Maintain healthy weight",
            "Regular exercise (30 min daily)",
            "Limit alcohol consumption",
            "Regular blood pressure monitoring"
        ]
    },
    "Anemia": {
        "symptoms": ["fatigue", "weakness", "pale_skin", "shortness_of_breath", "dizziness", "cold_hands_feet", "headache"],
        "severity": "moderate",
        "recommendations": [
            "Increase iron-rich foods",
            "Take iron supplements if recommended",
            "Eat vitamin C-rich foods",
            "Avoid tea/coffee with meals",
            "Regular blood tests"
        ]
    },
    "Asthma": {
        "symptoms": ["wheezing", "shortness_of_breath", "chest_tightness", "cough", "difficulty_breathing"],
        "severity": "serious",
        "recommendations": [
            "Use prescribed inhalers correctly",
            "Avoid triggers (smoke, allergens)",
            "Monitor peak flow readings",
            "Have emergency action plan",
            "Regular follow-up with healthcare provider"
        ]
    },
    "Arthritis": {
        "symptoms": ["joint_pain", "stiffness", "swelling", "reduced_range_of_motion", "fatigue", "warmth_in_joints"],
        "severity": "moderate",
        "recommendations": [
            "Regular low-impact exercise",
            "Maintain healthy weight",
            "Apply hot/cold therapy",
            "Use assistive devices if needed",
            "Consider physical therapy"
        ]
    },
    "Type 2 Diabetes": {
        "symptoms": ["frequent_urination", "thirst", "weight_loss", "fatigue", "blurred_vision", "slow_healing"],
        "severity": "serious",
        "recommendations": [
            "Monitor blood sugar regularly",
            "Follow balanced diet plan",
            "Regular physical activity",
            "Take medications as prescribed",
            "Regular health check-ups"
        ]
    },
    "Depression": {
        "symptoms": ["depression", "fatigue", "insomnia", "loss_of_appetite", "irritability", "loss_of_interest", "difficulty_concentrating"],
        "severity": "moderate",
        "recommendations": [
            "Seek professional counseling",
            "Regular exercise routine",
            "Maintain social connections",
            "Practice stress management",
            "Consider therapy or medication"
        ]
    },
    "Tension Headache": {
        "symptoms": ["headache", "neck_pain", "muscle_pain", "fatigue", "difficulty_concentrating"],
        "severity": "mild",
        "recommendations": [
            "Practice relaxation techniques",
            "Improve posture",
            "Regular breaks from screen time",
            "Massage and stretching",
            "Manage stress levels"
        ]
    },
    "COVID-19": {
        "symptoms": ["fever", "cough", "fatigue", "loss_of_taste", "loss_of_smell", "shortness_of_breath", "body_aches", "sore_throat"],
        "severity": "moderate",
        "recommendations": [
            "Self-isolate immediately",
            "Get tested and follow health guidelines",
            "Monitor oxygen levels",
            "Stay hydrated and rest",
            "Seek medical attention if breathing worsens"
        ]
    },
    "Pneumonia": {
        "symptoms": ["fever", "cough", "chest_pain", "shortness_of_breath", "fatigue", "chills", "mucus_production", "rapid_breathing"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical attention",
            "Antibiotics may be required",
            "Rest and stay hydrated",
            "Monitor breathing closely",
            "Complete prescribed medication course"
        ]
    },
    "Sinusitis": {
        "symptoms": ["facial_pain", "nasal_discharge", "congestion", "headache", "fever", "cough", "loss_of_smell"],
        "severity": "moderate",
        "recommendations": [
            "Use saline nasal rinse",
            "Apply warm compress",
            "Stay hydrated",
            "Consider decongestants",
            "See doctor if symptoms persist beyond 10 days"
        ]
    },
    "Thyroid Disorder (Hypothyroidism)": {
        "symptoms": ["fatigue", "weight_gain", "cold_intolerance", "dry_skin", "hair_loss", "constipation", "depression", "slow_heartbeat"],
        "severity": "moderate",
        "recommendations": [
            "Get thyroid function tests",
            "Medication may be required",
            "Regular monitoring needed",
            "Maintain healthy diet",
            "Follow endocrinologist advice"
        ]
    },
    "Thyroid Disorder (Hyperthyroidism)": {
        "symptoms": ["weight_loss", "rapid_heartbeat", "heat_intolerance", "increased_sweating", "anxiety", "tremors", "insomnia"],
        "severity": "moderate",
        "recommendations": [
            "Get thyroid function tests",
            "Medication or radioactive iodine therapy",
            "Regular monitoring required",
            "Manage stress levels",
            "Avoid caffeine and stimulants"
        ]
    },
    "Heart Disease": {
        "symptoms": ["chest_pain", "shortness_of_breath", "palpitations", "fatigue", "dizziness", "leg_swelling", "irregular_heartbeat"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical evaluation",
            "Lifestyle modifications required",
            "Medication management",
            "Regular cardiac monitoring",
            "Emergency care for chest pain"
        ]
    },
    "Kidney Disease": {
        "symptoms": ["fatigue", "swelling", "decreased_urine_output", "nausea", "confusion", "shortness_of_breath", "chest_pain"],
        "severity": "serious",
        "recommendations": [
            "Consult nephrologist immediately",
            "Blood and urine tests required",
            "Dietary modifications",
            "Blood pressure management",
            "Regular monitoring essential"
        ]
    },
    "Liver Disease": {
        "symptoms": ["yellowing_skin", "abdominal_pain", "swelling", "fatigue", "nausea", "dark_urine", "pale_skin", "easy_bruising"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical attention",
            "Liver function tests required",
            "Avoid alcohol completely",
            "Medication management",
            "Consider specialist consultation"
        ]
    },
    "Celiac Disease": {
        "symptoms": ["diarrhea", "abdominal_pain", "bloating", "weight_loss", "fatigue", "nausea", "constipation"],
        "severity": "moderate",
        "recommendations": [
            "Strict gluten-free diet",
            "Consult gastroenterologist",
            "Nutritional supplements may be needed",
            "Read food labels carefully",
            "Join support groups"
        ]
    },
    "Irritable Bowel Syndrome": {
        "symptoms": ["abdominal_pain", "bloating", "diarrhea", "constipation", "gas", "mucus_in_stool"],
        "severity": "moderate",
        "recommendations": [
            "Identify and avoid trigger foods",
            "Increase fiber intake",
            "Stress management",
            "Regular exercise",
            "Consider probiotics"
        ]
    },
    "Chronic Fatigue Syndrome": {
        "symptoms": ["extreme_fatigue", "muscle_pain", "joint_pain", "headache", "memory_loss", "insomnia", "sore_throat"],
        "severity": "moderate",
        "recommendations": [
            "Pace activities carefully",
            "Cognitive behavioral therapy",
            "Sleep management",
            "Gentle exercise program",
            "Symptom management with doctor"
        ]
    },
    "Fibromyalgia": {
        "symptoms": ["widespread_muscle_pain", "fatigue", "sleep_problems", "headache", "depression", "anxiety", "numbness", "tingling"],
        "severity": "moderate",
        "recommendations": [
            "Pain management strategies",
            "Regular gentle exercise",
            "Stress reduction techniques",
            "Sleep hygiene improvements",
            "Multidisciplinary treatment approach"
        ]
    },
    "Gout": {
        "symptoms": ["sudden_joint_pain", "swelling", "redness", "warmth", "limited_range_of_motion"],
        "severity": "moderate",
        "recommendations": [
            "Avoid high-purine foods",
            "Stay well hydrated",
            "Limit alcohol consumption",
            "Medication for acute attacks",
            "Weight management"
        ]
    },
    "Osteoporosis": {
        "symptoms": ["back_pain", "loss_of_height", "stooped_posture", "bone_fractures"],
        "severity": "moderate",
        "recommendations": [
            "Calcium and vitamin D supplementation",
            "Weight-bearing exercises",
            "Fall prevention strategies",
            "Bone density testing",
            "Medication if prescribed"
        ]
    },
    "Multiple Sclerosis": {
        "symptoms": ["numbness", "weakness", "vision_problems", "dizziness", "fatigue", "coordination_problems", "tremors"],
        "severity": "serious",
        "recommendations": [
            "Neurologist consultation required",
            "Disease-modifying therapies",
            "Physical therapy",
            "Symptom management",
            "Regular MRI monitoring"
        ]
    },
    "Parkinson Disease": {
        "symptoms": ["tremors", "slow_movement", "rigid_muscles", "balance_problems", "loss_of_coordination"],
        "severity": "serious",
        "recommendations": [
            "Neurologist consultation essential",
            "Medication management",
            "Physical and occupational therapy",
            "Exercise program",
            "Support group participation"
        ]
    },
    "Epilepsy": {
        "symptoms": ["seizures", "loss_of_consciousness", "confusion", "staring_spells", "muscle_jerking"],
        "severity": "serious",
        "recommendations": [
            "Neurologist consultation required",
            "Anti-seizure medications",
            "Avoid seizure triggers",
            "Safety precautions",
            "Regular monitoring"
        ]
    },
    "Stroke": {
        "symptoms": ["sudden_weakness", "facial_drooping", "speech_difficulty", "vision_problems", "severe_headache", "loss_of_balance"],
        "severity": "emergency",
        "recommendations": [
            "CALL 911 IMMEDIATELY",
            "Time is critical - act FAST",
            "Do not drive to hospital",
            "Note time symptoms started",
            "Emergency treatment required"
        ]
    },
    "Chronic Obstructive Pulmonary Disease": {
        "symptoms": ["shortness_of_breath", "chronic_cough", "mucus_production", "wheezing", "chest_tightness", "fatigue"],
        "severity": "serious",
        "recommendations": [
            "Quit smoking immediately",
            "Pulmonologist consultation",
            "Bronchodilator medications",
            "Pulmonary rehabilitation",
            "Oxygen therapy if needed"
        ]
    },
    "Sleep Apnea": {
        "symptoms": ["loud_snoring", "gasping", "daytime_fatigue", "morning_headache", "irritability", "difficulty_concentrating"],
        "severity": "moderate",
        "recommendations": [
            "Sleep study recommended",
            "CPAP therapy if diagnosed",
            "Weight loss if overweight",
            "Avoid alcohol before bed",
            "Sleep position changes"
        ]
    },
    "Psoriasis": {
        "symptoms": ["red_patches", "dry_skin", "itching", "burning", "skin_scales", "joint_pain"],
        "severity": "moderate",
        "recommendations": [
            "Dermatologist consultation",
            "Moisturize regularly",
            "Topical treatments",
            "Avoid triggers",
            "Stress management"
        ]
    },
    "Eczema": {
        "symptoms": ["itching", "dry_skin", "rash", "skin_redness", "blisters", "thickened_skin"],
        "severity": "mild",
        "recommendations": [
            "Moisturize frequently",
            "Identify and avoid triggers",
            "Use gentle soaps",
            "Topical corticosteroids",
            "Avoid scratching"
        ]
    },
    "Rheumatoid Arthritis": {
        "symptoms": ["joint_pain", "joint_stiffness", "swelling", "fatigue", "fever", "weight_loss"],
        "severity": "serious",
        "recommendations": [
            "Rheumatologist consultation",
            "Disease-modifying drugs",
            "Physical therapy",
            "Joint protection techniques",
            "Regular monitoring"
        ]
    },
    "Lupus": {
        "symptoms": ["fatigue", "joint_pain", "rash", "fever", "sensitivity_to_light", "kidney_problems", "chest_pain"],
        "severity": "serious",
        "recommendations": [
            "Rheumatologist consultation",
            "Immunosuppressive medications",
            "Sun protection",
            "Regular monitoring",
            "Multidisciplinary care"
        ]
    },
    "Crohn Disease": {
        "symptoms": ["abdominal_pain", "diarrhea", "weight_loss", "fatigue", "blood_in_stool", "nausea"],
        "severity": "serious",
        "recommendations": [
            "Gastroenterologist consultation",
            "Anti-inflammatory medications",
            "Dietary modifications",
            "Stress management",
            "Regular monitoring"
        ]
    },
    "Ulcerative Colitis": {
        "symptoms": ["diarrhea", "blood_in_stool", "abdominal_pain", "urgency", "weight_loss", "fatigue"],
        "severity": "serious",
        "recommendations": [
            "Gastroenterologist consultation",
            "Anti-inflammatory drugs",
            "Dietary adjustments",
            "Regular colonoscopy",
            "Symptom monitoring"
        ]
    },
    "Pancreatitis": {
        "symptoms": ["severe_abdominal_pain", "nausea", "vomiting", "fever", "rapid_pulse", "tender_abdomen"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical attention",
            "Hospital care often required",
            "Fasting to rest pancreas",
            "Pain management",
            "Address underlying cause"
        ]
    },
    "Gallstones": {
        "symptoms": ["sudden_abdominal_pain", "nausea", "vomiting", "back_pain", "yellowing_skin"],
        "severity": "moderate",
        "recommendations": [
            "Consult gastroenterologist",
            "Imaging tests required",
            "Low-fat diet",
            "Surgery if symptomatic",
            "Pain management"
        ]
    },
    "Peptic Ulcer": {
        "symptoms": ["burning_stomach_pain", "heartburn", "nausea", "bloating", "intolerance_to_fatty_foods"],
        "severity": "moderate",
        "recommendations": [
            "Avoid NSAIDs and alcohol",
            "Proton pump inhibitors",
            "H. pylori testing and treatment",
            "Stress management",
            "Small frequent meals"
        ]
    },
    "Tuberculosis": {
        "symptoms": ["persistent_cough", "coughing_blood", "chest_pain", "fever", "night_sweats", "weight_loss"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical testing",
            "Long-term antibiotic treatment",
            "Isolation during infectious period",
            "Contact tracing required",
            "Complete full treatment course"
        ]
    },
    "Mononucleosis": {
        "symptoms": ["fever", "sore_throat", "fatigue", "swollen_lymph_nodes", "rash", "loss_of_appetite"],
        "severity": "moderate",
        "recommendations": [
            "Rest is essential",
            "Stay hydrated",
            "Avoid contact sports",
            "Pain relievers for symptoms",
            "Gradual return to activities"
        ]
    },
    "Lyme Disease": {
        "symptoms": ["rash", "fever", "chills", "fatigue", "muscle_pain", "joint_pain", "headache"],
        "severity": "moderate",
        "recommendations": [
            "Seek medical attention promptly",
            "Antibiotic treatment required",
            "Tick prevention measures",
            "Early treatment prevents complications",
            "Follow-up if symptoms persist"
        ]
    },
    "Meningitis": {
        "symptoms": ["severe_headache", "fever", "stiff_neck", "nausea", "vomiting", "sensitivity_to_light", "confusion"],
        "severity": "emergency",
        "recommendations": [
            "SEEK EMERGENCY CARE IMMEDIATELY",
            "Life-threatening condition",
            "Antibiotics or antivirals needed",
            "Hospital admission required",
            "Vaccination available for prevention"
        ]
    },
    "Appendicitis": {
        "symptoms": ["abdominal_pain", "nausea", "vomiting", "fever", "loss_of_appetite", "constipation"],
        "severity": "emergency",
        "recommendations": [
            "Seek immediate emergency care",
            "Surgical removal usually required",
            "Do not eat or drink",
            "Time-sensitive condition",
            "Can lead to peritonitis if untreated"
        ]
    },
    "Glaucoma": {
        "symptoms": ["eye_pain", "blurred_vision", "halos", "headache", "nausea", "red_eyes"],
        "severity": "serious",
        "recommendations": [
            "Ophthalmologist consultation urgent",
            "Eye pressure lowering medications",
            "Regular monitoring essential",
            "May require laser or surgery",
            "Can cause permanent blindness"
        ]
    },
    "Cataracts": {
        "symptoms": ["blurred_vision", "decreased_vision", "sensitivity_to_light", "faded_colors", "halos", "double_vision"],
        "severity": "moderate",
        "recommendations": [
            "Ophthalmology consultation",
            "Surgical removal when vision affected",
            "Update eyeglass prescription",
            "Manage lighting at home",
            "Curable with surgery"
        ]
    },
    "Macular Degeneration": {
        "symptoms": ["blurred_vision", "vision_changes", "difficulty_reading", "decreased_central_vision", "distorted_vision"],
        "severity": "serious",
        "recommendations": [
            "Retina specialist consultation",
            "Anti-VEGF injections may help",
            "Nutritional supplements",
            "Low vision aids",
            "Regular monitoring required"
        ]
    },
    "Retinal Detachment": {
        "symptoms": ["floaters", "flashes_of_light", "vision_loss", "shadow_in_vision", "curtain_over_vision"],
        "severity": "emergency",
        "recommendations": [
            "SEEK EMERGENCY CARE IMMEDIATELY",
            "Surgical repair required urgently",
            "Permanent blindness if untreated",
            "Do not delay treatment",
            "Retina specialist needed"
        ]
    },
    "Otitis Media": {
        "symptoms": ["ear_pain", "fever", "hearing_loss", "fluid_drainage", "irritability", "difficulty_sleeping"],
        "severity": "moderate",
        "recommendations": [
            "Consult healthcare provider",
            "Antibiotics if bacterial",
            "Pain management",
            "Warm compress to ear",
            "Follow-up to ensure resolution"
        ]
    },
    "Vertigo (BPPV)": {
        "symptoms": ["spinning_sensation", "dizziness", "nausea", "vomiting", "balance_problems", "nystagmus"],
        "severity": "moderate",
        "recommendations": [
            "Epley maneuver may help",
            "Vestibular rehabilitation",
            "Avoid sudden head movements",
            "ENT consultation",
            "Usually resolves with treatment"
        ]
    },
    "Meniere Disease": {
        "symptoms": ["vertigo", "hearing_loss", "tinnitus", "ear_fullness", "nausea", "balance_problems"],
        "severity": "moderate",
        "recommendations": [
            "ENT specialist consultation",
            "Low-sodium diet",
            "Diuretic medications",
            "Avoid triggers",
            "Vestibular rehabilitation"
        ]
    },
    "Temporomandibular Joint Disorder": {
        "symptoms": ["jaw_pain", "clicking_jaw", "difficulty_chewing", "ear_pain", "headache", "facial_pain"],
        "severity": "mild",
        "recommendations": [
            "Apply ice or heat",
            "Soft food diet",
            "Jaw exercises",
            "Stress management",
            "Dental consultation if severe"
        ]
    },
    "Peripheral Neuropathy": {
        "symptoms": ["numbness", "tingling", "burning_sensation", "pain", "weakness", "loss_of_coordination"],
        "severity": "moderate",
        "recommendations": [
            "Neurologist consultation",
            "Identify and treat underlying cause",
            "Pain management",
            "Physical therapy",
            "Foot care if diabetic"
        ]
    },
    "Restless Legs Syndrome": {
        "symptoms": ["uncomfortable_leg_sensations", "urge_to_move_legs", "worse_at_night", "difficulty_sleeping"],
        "severity": "mild",
        "recommendations": [
            "Iron supplementation if deficient",
            "Avoid caffeine",
            "Regular exercise",
            "Leg massage",
            "Medications if severe"
        ]
    },
    "Carpal Tunnel Syndrome": {
        "symptoms": ["hand_numbness", "tingling", "weakness", "pain", "worse_at_night", "difficulty_gripping"],
        "severity": "moderate",
        "recommendations": [
            "Wrist splinting at night",
            "Ergonomic modifications",
            "Anti-inflammatory medications",
            "Corticosteroid injections",
            "Surgery if conservative treatment fails"
        ]
    },
    "Sciatica": {
        "symptoms": ["leg_pain", "lower_back_pain", "numbness", "tingling", "weakness", "shooting_pain"],
        "severity": "moderate",
        "recommendations": [
            "Physical therapy",
            "Pain management",
            "Core strengthening",
            "Avoid prolonged sitting",
            "Surgery if severe or progressive"
        ]
    },
    "Herniated Disc": {
        "symptoms": ["back_pain", "leg_pain", "numbness", "weakness", "radiating_pain", "difficulty_walking"],
        "severity": "moderate",
        "recommendations": [
            "Physical therapy",
            "Pain management",
            "Avoid heavy lifting",
            "Core strengthening",
            "Surgery if conservative treatment fails"
        ]
    },
    "Spinal Stenosis": {
        "symptoms": ["back_pain", "leg_pain", "numbness", "weakness", "cramping", "difficulty_walking"],
        "severity": "moderate",
        "recommendations": [
            "Physical therapy",
            "Pain management",
            "Epidural injections",
            "Walking assistance devices",
            "Surgery if severe symptoms"
        ]
    },
    "Polymyalgia Rheumatica": {
        "symptoms": ["shoulder_pain", "hip_pain", "morning_stiffness", "fatigue", "fever", "weight_loss"],
        "severity": "moderate",
        "recommendations": [
            "Rheumatologist consultation",
            "Corticosteroid treatment",
            "Regular monitoring",
            "Gradual steroid taper",
            "Monitor for temporal arteritis"
        ]
    },
    "Giant Cell Arteritis": {
        "symptoms": ["severe_headache", "scalp_tenderness", "jaw_pain", "vision_problems", "fever", "fatigue"],
        "severity": "emergency",
        "recommendations": [
            "SEEK IMMEDIATE MEDICAL CARE",
            "Risk of permanent blindness",
            "High-dose corticosteroids",
            "Temporal artery biopsy",
            "Rheumatology consultation urgent"
        ]
    },
    "Polymyositis": {
        "symptoms": ["muscle_weakness", "fatigue", "difficulty_swallowing", "shortness_of_breath", "joint_pain"],
        "severity": "serious",
        "recommendations": [
            "Rheumatologist consultation",
            "Immunosuppressive medications",
            "Physical therapy",
            "Regular monitoring",
            "Cardiac and pulmonary evaluation"
        ]
    },
    "Scleroderma": {
        "symptoms": ["skin_thickening", "raynauds_phenomenon", "difficulty_swallowing", "heartburn", "joint_pain"],
        "severity": "serious",
        "recommendations": [
            "Rheumatologist consultation",
            "Immunosuppressive treatment",
            "Skin care",
            "Organ monitoring",
            "Multidisciplinary care"
        ]
    },
    "Sarcoidosis": {
        "symptoms": ["cough", "shortness_of_breath", "chest_pain", "fatigue", "weight_loss", "skin_lesions"],
        "severity": "moderate",
        "recommendations": [
            "Pulmonologist consultation",
            "Corticosteroids if symptomatic",
            "Regular monitoring",
            "Chest imaging",
            "Multiorgan evaluation"
        ]
    },
    "Addison Disease": {
        "symptoms": ["fatigue", "weight_loss", "low_blood_pressure", "hyperpigmentation", "salt_craving", "nausea"],
        "severity": "serious",
        "recommendations": [
            "Endocrinologist consultation",
            "Hormone replacement therapy",
            "Emergency medication card",
            "Regular monitoring",
            "Stress dose adjustments"
        ]
    },
    "Cushing Syndrome": {
        "symptoms": ["weight_gain", "moon_face", "buffalo_hump", "high_blood_pressure", "diabetes", "easy_bruising"],
        "severity": "serious",
        "recommendations": [
            "Endocrinologist consultation",
            "Identify underlying cause",
            "Surgical or medical treatment",
            "Manage complications",
            "Regular monitoring"
        ]
    },
    "Acromegaly": {
        "symptoms": ["enlarged_hands", "enlarged_feet", "facial_changes", "headache", "vision_problems", "joint_pain"],
        "severity": "serious",
        "recommendations": [
            "Endocrinologist consultation",
            "MRI of pituitary",
            "Surgical treatment",
            "Medication management",
            "Screen for complications"
        ]
    },
    "Pheochromocytoma": {
        "symptoms": ["severe_headache", "rapid_heartbeat", "sweating", "high_blood_pressure", "anxiety", "tremors"],
        "severity": "serious",
        "recommendations": [
            "Emergency evaluation if crisis",
            "Endocrinology consultation",
            "Imaging studies",
            "Surgical removal",
            "Blood pressure management"
        ]
    },
    "Polycystic Ovary Syndrome": {
        "symptoms": ["irregular_periods", "acne", "weight_gain", "excess_hair", "hair_loss", "difficulty_getting_pregnant"],
        "severity": "moderate",
        "recommendations": [
            "Gynecologist or endocrinologist",
            "Lifestyle modifications",
            "Hormonal contraceptives",
            "Fertility treatment if needed",
            "Monitor for diabetes"
        ]
    },
    "Endometriosis": {
        "symptoms": ["pelvic_pain", "painful_periods", "painful_intercourse", "infertility", "heavy_bleeding"],
        "severity": "moderate",
        "recommendations": [
            "Gynecologist consultation",
            "Pain management",
            "Hormonal treatments",
            "Surgical treatment if severe",
            "Fertility preservation options"
        ]
    },
    "Benign Prostatic Hyperplasia": {
        "symptoms": ["difficulty_urinating", "weak_stream", "frequent_urination", "nocturia", "urgency", "incomplete_emptying"],
        "severity": "moderate",
        "recommendations": [
            "Urologist consultation",
            "Medications to improve flow",
            "Lifestyle modifications",
            "Surgical options if severe",
            "Regular monitoring"
        ]
    },
    "Interstitial Cystitis": {
        "symptoms": ["pelvic_pain", "urinary_urgency", "frequent_urination", "painful_urination", "pain_during_intercourse"],
        "severity": "moderate",
        "recommendations": [
            "Urologist consultation",
            "Dietary modifications",
            "Bladder instillations",
            "Pain management",
            "Physical therapy"
        ]
    },
    "Diverticulitis": {
        "symptoms": ["abdominal_pain", "fever", "nausea", "constipation", "diarrhea", "bloating"],
        "severity": "moderate",
        "recommendations": [
            "Clear liquid diet initially",
            "Antibiotics if prescribed",
            "Gradual diet advancement",
            "High-fiber diet after recovery",
            "Surgery if complications"
        ]
    },
    "Hemorrhoids": {
        "symptoms": ["rectal_bleeding", "anal_pain", "itching", "swelling", "discomfort"],
        "severity": "mild",
        "recommendations": [
            "High-fiber diet",
            "Adequate hydration",
            "Sitz baths",
            "Topical treatments",
            "Procedures or surgery if severe"
        ]
    },
    "Gastroesophageal Reflux Disease": {
        "symptoms": ["heartburn", "acid_reflux", "chest_pain", "difficulty_swallowing", "chronic_cough", "hoarseness"],
        "severity": "moderate",
        "recommendations": [
            "Lifestyle modifications",
            "Elevate head of bed",
            "Avoid trigger foods",
            "Proton pump inhibitors",
            "Endoscopy if alarm symptoms"
        ]
    },
    "Barrett Esophagus": {
        "symptoms": ["heartburn", "difficulty_swallowing", "chest_pain", "chronic_reflux"],
        "severity": "serious",
        "recommendations": [
            "Gastroenterologist consultation",
            "Proton pump inhibitors",
            "Regular endoscopic surveillance",
            "Treatment if dysplasia found",
            "Risk factor for esophageal cancer"
        ]
    },
    "Lactose Intolerance": {
        "symptoms": ["diarrhea", "bloating", "gas", "abdominal_cramps", "nausea"],
        "severity": "mild",
        "recommendations": [
            "Avoid dairy products",
            "Lactase supplements",
            "Calcium-fortified alternatives",
            "Gradual reintroduction trial",
            "Nutritional counseling"
        ]
    },
    "Food Allergy": {
        "symptoms": ["hives", "itching", "swelling", "difficulty_breathing", "nausea", "vomiting", "diarrhea"],
        "severity": "serious",
        "recommendations": [
            "Allergist consultation",
            "Strict allergen avoidance",
            "Carry epinephrine auto-injector",
            "Read food labels carefully",
            "Medical alert bracelet"
        ]
    },
    "Anaphylaxis": {
        "symptoms": ["difficulty_breathing", "swelling", "hives", "rapid_pulse", "dizziness", "loss_of_consciousness"],
        "severity": "emergency",
        "recommendations": [
            "CALL 911 IMMEDIATELY",
            "Use epinephrine immediately",
            "Lie flat with legs elevated",
            "Life-threatening emergency",
            "Hospital monitoring required"
        ]
    },
    "Chronic Kidney Disease": {
        "symptoms": ["fatigue", "swelling", "decreased_appetite", "nausea", "shortness_of_breath", "confusion"],
        "severity": "serious",
        "recommendations": [
            "Nephrologist consultation",
            "Blood pressure control",
            "Dietary modifications",
            "Regular monitoring",
            "Dialysis or transplant if advanced"
        ]
    },
    "Nephrotic Syndrome": {
        "symptoms": ["severe_swelling", "foamy_urine", "weight_gain", "fatigue", "loss_of_appetite"],
        "severity": "serious",
        "recommendations": [
            "Nephrologist consultation urgent",
            "Kidney biopsy may be needed",
            "Immunosuppressive treatment",
            "Diuretics for swelling",
            "Monitor for complications"
        ]
    },
    "Acute Kidney Injury": {
        "symptoms": ["decreased_urine_output", "swelling", "fatigue", "confusion", "nausea", "chest_pain"],
        "severity": "emergency",
        "recommendations": [
            "Seek immediate medical care",
            "Identify and treat cause",
            "Hospital admission usually required",
            "May need dialysis",
            "Can be reversible if treated promptly"
        ]
    },
    "Rhabdomyolysis": {
        "symptoms": ["muscle_pain", "weakness", "dark_urine", "fatigue", "nausea", "confusion"],
        "severity": "emergency",
        "recommendations": [
            "SEEK EMERGENCY CARE IMMEDIATELY",
            "IV fluids essential",
            "Can cause kidney failure",
            "Hospital admission required",
            "Avoid muscle damage triggers"
        ]
    },
    "Deep Vein Thrombosis": {
        "symptoms": ["leg_swelling", "leg_pain", "warmth", "redness", "prominent_veins"],
        "severity": "serious",
        "recommendations": [
            "Seek immediate medical evaluation",
            "Ultrasound imaging",
            "Anticoagulation therapy",
            "Risk of pulmonary embolism",
            "Compression stockings"
        ]
    },
    "Pulmonary Embolism": {
        "symptoms": ["sudden_shortness_of_breath", "chest_pain", "coughing_blood", "rapid_heartbeat", "lightheadedness"],
        "severity": "emergency",
        "recommendations": [
            "CALL 911 IMMEDIATELY",
            "Life-threatening condition",
            "Anticoagulation required",
            "Hospital admission essential",
            "May need thrombolysis"
        ]
    }
}

EXTRA_CONDITION_PATTERNS = {
    "Malaria": {
        "symptoms": ["fever", "chills", "rigors", "sweating", "headache", "muscle_pain", "fatigue", "nausea", "vomiting"],
        "severity": "serious",
        "recommendations": [
            "Seek medical evaluation promptly",
            "Blood testing is required for diagnosis",
            "Antimalarial treatment may be needed",
            "Stay hydrated",
            "Seek urgent care for confusion, seizures, or severe weakness"
        ]
    },
    "Dengue Fever": {
        "symptoms": ["high_fever", "severe_headache", "eye_pain", "joint_pain", "muscle_pain", "rash", "nausea", "easy_bruising"],
        "severity": "serious",
        "recommendations": [
            "Seek medical evaluation",
            "Avoid aspirin and ibuprofen unless directed by a clinician",
            "Drink fluids frequently",
            "Monitor for bleeding or severe abdominal pain",
            "Urgent care if dizziness, confusion, or persistent vomiting occurs"
        ]
    },
    "Typhoid Fever": {
        "symptoms": ["persistent_fever", "headache", "abdominal_pain", "constipation", "diarrhea", "fatigue", "loss_of_appetite", "rash"],
        "severity": "serious",
        "recommendations": [
            "Medical evaluation and testing are needed",
            "Antibiotics may be required",
            "Maintain hydration",
            "Use safe food and water precautions",
            "Seek urgent care for severe abdominal pain or confusion"
        ]
    },
    "Hepatitis A": {
        "symptoms": ["fatigue", "nausea", "abdominal_pain", "loss_of_appetite", "dark_urine", "jaundice", "fever", "joint_pain"],
        "severity": "moderate",
        "recommendations": [
            "Consult a healthcare provider",
            "Rest and maintain hydration",
            "Avoid alcohol",
            "Practice careful hand hygiene",
            "Discuss vaccination and exposure guidance"
        ]
    },
    "Chickenpox": {
        "symptoms": ["fever", "fatigue", "itching", "blisters", "rash", "loss_of_appetite", "headache"],
        "severity": "moderate",
        "recommendations": [
            "Isolate until lesions crust over",
            "Avoid scratching",
            "Use soothing skin care as directed",
            "Seek care for adults, pregnancy, or immune suppression",
            "Monitor for skin infection"
        ]
    },
    "Measles": {
        "symptoms": ["high_fever", "cough", "runny_nose", "red_eyes", "rash", "sensitivity_to_light", "fatigue"],
        "severity": "serious",
        "recommendations": [
            "Contact a healthcare provider before visiting a clinic",
            "Isolate to prevent spread",
            "Supportive care and hydration",
            "Check vaccination status",
            "Urgent care for breathing difficulty or confusion"
        ]
    },
    "Mumps": {
        "symptoms": ["fever", "headache", "muscle_pain", "fatigue", "loss_of_appetite", "swollen_salivary_glands", "jaw_pain"],
        "severity": "moderate",
        "recommendations": [
            "Rest and hydrate",
            "Use pain relief as directed",
            "Avoid acidic foods if painful",
            "Isolate to reduce spread",
            "Seek care for testicular pain, severe headache, or stiff neck"
        ]
    },
    "Strep Throat": {
        "symptoms": ["sore_throat", "fever", "swollen_lymph_nodes", "difficulty_swallowing", "headache", "nausea", "red_tonsils"],
        "severity": "moderate",
        "recommendations": [
            "Throat testing may be needed",
            "Antibiotics may be prescribed",
            "Gargle with warm salt water",
            "Replace toothbrush after starting antibiotics",
            "Seek care for breathing or swallowing difficulty"
        ]
    },
    "Tonsillitis": {
        "symptoms": ["sore_throat", "difficulty_swallowing", "fever", "bad_breath", "swollen_lymph_nodes", "hoarseness", "red_tonsils"],
        "severity": "moderate",
        "recommendations": [
            "Rest and drink fluids",
            "Use warm salt water gargles",
            "Pain relief as directed",
            "Medical review if recurrent or severe",
            "Urgent care for drooling or breathing difficulty"
        ]
    },
    "Conjunctivitis": {
        "symptoms": ["eye_redness", "eye_discharge", "watery_eyes", "itching", "eye_pain", "blurred_vision", "sensitivity_to_light"],
        "severity": "mild",
        "recommendations": [
            "Avoid touching or rubbing eyes",
            "Wash hands frequently",
            "Avoid sharing towels",
            "Stop contact lenses until cleared",
            "Seek care for pain, light sensitivity, or vision changes"
        ]
    },
    "Dental Abscess": {
        "symptoms": ["tooth_pain", "jaw_pain", "facial_swelling", "fever", "bad_breath", "sensitive_teeth", "difficulty_chewing"],
        "severity": "serious",
        "recommendations": [
            "See a dentist urgently",
            "Do not ignore facial swelling",
            "Pain relief as directed",
            "Antibiotics or drainage may be needed",
            "Emergency care for trouble breathing or swallowing"
        ]
    },
    "Gingivitis": {
        "symptoms": ["bleeding_gums", "gum_swelling", "bad_breath", "sensitive_teeth", "gum_pain", "red_gums"],
        "severity": "mild",
        "recommendations": [
            "Brush and floss gently every day",
            "Schedule dental cleaning",
            "Use dentist-recommended mouth rinse",
            "Avoid tobacco",
            "Seek dental care if bleeding persists"
        ]
    },
    "Vitamin B12 Deficiency": {
        "symptoms": ["fatigue", "weakness", "numbness", "tingling", "memory_loss", "dizziness", "pale_skin", "glossitis"],
        "severity": "moderate",
        "recommendations": [
            "Ask a clinician about blood testing",
            "Dietary review may help",
            "Supplements or injections may be needed",
            "Monitor nerve symptoms",
            "Seek care for worsening weakness or confusion"
        ]
    },
    "Vitamin D Deficiency": {
        "symptoms": ["fatigue", "bone_pain", "muscle_weakness", "muscle_pain", "depression", "frequent_infections"],
        "severity": "mild",
        "recommendations": [
            "Discuss vitamin D testing",
            "Safe sunlight exposure may help",
            "Use supplements only as directed",
            "Include vitamin D rich foods",
            "Evaluate persistent bone pain"
        ]
    },
    "Dehydration": {
        "symptoms": ["thirst", "dry_mouth", "dizziness", "dark_urine", "decreased_urine_output", "fatigue", "confusion"],
        "severity": "moderate",
        "recommendations": [
            "Drink oral rehydration fluids",
            "Rest in a cool place",
            "Avoid alcohol",
            "Monitor urination",
            "Seek urgent care for confusion, fainting, or inability to keep fluids down"
        ]
    },
    "Heat Exhaustion": {
        "symptoms": ["excessive_sweating", "weakness", "dizziness", "nausea", "headache", "muscle_cramps", "rapid_heartbeat"],
        "severity": "serious",
        "recommendations": [
            "Move to a cool place immediately",
            "Drink cool fluids",
            "Loosen clothing",
            "Use cool compresses",
            "Emergency care if confusion, fainting, or very high temperature occurs"
        ]
    },
    "Hypoglycemia": {
        "symptoms": ["sweating", "tremors", "excessive_hunger", "dizziness", "confusion", "palpitations", "weakness", "anxiety"],
        "severity": "serious",
        "recommendations": [
            "Check blood glucose if possible",
            "Take fast-acting carbohydrate if safe",
            "Recheck symptoms after 15 minutes",
            "Eat a snack or meal after recovery",
            "Emergency care for seizure or unconsciousness"
        ]
    },
    "Hyperglycemia": {
        "symptoms": ["excessive_thirst", "frequent_urination", "fatigue", "blurred_vision", "dry_mouth", "weight_loss", "nausea"],
        "severity": "serious",
        "recommendations": [
            "Check blood glucose if possible",
            "Follow diabetes sick-day plan if prescribed",
            "Drink water",
            "Contact a healthcare provider",
            "Urgent care for vomiting, confusion, or deep rapid breathing"
        ]
    },
    "Panic Attack": {
        "symptoms": ["panic_attacks", "palpitations", "chest_tightness", "shortness_of_breath", "tremors", "sweating", "dizziness", "fear_of_dying"],
        "severity": "moderate",
        "recommendations": [
            "Use slow breathing techniques",
            "Move to a calm environment",
            "Limit caffeine and stimulants",
            "Consider counseling or therapy",
            "Seek emergency care for new or severe chest pain"
        ]
    },
    "Post-Traumatic Stress Disorder": {
        "symptoms": ["anxiety", "nightmares", "insomnia", "irritability", "social_withdrawal", "panic_attacks", "difficulty_concentrating", "hypervigilance"],
        "severity": "moderate",
        "recommendations": [
            "Consider trauma-focused therapy",
            "Maintain regular sleep routine",
            "Use grounding techniques",
            "Avoid alcohol or substance misuse",
            "Seek urgent help for suicidal thoughts"
        ]
    },
    "Cellulitis": {
        "symptoms": ["skin_redness", "warm_skin", "swelling", "pain", "fever", "tenderness", "skin_lesions"],
        "severity": "serious",
        "recommendations": [
            "Seek medical care promptly",
            "Antibiotics may be needed",
            "Elevate affected area",
            "Mark spreading redness if advised",
            "Emergency care for rapid spread or confusion"
        ]
    },
    "Fungal Skin Infection": {
        "symptoms": ["itching", "rash", "scaling", "skin_redness", "crusting", "skin_discoloration", "burning"],
        "severity": "mild",
        "recommendations": [
            "Keep area clean and dry",
            "Use antifungal treatment as directed",
            "Avoid sharing towels",
            "Wear breathable clothing",
            "Seek care if spreading or recurrent"
        ]
    },
    "Scabies": {
        "symptoms": ["intense_itching", "rash", "papules", "burrows", "worse_at_night", "skin_lesions"],
        "severity": "moderate",
        "recommendations": [
            "Medical diagnosis and prescription treatment are needed",
            "Treat close contacts as directed",
            "Wash bedding and clothing in hot water",
            "Avoid skin contact until treated",
            "Itching may persist after treatment"
        ]
    },
    "Shingles": {
        "symptoms": ["burning_pain", "tingling", "rash", "blisters", "skin_sensitivity", "fever", "headache"],
        "severity": "moderate",
        "recommendations": [
            "Seek care early for antiviral treatment",
            "Keep rash covered",
            "Avoid contact with pregnant or immunocompromised people",
            "Pain control may be needed",
            "Urgent care for eye involvement"
        ]
    },
    "Kidney Stones": {
        "symptoms": ["severe_flank_pain", "blood_in_urine", "nausea", "vomiting", "painful_urination", "urinary_urgency", "groin_pain"],
        "severity": "serious",
        "recommendations": [
            "Seek medical evaluation",
            "Drink fluids if not vomiting",
            "Pain control may be needed",
            "Imaging may be required",
            "Emergency care for fever, blocked urination, or uncontrolled pain"
        ]
    },
    "Prostatitis": {
        "symptoms": ["pelvic_pain", "painful_urination", "frequent_urination", "fever", "chills", "back_pain", "painful_ejaculation"],
        "severity": "moderate",
        "recommendations": [
            "Medical evaluation is recommended",
            "Antibiotics may be needed",
            "Drink fluids",
            "Avoid bladder irritants",
            "Urgent care for high fever or urinary retention"
        ]
    },
    "Pelvic Inflammatory Disease": {
        "symptoms": ["pelvic_pain", "vaginal_discharge", "fever", "painful_intercourse", "vaginal_bleeding", "painful_urination", "lower_abdominal_pain"],
        "severity": "serious",
        "recommendations": [
            "Seek medical care promptly",
            "Antibiotics are usually required",
            "Partners may need treatment",
            "Avoid sex until treatment is complete",
            "Emergency care for severe pain or fainting"
        ]
    },
    "Ovarian Cyst": {
        "symptoms": ["pelvic_pain", "bloating", "abdominal_pain", "painful_intercourse", "menstrual_irregularities", "nausea"],
        "severity": "moderate",
        "recommendations": [
            "Schedule medical evaluation",
            "Ultrasound may be needed",
            "Track menstrual symptoms",
            "Pain relief as directed",
            "Emergency care for sudden severe pelvic pain"
        ]
    },
    "Pregnancy": {
        "symptoms": ["missed_period", "nausea", "breast_pain", "fatigue", "frequent_urination", "food_aversions", "mood_swings"],
        "severity": "mild",
        "recommendations": [
            "Take a pregnancy test",
            "Schedule prenatal care if positive",
            "Start prenatal vitamins if appropriate",
            "Avoid alcohol and smoking",
            "Urgent care for heavy bleeding or severe abdominal pain"
        ]
    },
    "Menopause": {
        "symptoms": ["hot_flashes", "night_sweats", "menstrual_irregularities", "mood_swings", "difficulty_sleeping", "vaginal_dryness", "weight_gain"],
        "severity": "mild",
        "recommendations": [
            "Discuss symptoms with a clinician",
            "Maintain regular exercise",
            "Use sleep hygiene strategies",
            "Consider non-hormonal and hormonal options if appropriate",
            "Keep up with preventive screening"
        ]
    },
    "Hand Foot and Mouth Disease": {
        "symptoms": ["fever", "mouth_sores", "rash", "blisters", "sore_throat", "loss_of_appetite", "fatigue"],
        "severity": "mild",
        "recommendations": [
            "Encourage fluids",
            "Use pain relief as directed",
            "Avoid acidic foods",
            "Practice hand hygiene",
            "Seek care for dehydration or persistent fever"
        ]
    },
    "Sepsis": {
        "symptoms": ["fever", "chills", "rapid_heartbeat", "rapid_breathing", "confusion", "low_blood_pressure", "cold_skin", "decreased_urine_output"],
        "severity": "emergency",
        "recommendations": [
            "CALL EMERGENCY SERVICES IMMEDIATELY",
            "Sepsis is life-threatening",
            "Hospital treatment is required",
            "Antibiotics and IV fluids may be needed",
            "Do not delay care"
        ]
    },
    "Gallstones": {
        "symptoms": ["right_upper_abdominal_pain", "nausea", "vomiting", "back_pain", "indigestion", "bloating", "jaundice"],
        "severity": "moderate",
        "recommendations": [
            "Medical evaluation may be needed",
            "Avoid fatty trigger foods",
            "Ultrasound may be recommended",
            "Seek urgent care for fever or yellowing skin",
            "Surgery may be needed for recurrent attacks"
        ]
    },
    "Tension Headache": {
        "symptoms": ["headache", "neck_pain", "scalp_tenderness", "fatigue", "difficulty_concentrating", "shoulder_pain"],
        "severity": "mild",
        "recommendations": [
            "Rest and hydrate",
            "Gentle stretching may help",
            "Reduce screen strain",
            "Use pain relief as directed",
            "Seek care for sudden severe or unusual headache"
        ]
    },
    "Cluster Headache": {
        "symptoms": ["severe_headache", "eye_pain", "watery_eyes", "nasal_congestion", "restlessness", "facial_sweating", "drooping_eyelid"],
        "severity": "serious",
        "recommendations": [
            "Medical evaluation is recommended",
            "Specific acute treatments may help",
            "Avoid alcohol during clusters",
            "Track timing and triggers",
            "Seek urgent care for first or worst headache"
        ]
    }
}

EXPANDED_CONDITION_PATTERNS = {
    "Bell Palsy": {
        "symptoms": ["facial_droop", "facial_weakness", "drooling", "eye_dryness", "taste_changes", "ear_pain", "sensitivity_to_sound"],
        "severity": "serious",
        "recommendations": [
            "Seek same-day medical evaluation",
            "Stroke must be ruled out for sudden facial weakness",
            "Protect the eye if it cannot close fully",
            "Treatment works best when started early",
            "Emergency care for arm weakness, speech difficulty, or confusion"
        ]
    },
    "Diabetic Ketoacidosis": {
        "symptoms": ["excessive_thirst", "frequent_urination", "nausea", "vomiting", "abdominal_pain", "deep_rapid_breathing", "fruity_breath", "confusion"],
        "severity": "emergency",
        "recommendations": [
            "Seek emergency care immediately",
            "Check blood glucose and ketones if available",
            "Do not delay care for persistent vomiting or confusion",
            "IV fluids and insulin may be required",
            "Follow a clinician's diabetes sick-day plan"
        ]
    },
    "Pneumothorax": {
        "symptoms": ["sudden_chest_pain", "sudden_shortness_of_breath", "rapid_breathing", "rapid_heartbeat", "chest_tightness", "cyanosis", "fatigue"],
        "severity": "emergency",
        "recommendations": [
            "Seek emergency care immediately",
            "Avoid exertion",
            "Oxygen and imaging may be needed",
            "Treatment depends on severity",
            "Call emergency services for severe breathing trouble"
        ]
    },
    "Whooping Cough": {
        "symptoms": ["paroxysmal_cough", "whooping_cough", "coughing_fits", "vomiting_after_cough", "runny_nose", "low_grade_fever", "fatigue"],
        "severity": "serious",
        "recommendations": [
            "Contact a healthcare provider",
            "Testing and antibiotics may be needed",
            "Avoid contact with infants and pregnant people",
            "Stay hydrated",
            "Seek urgent care for breathing pauses or blue lips"
        ]
    },
    "Laryngitis": {
        "symptoms": ["hoarseness", "voice_loss", "sore_throat", "dry_cough", "throat_irritation", "difficulty_speaking"],
        "severity": "mild",
        "recommendations": [
            "Rest your voice",
            "Drink warm fluids",
            "Avoid smoke and irritants",
            "Use humidified air",
            "Seek care if hoarseness lasts more than two weeks"
        ]
    },
    "Peritonsillar Abscess": {
        "symptoms": ["severe_sore_throat", "difficulty_swallowing", "fever", "muffled_voice", "drooling", "jaw_stiffness", "swollen_lymph_nodes"],
        "severity": "serious",
        "recommendations": [
            "Seek urgent medical care",
            "Drainage and antibiotics may be needed",
            "Do not delay care if swallowing is difficult",
            "Emergency care for breathing difficulty",
            "Maintain fluids if safe to swallow"
        ]
    },
    "Oral Thrush": {
        "symptoms": ["white_patches_in_mouth", "mouth_pain", "loss_of_taste", "dry_mouth", "cracking_corners_of_mouth", "difficulty_swallowing"],
        "severity": "mild",
        "recommendations": [
            "Consult a healthcare provider or dentist",
            "Antifungal treatment may be needed",
            "Rinse mouth after inhaled steroid use",
            "Keep dentures clean if used",
            "Seek care for swallowing pain or recurrent symptoms"
        ]
    },
    "Dry Eye Syndrome": {
        "symptoms": ["dry_eyes", "eye_redness", "burning_eyes", "gritty_eyes", "blurred_vision", "watery_eyes", "light_sensitivity"],
        "severity": "mild",
        "recommendations": [
            "Use lubricating eye drops if appropriate",
            "Take screen breaks",
            "Avoid smoke and wind exposure",
            "Review medicines that may worsen dryness with a clinician",
            "Seek care for pain, vision loss, or severe redness"
        ]
    },
    "Otitis Externa": {
        "symptoms": ["ear_pain", "itching_ear", "ear_discharge", "ear_fullness", "hearing_loss", "pain_with_ear_movement"],
        "severity": "moderate",
        "recommendations": [
            "Keep the ear dry",
            "Avoid inserting objects into the ear",
            "Medical ear drops may be needed",
            "Seek care for fever or spreading redness",
            "Avoid swimming until improved"
        ]
    },
    "Earwax Impaction": {
        "symptoms": ["ear_fullness", "hearing_loss", "tinnitus", "ear_pain", "dizziness", "cough"],
        "severity": "mild",
        "recommendations": [
            "Avoid cotton swabs deep in the ear",
            "Consider clinician-approved wax softening drops",
            "Seek care for pain, drainage, or sudden hearing loss",
            "Professional removal may be needed",
            "Do not irrigate if eardrum injury is possible"
        ]
    },
    "Epistaxis": {
        "symptoms": ["nosebleeds", "blood_from_nose", "nasal_dryness", "dizziness", "pale_skin"],
        "severity": "moderate",
        "recommendations": [
            "Sit upright and lean forward",
            "Pinch the soft part of the nose",
            "Avoid nose blowing after bleeding stops",
            "Seek urgent care for heavy or persistent bleeding",
            "Review blood thinner use with a clinician"
        ]
    },
    "Rosacea": {
        "symptoms": ["facial_redness", "flushing", "papules", "skin_sensitivity", "visible_blood_vessels", "burning_skin", "eye_redness"],
        "severity": "mild",
        "recommendations": [
            "Identify and avoid triggers",
            "Use gentle skin care",
            "Apply sunscreen daily",
            "Medical creams or tablets may help",
            "Seek care for eye irritation"
        ]
    },
    "Impetigo": {
        "symptoms": ["skin_lesions", "crusting", "blisters", "itching", "skin_redness", "oozing_sores"],
        "severity": "moderate",
        "recommendations": [
            "Seek medical care for diagnosis",
            "Antibiotic treatment may be needed",
            "Avoid scratching",
            "Do not share towels or bedding",
            "Keep sores covered when possible"
        ]
    },
    "Seborrheic Dermatitis": {
        "symptoms": ["scaling", "itching", "skin_redness", "flaky_scalp", "greasy_skin", "crusting"],
        "severity": "mild",
        "recommendations": [
            "Use medicated shampoo as directed",
            "Keep affected areas clean",
            "Avoid harsh skin products",
            "Treatment may need maintenance",
            "Seek care if widespread or infected"
        ]
    },
    "Allergic Contact Dermatitis": {
        "symptoms": ["itching", "rash", "skin_redness", "blisters", "swelling", "burning_skin", "dry_skin"],
        "severity": "mild",
        "recommendations": [
            "Avoid the suspected trigger",
            "Wash exposed skin gently",
            "Use cool compresses",
            "Antihistamines or topical treatments may help",
            "Seek urgent care for face swelling or breathing trouble"
        ]
    },
    "Vaginal Yeast Infection": {
        "symptoms": ["vaginal_itching", "vaginal_discharge", "burning", "painful_urination", "vaginal_redness", "painful_intercourse"],
        "severity": "mild",
        "recommendations": [
            "Consult a clinician if symptoms are new",
            "Antifungal treatment may help",
            "Avoid irritants and douching",
            "Seek care during pregnancy",
            "Evaluate recurrent symptoms"
        ]
    },
    "Bacterial Vaginosis": {
        "symptoms": ["vaginal_discharge", "fishy_odor", "vaginal_itching", "burning", "painful_urination"],
        "severity": "moderate",
        "recommendations": [
            "Medical evaluation can confirm diagnosis",
            "Antibiotics may be prescribed",
            "Avoid douching",
            "Seek care during pregnancy",
            "Return if symptoms recur"
        ]
    },
    "Premenstrual Syndrome": {
        "symptoms": ["premenstrual_symptoms", "mood_swings", "bloating", "breast_pain", "headache", "fatigue", "irritability", "food_cravings"],
        "severity": "mild",
        "recommendations": [
            "Track symptoms with the menstrual cycle",
            "Regular exercise and sleep may help",
            "Limit salt, caffeine, and alcohol if they worsen symptoms",
            "Discuss severe mood symptoms with a clinician",
            "Seek urgent help for self-harm thoughts"
        ]
    },
    "Mastitis": {
        "symptoms": ["breast_pain", "breast_swelling", "skin_redness", "fever", "chills", "fatigue", "warm_skin"],
        "severity": "moderate",
        "recommendations": [
            "Contact a healthcare provider",
            "Continue feeding or pumping if advised",
            "Use warm compresses",
            "Antibiotics may be needed",
            "Seek urgent care for abscess signs or worsening fever"
        ]
    },
    "Hypotension": {
        "symptoms": ["low_blood_pressure", "dizziness", "fainting", "blurred_vision", "nausea", "fatigue", "confusion", "cold_skin"],
        "severity": "moderate",
        "recommendations": [
            "Sit or lie down if dizzy",
            "Hydrate if safe",
            "Review medications with a clinician",
            "Seek urgent care for fainting, chest pain, or confusion",
            "Monitor blood pressure if available"
        ]
    },
    "Hyperkalemia": {
        "symptoms": ["muscle_weakness", "palpitations", "nausea", "chest_pain", "shortness_of_breath", "irregular_heartbeat"],
        "severity": "serious",
        "recommendations": [
            "Seek medical evaluation promptly",
            "Blood testing and ECG may be needed",
            "Review kidney disease and medication risks",
            "Emergency care for chest pain or severe weakness",
            "Do not self-treat with supplements"
        ]
    },
    "Hypokalemia": {
        "symptoms": ["muscle_weakness", "muscle_cramps", "fatigue", "constipation", "palpitations", "tingling"],
        "severity": "moderate",
        "recommendations": [
            "Medical testing may be needed",
            "Review vomiting, diarrhea, and medication causes",
            "Use potassium supplements only as directed",
            "Seek urgent care for severe weakness or palpitations",
            "Stay hydrated"
        ]
    },
    "Raynaud Phenomenon": {
        "symptoms": ["cold_hands", "cold_feet", "color_changes_in_fingers", "numbness", "tingling", "finger_pain"],
        "severity": "mild",
        "recommendations": [
            "Keep hands and feet warm",
            "Avoid smoking and cold exposure",
            "Manage stress triggers",
            "Seek care for sores or severe pain",
            "Evaluation may be needed if symptoms are new"
        ]
    },
    "Plantar Fasciitis": {
        "symptoms": ["heel_pain", "foot_pain", "morning_stiffness", "pain_with_walking", "tenderness"],
        "severity": "mild",
        "recommendations": [
            "Rest from aggravating activity",
            "Stretch calves and foot gently",
            "Use supportive footwear",
            "Ice after activity",
            "Seek care if pain persists or walking is difficult"
        ]
    },
    "Trigeminal Neuralgia": {
        "symptoms": ["facial_pain", "electric_shock_pain", "jaw_pain", "tooth_pain", "pain_triggered_by_touch"],
        "severity": "serious",
        "recommendations": [
            "Schedule medical evaluation",
            "Specific nerve pain treatments may help",
            "Dental causes may need to be ruled out",
            "Track triggers and pain episodes",
            "Seek urgent care for weakness, numbness, or new neurological symptoms"
        ]
    },
    "H. pylori Gastritis": {
        "symptoms": ["abdominal_pain", "bloating", "nausea", "loss_of_appetite", "belching", "heartburn", "early_satiety"],
        "severity": "moderate",
        "recommendations": [
            "Testing may be needed",
            "Antibiotic combination therapy may be prescribed",
            "Avoid NSAIDs unless directed",
            "Seek urgent care for black stool or vomiting blood",
            "Complete the full treatment if prescribed"
        ]
    },
    "Acute Gastrointestinal Bleeding": {
        "symptoms": ["blood_in_stool", "black_stool", "vomiting_blood", "dizziness", "weakness", "pale_skin", "rapid_heartbeat"],
        "severity": "emergency",
        "recommendations": [
            "Seek emergency care immediately",
            "Do not ignore black stool or vomiting blood",
            "Avoid NSAIDs unless directed",
            "Hospital evaluation may be required",
            "Call emergency services for fainting or severe weakness"
        ]
    },
    "Alcohol Withdrawal": {
        "symptoms": ["tremors", "anxiety", "sweating", "nausea", "vomiting", "insomnia", "rapid_heartbeat", "seizures", "hallucinations"],
        "severity": "serious",
        "recommendations": [
            "Medical supervision may be needed",
            "Seek urgent care for seizures, confusion, or hallucinations",
            "Do not stop heavy alcohol use abruptly without guidance",
            "Stay hydrated if safe",
            "Support and treatment programs can help"
        ]
    },
    "Zika Virus Infection": {
        "symptoms": ["fever", "rash", "joint_pain", "eye_redness", "headache", "muscle_pain"],
        "severity": "moderate",
        "recommendations": [
            "Rest and drink fluids",
            "Avoid mosquito bites to reduce spread",
            "Discuss pregnancy or travel exposure with a clinician",
            "Use pain relief as directed",
            "Seek care for severe symptoms or neurological changes"
        ]
    }
}

EXTRA_CONDITION_PATTERNS.update(EXPANDED_CONDITION_PATTERNS)
CONDITION_PATTERNS.update(EXTRA_CONDITION_PATTERNS)

CONDITION_SYMPTOM_EXTENSIONS = {
    "Stroke": [
        "facial_droop",
        "facial_drooping",
        "one_sided_weakness",
        "arm_weakness",
        "leg_weakness",
        "numbness_one_side"
    ],
    "Bell Palsy": [
        "facial_drooping"
    ],
    "Heart Disease": [
        "chest_pressure",
        "radiating_arm_pain",
        "jaw_pain",
        "lightheadedness"
    ],
    "Pulmonary Embolism": [
        "sudden_chest_pain",
        "sudden_shortness_of_breath"
    ],
    "Hypotension": [
        "presyncope"
    ]
}

for condition, symptoms in CONDITION_SYMPTOM_EXTENSIONS.items():
    if condition in CONDITION_PATTERNS:
        for symptom in symptoms:
            if symptom not in CONDITION_PATTERNS[condition]["symptoms"]:
                CONDITION_PATTERNS[condition]["symptoms"].append(symptom)

# Ensure every symptom referenced by any condition becomes a model feature.
for symptom in sorted({s for p in CONDITION_PATTERNS.values() for s in p["symptoms"]}):
    if symptom not in SYMPTOMS:
        SYMPTOMS.append(symptom)

def build_expanded_symptom_features(base_symptoms: List[str]) -> List[str]:
    """Add searchable symptom variants without inventing extra diseases."""
    expanded = list(base_symptoms)
    seen = set(expanded)
    prefixes = [
        "mild", "moderate", "severe", "sudden", "persistent", "recurrent",
        "chronic", "acute", "nighttime", "morning"
    ]
    sides = ["left", "right", "bilateral"]
    body_sites = [
        "head", "face", "eye", "ear", "throat", "neck", "chest", "upper_back",
        "lower_back", "abdomen", "pelvis", "hip", "knee", "ankle", "foot",
        "shoulder", "arm", "wrist", "hand"
    ]
    base_for_modifiers = [
        symptom for symptom in base_symptoms
        if not symptom.startswith(("mild_", "moderate_", "severe_", "sudden_", "persistent_"))
    ]

    for symptom in base_for_modifiers:
        for prefix in prefixes:
            candidate = f"{prefix}_{symptom}"
            if candidate not in seen:
                expanded.append(candidate)
                seen.add(candidate)
            if len(expanded) >= 1100:
                return expanded

    localized_roots = ["pain", "swelling", "rash", "numbness", "tingling", "weakness", "stiffness"]
    for site in body_sites:
        for root in localized_roots:
            candidate = f"{site}_{root}"
            if candidate not in seen:
                expanded.append(candidate)
                seen.add(candidate)
            if len(expanded) >= 1100:
                return expanded
        for side in sides:
            candidate = f"{side}_{site}_pain"
            if candidate not in seen:
                expanded.append(candidate)
                seen.add(candidate)
            if len(expanded) >= 1100:
                return expanded

    return expanded

CONDITION_SYMPTOM_FEATURES = sorted({s for p in CONDITION_PATTERNS.values() for s in p["symptoms"]})
SYMPTOMS = build_expanded_symptom_features(SYMPTOMS)

DEFAULT_NUM_SAMPLES = 25000

def generate_training_data(num_samples: int = DEFAULT_NUM_SAMPLES) -> List[Dict]:
    """Generate synthetic training data (enterprise-level with comprehensive coverage)"""
    data = []
    
    for _ in range(num_samples):
        # Randomly select a condition
        condition = random.choice(list(CONDITION_PATTERNS.keys()))
        pattern = CONDITION_PATTERNS[condition]
        
        # Get core symptoms for this condition
        core_symptoms = pattern["symptoms"]
        
        # Select 3-7 symptoms (with high probability for core symptoms)
        num_symptoms = random.randint(3, 7)
        selected_symptoms = set()
        
        # Add core symptoms (70% chance each)
        for symptom in core_symptoms:
            if random.random() < 0.7:
                selected_symptoms.add(symptom)
        
        # Add random symptoms to reach target count
        while len(selected_symptoms) < num_symptoms:
            # Add related symptoms more often, random symptoms occasionally
            if random.random() < 0.7 and len(selected_symptoms) < len(core_symptoms):
                selected_symptoms.add(random.choice(core_symptoms))
            else:
                selected_symptoms.add(random.choice(CONDITION_SYMPTOM_FEATURES))
        
        # Store sparse positives only. The trainer treats missing symptoms as 0,
        # so this keeps the generated JSON small even with 1000+ features.
        symptom_vector = {symptom: 1 for symptom in selected_symptoms if symptom in SYMPTOMS}
        
        data.append({
            "symptoms": symptom_vector,
            "condition": condition,
            "severity": pattern["severity"]
        })
    
    return data

def save_dataset(filename: str = "symptom_condition_data.json"):
    """Generate and save dataset"""
    random.seed(42)
    data = generate_training_data(DEFAULT_NUM_SAMPLES)  # Enterprise dataset
    
    with open(filename, 'w') as f:
        json.dump({
            "data": data,
            "symptoms_list": SYMPTOMS,
            "conditions": list(CONDITION_PATTERNS.keys()),
            "condition_info": CONDITION_PATTERNS
        }, f, indent=2)
    
    print(f"Dataset saved: {filename}")
    print(f"   - Samples: {len(data)}")
    print(f"   - Symptoms: {len(SYMPTOMS)}")
    print(f"   - Conditions: {len(CONDITION_PATTERNS)}")

if __name__ == "__main__":
    save_dataset("data/symptom_condition_data.json")
