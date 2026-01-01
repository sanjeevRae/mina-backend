"""
Symptom-Condition Dataset Generator
Based on open medical knowledge and common health conditions
"""
import json
import random
from typing import List, Dict

# Common symptoms (83 symptoms based on medical literature)
SYMPTOMS = [
    # General symptoms
    "fever", "fatigue", "weakness", "chills", "night_sweats", "weight_loss", 
    "weight_gain", "loss_of_appetite", "nausea", "vomiting", "dizziness",
    
    # Respiratory
    "cough", "shortness_of_breath", "chest_pain", "wheezing", "sore_throat",
    "runny_nose", "congestion", "sneezing",
    
    # Digestive
    "abdominal_pain", "diarrhea", "constipation", "bloating", "heartburn",
    "difficulty_swallowing", "blood_in_stool",
    
    # Musculoskeletal
    "joint_pain", "muscle_pain", "back_pain", "neck_pain", "stiffness",
    "swelling", "numbness", "tingling",
    
    # Neurological
    "headache", "migraine", "confusion", "memory_loss", "seizures",
    "loss_of_consciousness", "tremors", "coordination_problems",
    
    # Cardiovascular
    "palpitations", "irregular_heartbeat", "chest_tightness", "leg_swelling",
    
    # Skin
    "rash", "itching", "skin_redness", "hives", "dry_skin", "bruising",
    
    # ENT (Ear, Nose, Throat)
    "ear_pain", "hearing_loss", "ringing_in_ears", "vision_changes",
    "eye_pain", "sensitivity_to_light",
    
    # Urinary
    "frequent_urination", "painful_urination", "blood_in_urine", "dark_urine",
    
    # Respiratory/Throat
    "difficulty_breathing", "hoarseness", "persistent_cough",
    
    # Mental Health
    "anxiety", "depression", "insomnia", "irritability", "mood_swings",
    
    # Other
    "sweating", "dehydration", "thirst", "pale_skin", "yellowing_skin",
    "swollen_lymph_nodes", "mouth_sores", "bleeding_gums"
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
    }
}

def generate_training_data(num_samples: int = 1000) -> List[Dict]:
    """Generate synthetic training data (reduced for faster training)"""
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
    data = generate_training_data(1000)  # Reduced for faster generation
    
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
