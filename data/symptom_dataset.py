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

def generate_training_data(num_samples: int = 5000) -> List[Dict]:
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
                selected_symptoms.add(random.choice(SYMPTOMS))
        
        # Create symptom vector
        symptom_vector = {symptom: 0 for symptom in SYMPTOMS}
        for symptom in selected_symptoms:
            if symptom in symptom_vector:
                symptom_vector[symptom] = 1
        
        data.append({
            "symptoms": symptom_vector,
            "condition": condition,
            "severity": pattern["severity"]
        })
    
    return data

def save_dataset(filename: str = "symptom_condition_data.json"):
    """Generate and save dataset"""
    data = generate_training_data(5000)  # Enterprise dataset
    
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
