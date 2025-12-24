
import pandas as pd
import numpy as np

# Settings
n_samples = 100000  # Even larger dataset
np.random.seed(42)

# Automatically expanded symptom and diagnosis lists
symptoms = [
    'fever', 'cough', 'headache', 'sore_throat', 'shortness_of_breath', 'body_pain', 'loss_of_smell', 'loss_of_taste', 'diarrhea', 'chills',
    'nausea', 'vomiting', 'rash', 'runny_nose', 'chest_pain', 'dizziness', 'fatigue', 'abdominal_pain', 'eye_pain', 'joint_pain', 'ear_pain',
    'congestion', 'sneezing', 'weight_loss', 'weight_gain', 'night_sweats', 'palpitations', 'anxiety', 'depression', 'insomnia', 'blurred_vision',
    'back_pain', 'constipation', 'itching', 'swelling', 'bleeding', 'urinary_pain', 'frequent_urination', 'hair_loss', 'dry_skin', 'yellow_skin',
    'red_eyes', 'hoarseness', 'difficulty_swallowing', 'memory_loss', 'confusion', 'tremor', 'muscle_weakness', 'numbness', 'tingling',
    'loss_of_balance', 'speech_difficulty', 'hearing_loss', 'wheezing', 'cyanosis', 'enlarged_lymph_nodes', 'abnormal_heartbeat', 'cold_extremities',
    'excessive_thirst', 'excessive_hunger', 'sweating', 'vomiting_blood', 'blood_in_stool', 'chest_tightness', 'difficulty_breathing', 'muscle_cramps',
    'seizures', 'fainting', 'irritability', 'agitation', 'hallucinations', 'delusions', 'paranoia', 'panic_attacks', 'obsessions', 'compulsions',
    'hyperactivity', 'impulsivity', 'social_withdrawal', 'apathy', 'emotional_lability', 'crying_spells', 'euphoria', 'mania', 'hypomania', 'hypersomnia',
    'restlessness', 'tics', 'stuttering', 'clumsiness', 'difficulty_concentrating', 'forgetfulness', 'disorientation', 'difficulty_walking',
    'difficulty_writing', 'difficulty_reading', 'difficulty_calculating', 'difficulty_recognizing_faces', 'difficulty_recognizing_objects',
    'difficulty_speaking', 'difficulty_understanding_speech', 'difficulty_chewing', 'skin_discoloration', 'muscle_stiffness', 'photophobia',
    'sensitivity_to_noise', 'swollen_glands', 'loss_of_appetite', 'increased_appetite', 'dry_mouth', 'mouth_ulcers', 'tooth_pain', 'gum_bleeding',
    'bad_breath', 'neck_pain', 'shoulder_pain', 'hip_pain', 'knee_pain', 'ankle_pain', 'foot_pain', 'hand_pain', 'finger_pain', 'toe_pain',
    'nail_changes', 'easy_bruising', 'slow_healing', 'frequent_infections', 'heat_intolerance', 'cold_intolerance', 'flushing', 'hives',
    'difficulty_hearing', 'difficulty_seeing', 'double_vision', 'eye_discharge', 'ear_discharge', 'nosebleeds', 'sinus_pain', 'jaw_pain',
    'voice_changes', 'difficulty_breathing_at_night', 'sleep_apnea', 'snoring', 'restless_legs', 'leg_cramps', 'muscle_twitching', 'muscle_aches',
    'joint_swelling', 'joint_stiffness', 'joint_redness', 'joint_warmth', 'joint_deformity', 'spinal_pain', 'pelvic_pain', 'groin_pain',
    'testicular_pain', 'scrotal_swelling', 'vaginal_discharge', 'vaginal_bleeding', 'painful_intercourse', 'urinary_incontinence', 'urinary_urgency',
    'urinary_retention', 'nocturia', 'polyuria', 'oliguria', 'hematuria', 'proteinuria', 'edema', 'ascites', 'jaundice', 'pruritus', 'hematemesis',
    'melena', 'rectal_bleeding', 'anal_pain', 'anal_itching', 'anal_discharge', 'anal_swelling', 'anal_fissures', 'anal_fistula', 'anal_abscess',
    'rectal_prolapse', 'fecal_incontinence', 'constipation', 'diarrhea', 'bowel_incontinence', 'bowel_obstruction', 'abdominal_distension',
    'abdominal_tenderness', 'abdominal_mass', 'abdominal_rigidity', 'abdominal_guarding', 'abdominal_bruit', 'abdominal_pulsation', 'abdominal_hernia',
    'abdominal_scars', 'abdominal_striae', 'abdominal_veins', 'abdominal_wall_pain', 'abdominal_wall_mass', 'abdominal_wall_hernia', 'abdominal_wall_scars',
    'abdominal_wall_striae', 'abdominal_wall_veins', 'abdominal_wall_pulsation', 'abdominal_wall_bruit', 'abdominal_wall_rigidity', 'abdominal_wall_guarding'
]
diagnoses = [
    'Flu', 'COVID-19', 'Migraine', 'Common Cold', 'Allergy', 'Healthy', 'Gastroenteritis', 'Sinusitis', 'Bronchitis', 'Pneumonia',
    'Anxiety Disorder', 'Depression', 'Insomnia', 'Otitis', 'Dermatitis', 'Asthma', 'Hypertension', 'Diabetes', 'Epilepsy', 'Stroke',
    'Parkinsons', 'Alzheimers', 'Multiple Sclerosis', 'Schizophrenia', 'Bipolar Disorder', 'Obsessive Compulsive Disorder', 'Panic Disorder',
    'ADHD', 'Autism Spectrum Disorder', 'Chronic Kidney Disease', 'Liver Disease', 'Heart Failure', 'Coronary Artery Disease', 'Tuberculosis',
    'Malaria', 'Dengue', 'Typhoid', 'Leukemia', 'Lymphoma', 'Melanoma', 'Psoriasis', 'Rheumatoid Arthritis', 'Lupus', 'Crohns Disease',
    'Ulcerative Colitis', 'Celiac Disease', 'Hyperthyroidism', 'Hypothyroidism', 'Polycystic Ovary Syndrome', 'Endometriosis', 'Fibromyalgia',
    'Gout', 'Scleroderma', 'Sjogrens Syndrome', 'Vasculitis', 'Sarcoidosis', 'Amyloidosis', 'Hemochromatosis', 'Wilson Disease', 'Addison Disease',
    'Cushings Syndrome', 'Pheochromocytoma', 'Acromegaly', 'Gigantism', 'Dwarfism', 'Turner Syndrome', 'Klinefelter Syndrome', 'Marfan Syndrome',
    'Ehlers-Danlos Syndrome', 'Down Syndrome', 'Fragile X Syndrome', 'Prader-Willi Syndrome', 'Angelman Syndrome', 'Williams Syndrome',
    'Noonan Syndrome', 'Alport Syndrome', 'Bartter Syndrome', 'Gitelman Syndrome', 'Liddle Syndrome', 'Nephrotic Syndrome', 'Nephritic Syndrome',
    'Goodpasture Syndrome', 'Wegener Granulomatosis', 'Churg-Strauss Syndrome', 'Microscopic Polyangiitis', 'Polyarteritis Nodosa',
    'Takayasu Arteritis', 'Giant Cell Arteritis', 'Behcet Disease', 'Kawasaki Disease', 'Henoch-Schonlein Purpura', 'Cryoglobulinemia',
    'Antiphospholipid Syndrome', 'Antithrombin Deficiency', 'Protein C Deficiency', 'Protein S Deficiency', 'Factor V Leiden', 'Prothrombin Mutation',
    'Hemophilia A', 'Hemophilia B', 'Von Willebrand Disease', 'Thalassemia', 'Sickle Cell Disease', 'Hereditary Spherocytosis', 'G6PD Deficiency',
    'Pyruvate Kinase Deficiency', 'Aplastic Anemia', 'Myelodysplastic Syndrome', 'Paroxysmal Nocturnal Hemoglobinuria', 'Fanconi Anemia',
    'Diamond-Blackfan Anemia', 'Shwachman-Diamond Syndrome', 'Kostmann Syndrome', 'Chediak-Higashi Syndrome', 'Griscelli Syndrome',
    'Hermansky-Pudlak Syndrome', 'Albinism', 'Oculocutaneous Albinism', 'Ocular Albinism', 'Xeroderma Pigmentosum', 'Cockayne Syndrome',
    'Trichothiodystrophy', 'Menkes Disease', 'Mucopolysaccharidosis', 'Gaucher Disease', 'Niemann-Pick Disease', 'Tay-Sachs Disease',
    'Sandhoff Disease', 'Krabbe Disease', 'Metachromatic Leukodystrophy', 'Adrenoleukodystrophy', 'Canavan Disease', 'Alexander Disease',
    'Pelizaeus-Merzbacher Disease', 'Spinal Muscular Atrophy', 'Friedreich Ataxia', 'Ataxia-Telangiectasia', 'Rett Syndrome', 'MECP2 Duplication Syndrome'
]


# Generate random binary symptom data
X = np.random.randint(0, 2, size=(n_samples, len(symptoms)))

# Generate diagnosis based on more complex rules for realism
Y = []
for row in X:
    # Example: COVID-19
    if row[symptoms.index('fever')] and row[symptoms.index('cough')] and row[symptoms.index('shortness_of_breath')] and row[symptoms.index('loss_of_smell')]:
        Y.append('COVID-19')
    # Example: Migraine
    elif row[symptoms.index('headache')] and row[symptoms.index('nausea')] and row[symptoms.index('vomiting')] and not row[symptoms.index('fever')]:
        Y.append('Migraine')
    # Example: Depression
    elif row[symptoms.index('depression')] and row[symptoms.index('insomnia')] and row[symptoms.index('apathy')]:
        Y.append('Depression')
    # Example: Diabetes
    elif row[symptoms.index('excessive_thirst')] and row[symptoms.index('frequent_urination')] and row[symptoms.index('weight_loss')]:
        Y.append('Diabetes')
    # Example: Epilepsy
    elif row[symptoms.index('seizures')] and row[symptoms.index('confusion')]:
        Y.append('Epilepsy')
    # Example: Asthma
    elif row[symptoms.index('wheezing')] and row[symptoms.index('shortness_of_breath')]:
        Y.append('Asthma')
    # Example: Heart Failure
    elif row[symptoms.index('chest_pain')] and row[symptoms.index('fatigue')] and row[symptoms.index('shortness_of_breath')]:
        Y.append('Heart Failure')
    # Example: Schizophrenia
    elif row[symptoms.index('hallucinations')] and row[symptoms.index('delusions')]:
        Y.append('Schizophrenia')
    # Example: Bipolar Disorder
    elif row[symptoms.index('mania')] and row[symptoms.index('depression')]:
        Y.append('Bipolar Disorder')
    # Example: Tuberculosis
    elif row[symptoms.index('cough')] and row[symptoms.index('night_sweats')] and row[symptoms.index('weight_loss')]:
        Y.append('Tuberculosis')
    # Example: Malaria
    elif row[symptoms.index('fever')] and row[symptoms.index('chills')] and row[symptoms.index('sweating')]:
        Y.append('Malaria')
    # Example: Dengue
    elif row[symptoms.index('fever')] and row[symptoms.index('rash')] and row[symptoms.index('headache')]:
        Y.append('Dengue')
    # Example: Celiac Disease
    elif row[symptoms.index('diarrhea')] and row[symptoms.index('weight_loss')] and row[symptoms.index('abdominal_pain')]:
        Y.append('Celiac Disease')
    # Example: Healthy
    elif not any(row):
        Y.append('Healthy')
    else:
        Y.append(np.random.choice(diagnoses))

# Create DataFrame
symptom_df = pd.DataFrame(X, columns=symptoms)
symptom_df['diagnosis'] = Y

# Save to CSV
symptom_df.to_csv('data/symptom_data.csv', index=False)
print('Large synthetic dataset with more symptoms saved to data/symptom_data.csv')
