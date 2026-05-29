"""
ML Inference Service for Symptom Checker
Memory-optimized lightweight service for Render free tier
"""
import json
import numpy as np
import joblib
import re
from difflib import get_close_matches
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import lightgbm as lgb
import logging

logger = logging.getLogger(__name__)

SYMPTOM_ALIASES = {
    "abdomen pain": "abdominal_pain",
    "abdominal ache": "abdominal_pain",
    "belly ache": "abdominal_pain",
    "belly pain": "abdominal_pain",
    "stomach ache": "abdominal_pain",
    "stomach pain": "abdominal_pain",
    "stomach cramps": "stomach_cramps",
    "tummy ache": "abdominal_pain",
    "tummy pain": "abdominal_pain",
    "lower belly pain": "lower_abdominal_pain",
    "right upper belly pain": "right_upper_abdominal_pain",
    "right upper abdominal pain": "right_upper_abdominal_pain",
    "flank pain": "flank_pain",
    "side pain": "flank_pain",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "loose stool": "diarrhea",
    "loose stools": "diarrhea",
    "watery stool": "diarrhea",
    "watery stools": "diarrhea",
    "throwing up": "vomiting",
    "throw up": "vomiting",
    "puking": "vomiting",
    "feel sick": "nausea",
    "feeling sick": "nausea",
    "high temperature": "fever",
    "temperature": "fever",
    "mild temperature": "mild_fever",
    "low grade fever": "mild_fever",
    "very high fever": "high_fever",
    "body pain": "body_aches",
    "body ache": "body_aches",
    "body aches": "body_aches",
    "muscle ache": "muscle_pain",
    "muscle aches": "muscle_pain",
    "joint ache": "joint_pain",
    "joint aches": "joint_pain",
    "breathlessness": "shortness_of_breath",
    "short of breath": "shortness_of_breath",
    "difficulty breathing": "difficulty_breathing",
    "trouble breathing": "difficulty_breathing",
    "can't breathe": "difficulty_breathing",
    "cannot breathe": "difficulty_breathing",
    "chest tight": "chest_tightness",
    "tight chest": "chest_tightness",
    "heart racing": "rapid_heartbeat",
    "fast heartbeat": "rapid_heartbeat",
    "fast heart beat": "rapid_heartbeat",
    "irregular heart beat": "irregular_heartbeat",
    "high bp": "high_blood_pressure",
    "high blood pressure": "high_blood_pressure",
    "blood pressure high": "high_blood_pressure",
    "low bp": "low_blood_pressure",
    "low blood pressure": "low_blood_pressure",
    "blood pressure low": "low_blood_pressure",
    "runny nose": "runny_nose",
    "blocked nose": "congestion",
    "stuffy nose": "congestion",
    "nose bleed": "nosebleeds",
    "nosebleed": "nosebleeds",
    "sore throat": "sore_throat",
    "throat pain": "sore_throat",
    "red eye": "red_eyes",
    "red eyes": "red_eyes",
    "pink eye": "eye_redness",
    "eye infection": "eye_redness",
    "dry eyes": "dry_eyes",
    "dry eye": "dry_eyes",
    "ringing ears": "tinnitus",
    "ringing in ear": "tinnitus",
    "ringing in ears": "tinnitus",
    "ear ache": "ear_pain",
    "earache": "ear_pain",
    "ear discharge": "otorrhea",
    "ear drainage": "otorrhea",
    "blocked ear": "ear_fullness",
    "ear fullness": "ear_fullness",
    "blurry vision": "blurred_vision",
    "blurred eyesight": "blurred_vision",
    "double eyesight": "double_vision",
    "light sensitivity": "sensitivity_to_light",
    "sensitive to light": "sensitivity_to_light",
    "pee pain": "painful_urination",
    "burning pee": "painful_urination",
    "burning urination": "painful_urination",
    "pain while urinating": "painful_urination",
    "painful pee": "painful_urination",
    "frequent pee": "frequent_urination",
    "frequent urination": "frequent_urination",
    "blood urine": "blood_in_urine",
    "blood in pee": "blood_in_urine",
    "dark pee": "dark_urine",
    "cloudy pee": "cloudy_urine",
    "foamy pee": "foamy_urine",
    "trouble peeing": "difficulty_urinating",
    "cannot pee": "urinary_retention",
    "cant pee": "urinary_retention",
    "swollen legs": "leg_swelling",
    "swollen ankles": "ankle_swelling",
    "swollen glands": "swollen_lymph_nodes",
    "swollen lymph nodes": "swollen_lymph_nodes",
    "yellow skin": "yellowing_skin",
    "yellow eyes": "jaundice",
    "skin yellowing": "jaundice",
    "itchy skin": "itching",
    "itchy": "itching",
    "skin burning": "burning",
    "burning skin": "burning",
    "hive": "hives",
    "hives": "hives",
    "period pain": "painful_periods",
    "painful periods": "painful_periods",
    "irregular period": "menstrual_irregularities",
    "irregular periods": "menstrual_irregularities",
    "missed period": "missed_period",
    "pms": "premenstrual_symptoms",
    "white discharge": "vaginal_discharge",
    "vaginal itching": "vaginal_itching",
    "vaginal itch": "vaginal_itching",
    "vaginal dryness": "vaginal_dryness",
    "hot flashes": "hot_flashes",
    "hot flushes": "hot_flashes",
    "panic": "panic_attacks",
    "panic attack": "panic_attacks",
    "panic attacks": "panic_attacks",
    "cannot sleep": "insomnia",
    "can't sleep": "insomnia",
    "trouble sleeping": "difficulty_sleeping",
    "sleep problem": "sleep_problems",
    "sleep problems": "sleep_problems",
    "low mood": "depression",
    "sadness": "depression",
    "worried": "anxiety",
    "worry": "anxiety",
    "tired": "fatigue",
    "tiredness": "fatigue",
    "exhausted": "fatigue",
    "low energy": "fatigue",
    "weak": "weakness",
    "weakness": "weakness",
    "dizzy": "dizziness",
    "dizzyness": "dizziness",
    "faint": "fainting",
    "fainted": "fainting",
    "pass out": "loss_of_consciousness",
    "passed out": "loss_of_consciousness",
    "face drooping": "facial_droop",
    "facial droop": "facial_droop",
    "slurred speech": "speech_difficulty",
    "one sided weakness": "one_sided_weakness",
    "one-sided weakness": "one_sided_weakness",
    "coughing fits": "paroxysmal_cough",
    "whooping cough": "whooping_cough",
    "lost smell": "loss_of_smell",
    "loss smell": "loss_of_smell",
    "lost taste": "loss_of_taste",
    "loss taste": "loss_of_taste",
    "mouth fungus": "oral_thrush",
    "white patches mouth": "white_patches_in_mouth",
    "tooth ache": "tooth_pain",
    "toothache": "tooth_pain",
    "heel pain": "heel_pain",
    "painful heel": "heel_pain",
    "raynaud": "color_changes_in_fingers",
    "cold fingers": "cold_hands",
}

CHAT_GREETINGS = {
    "hi", "hello", "hey", "namaste", "good morning", "good afternoon",
    "good evening", "help me", "can you help me"
}

CHAT_HELP_TERMS = {
    "help", "how to use", "how do i use", "what can you do", "guide",
    "instructions", "usage", "symptom checker", "how it works"
}

CHAT_THANKS = {"thanks", "thank you", "thx", "ok thanks", "okay thanks"}

OUT_OF_SCOPE_TERMS = {
    "weather", "movie", "music", "joke", "football", "cricket", "stock",
    "coding", "homework", "travel", "restaurant", "shopping"
}

STOP_TERMS = {
    "i", "im", "am", "have", "has", "having", "feel", "feeling", "with",
    "and", "or", "the", "a", "an", "my", "me", "is", "are", "was", "were",
    "for", "since", "from", "please", "what", "should", "do", "can", "you",
    "but", "also", "very", "really", "today", "yesterday", "days", "day",
    "week", "weeks", "month", "months",
    "this"
}

NEGATION_TERMS = {
    "no", "not", "never", "without", "denies", "deny", "none", "dont",
    "doesnt", "didnt", "cannot", "cant"
}

EMERGENCY_CHAT_TERMS = {
    "emergency", "urgent", "911", "ambulance", "cant breathe",
    "cannot breathe", "severe chest pain", "chest pressure",
    "face drooping", "slurred speech", "one sided weakness",
    "unconscious", "passed out", "seizure", "blue lips",
    "vomiting blood", "black stool", "worst headache"
}

SEVERITY_TERMS = {
    "mild": "mild",
    "little": "mild",
    "moderate": "moderate",
    "bad": "moderate",
    "severe": "severe",
    "very bad": "severe",
    "unbearable": "severe",
    "worst": "severe"
}


class SymptomCheckerService:
    """Lightweight symptom checker inference service"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure single model instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize service (loads model on first access)"""
        if self._initialized:
            return
            
        self.model = None
        self.label_encoder = None
        self.symptoms_list = None
        self.condition_info = None
        self.metadata = None
        self.model_load_error = None
        self._initialized = True
        
    def load_model(self, model_dir: str = "models/symptom_checker"):
        """Load model and metadata (lazy loading)"""
        if self.model is not None or (self.condition_info is not None and self.model_load_error is not None):
            return  # Already loaded
            
        model_path = Path(model_dir)
        
        try:
            metadata_file = model_path / "metadata.json"
            label_encoder_file = model_path / "label_encoder.pkl"
            model_file = model_path / "lightgbm_model.txt"

            if not all(path.exists() for path in [metadata_file, label_encoder_file, model_file]):
                logger.warning(f"Symptom checker files missing in {model_path}. Auto-training model...")
                self._auto_train_model()
            
            # Load metadata
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)
            
            self.symptoms_list = self.metadata.get('symptoms_list') or []
            self.condition_info = self.metadata.get('condition_info') or {}

            if not self.symptoms_list:
                raise ValueError("Symptom checker metadata is missing symptoms_list")
            
            # Load label encoder
            self.label_encoder = joblib.load(label_encoder_file)

            try:
                self.model = lgb.Booster(model_file=str(model_file))
                self.model_load_error = None
            except Exception as e:
                self.model = None
                self.model_load_error = e
                logger.exception("Failed to load LightGBM symptom model; rule-based fallback will be used")
            
            logger.info("Symptom checker metadata loaded successfully")
            logger.info(f"   - Features: {len(self.symptoms_list)}")
            logger.info(f"   - Conditions: {len(self.condition_info)}")
            logger.info(f"   - LightGBM model loaded: {self.model is not None}")
            
        except Exception as e:
            logger.error(f"Failed to load symptom checker model: {e}")
            raise
    
    def preprocess_symptoms(self, symptoms: List[str]) -> np.ndarray:
        """Convert symptom list to feature vector"""
        # Ensure model is loaded
        if self.symptoms_list is None:
            self.load_model()
        
        # Create feature vector
        feature_vector = np.zeros(len(self.symptoms_list), dtype=np.float32)
        
        # Normalize symptom names (lowercase, replace spaces with underscores)
        normalized_symptoms = [self._normalize_symptom(s) for s in symptoms]
        
        for i, symptom in enumerate(self.symptoms_list):
            if symptom in normalized_symptoms:
                feature_vector[i] = 1.0
        
        return feature_vector.reshape(1, -1)
    
    def predict(self, symptoms: List[str], top_k: int = 3) -> List[Dict]:
        """
        Predict conditions from symptoms
        
        Args:
            symptoms: List of symptom names
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions with conditions, confidence, and recommendations
        """
        # Ensure model is loaded
        if self.symptoms_list is None:
            self.load_model()

        if self.model is None:
            return self._fallback_predict(symptoms, top_k=top_k, error=self.model_load_error)
        
        try:
            # Preprocess and predict probabilities. Keep both operations in the
            # fallback boundary because LightGBM can raise native errors such as
            # unordered_map::at when model metadata is inconsistent.
            X = self.preprocess_symptoms(symptoms)

            # Predict probabilities
            probabilities = self.model.predict(X)[0]
        except Exception as e:
            logger.exception("LightGBM symptom prediction failed; using rule-based fallback")
            return self._fallback_predict(symptoms, top_k=top_k, error=e)
        
        # Get top k predictions
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        predictions = []
        for idx in top_indices:
            condition = str(self.label_encoder.classes_[idx])
            confidence = float(probabilities[idx])
            
            # Get condition info
            condition_details = self.condition_info.get(condition, {})
            
            predictions.append({
                "condition": condition,
                "confidence": round(confidence * 100, 2),
                "severity": condition_details.get("severity", "unknown"),
                "recommendations": condition_details.get("recommendations", []),
                "matched_symptoms": [s for s in symptoms if self._normalize_symptom(s)
                                   in condition_details.get("symptoms", [])]
            })

        if predictions and predictions[0]["confidence"] < 20:
            fallback_predictions = self._fallback_predict(symptoms, top_k=top_k)
            if fallback_predictions and fallback_predictions[0]["confidence"] > predictions[0]["confidence"]:
                return fallback_predictions

        return predictions

    def _fallback_predict(self, symptoms: List[str], top_k: int = 3, error: Optional[Exception] = None) -> List[Dict]:
        """Rank conditions by symptom overlap when model inference fails."""
        if not self.condition_info:
            if error:
                raise error
            return []

        normalized_symptoms = {self._normalize_symptom(s) for s in symptoms}
        normalized_symptoms.discard("")
        scored_conditions = []

        for condition, details in self.condition_info.items():
            condition_symptoms = set(details.get("symptoms", []))
            if not condition_symptoms:
                continue

            matched = normalized_symptoms.intersection(condition_symptoms)
            if not matched:
                continue

            coverage = len(matched) / len(condition_symptoms)
            input_match = len(matched) / max(len(normalized_symptoms), 1)
            score = (coverage * 0.6) + (input_match * 0.4)
            scored_conditions.append((score, condition, details, matched))

        scored_conditions.sort(key=lambda item: item[0], reverse=True)

        predictions = []
        for score, condition, details, matched in scored_conditions[:top_k]:
            predictions.append({
                "condition": str(condition),
                "confidence": round(score * 100, 2),
                "severity": details.get("severity", "unknown"),
                "recommendations": details.get("recommendations", []),
                "matched_symptoms": [
                    symptom for symptom in symptoms
                    if self._normalize_symptom(symptom) in matched
                ]
            })

        return predictions

    @staticmethod
    def _normalize_symptom(symptom: str) -> str:
        """Normalize user-entered symptom names to the model feature format."""
        if symptom is None:
            return ""
        normalized = str(symptom).strip().lower().replace("-", " ")
        normalized = " ".join(normalized.split())
        alias = SYMPTOM_ALIASES.get(normalized)
        if alias:
            return alias
        return normalized.replace(" ", "_")
    
    def get_all_symptoms(self) -> List[str]:
        """Get list of all recognized symptoms"""
        if self.model is None:
            self.load_model()
        
        # Convert to readable format
        return [symptom.replace('_', ' ').title() for symptom in self.symptoms_list]
    
    def get_condition_info(self, condition_name: str) -> Optional[Dict]:
        """Get detailed information about a condition"""
        if self.model is None:
            self.load_model()
        
        return self.condition_info.get(condition_name)
    
    def validate_symptoms(self, symptoms: List[str]) -> Tuple[List[str], List[str]]:
        """
        Validate symptoms against known symptom list
        
        Returns:
            Tuple of (valid_symptoms, unknown_symptoms)
        """
        if self.model is None:
            self.load_model()
        
        normalized_input = [self._normalize_symptom(s) for s in symptoms]
        
        valid = []
        unknown = []
        
        for i, symptom in enumerate(symptoms):
            if normalized_input[i] in self.symptoms_list:
                valid.append(symptom)
            else:
                unknown.append(symptom)
        
        return valid, unknown

    def chat(self, message: str) -> Dict:
        """Small rule-based chat layer for normal symptom checker conversation."""
        if self.symptoms_list is None:
            self.load_model()

        text = self._normalize_chat_text(message)
        extracted_symptoms, unknown_terms = self.extract_symptoms_from_text(message)
        context = self._extract_message_context(text)

        if self._contains_any(text, EMERGENCY_CHAT_TERMS) and not extracted_symptoms:
            return {
                "intent": "emergency_guidance",
                "response": "That may be urgent. If there is severe chest pain, stroke signs, trouble breathing, seizure, fainting, or heavy bleeding, seek emergency medical help now.",
                "extracted_symptoms": [],
                "unknown_terms": unknown_terms,
                "predictions": [],
                "suggestions": [
                    "Call local emergency services if symptoms are severe",
                    "Do not drive yourself during a possible emergency",
                    "Tell me the symptoms if you want a basic symptom check"
                ]
            }

        if self._contains_any(text, CHAT_THANKS):
            return {
                "intent": "thanks",
                "response": "You're welcome. Keep monitoring how you feel, and seek medical care if symptoms become severe or worrying.",
                "extracted_symptoms": extracted_symptoms,
                "unknown_terms": unknown_terms,
                "predictions": [],
                "suggestions": [
                    "Tell me symptoms in one sentence",
                    "Example: I have fever, cough, and chest pain"
                ]
            }

        if self._contains_any(text, CHAT_GREETINGS) and not extracted_symptoms:
            return {
                "intent": "greeting",
                "response": "Hi, I can help you check possible conditions from symptoms. Tell me what you are feeling, like: I have fever, cough, headache, and sore throat.",
                "extracted_symptoms": [],
                "unknown_terms": unknown_terms,
                "predictions": [],
                "suggestions": [
                    "Describe 2 to 6 symptoms",
                    "Mention emergency symptoms immediately",
                    "Use /symptom-checker/symptoms to see supported symptoms"
                ]
            }

        if self._contains_any(text, CHAT_HELP_TERMS) and not extracted_symptoms:
            return {
                "intent": "help",
                "response": "Send your symptoms in simple language. I will extract the symptoms I recognize, check possible conditions, and share basic next steps. This is not a diagnosis.",
                "extracted_symptoms": [],
                "unknown_terms": unknown_terms,
                "predictions": [],
                "suggestions": [
                    "Example: I have burning urination and lower belly pain",
                    "Example: I feel dizzy with chest pressure",
                    "For severe chest pain, stroke signs, or trouble breathing, seek emergency care"
                ]
            }

        if extracted_symptoms:
            predictions = self.predict(extracted_symptoms, top_k=3)
            if predictions:
                top = predictions[0]
                symptom_text = ", ".join(symptom.replace("_", " ") for symptom in extracted_symptoms)
                response = (
                    f"I found {len(extracted_symptoms)} symptom(s): "
                    f"{symptom_text}. The closest match is "
                    f"{top['condition']} ({top['confidence']}% confidence). "
                    "Use this as guidance only, not a diagnosis."
                )
                if context.get("duration"):
                    response += f" I noticed the duration: {context['duration']}."
                if context.get("severity"):
                    response += f" You described the severity as {context['severity']}."
                if top.get("severity") == "emergency" or context.get("emergency"):
                    response = (
                        response
                        + " These symptoms may be urgent. Please seek emergency medical help now."
                    )
            else:
                response = (
                    f"I recognized {', '.join(extracted_symptoms)}, but I could not find a strong match. "
                    "Please add more symptoms or consult a healthcare professional."
                )

            return {
                "intent": "symptom_report",
                "response": response,
                "extracted_symptoms": extracted_symptoms,
                "unknown_terms": unknown_terms,
                "predictions": predictions,
                "suggestions": [
                    "Add symptom duration and severity",
                    "Say if a symptom is absent, for example: fever but no cough",
                    "Add other symptoms you are feeling",
                    "Seek urgent care for chest pain, stroke signs, severe breathing trouble, or confusion"
                ]
            }

        if self._contains_any(text, OUT_OF_SCOPE_TERMS):
            return {
                "intent": "out_of_scope",
                "response": "I am focused on symptom checking and basic wellness guidance. Tell me your symptoms and I will try to help safely.",
                "extracted_symptoms": [],
                "unknown_terms": unknown_terms,
                "predictions": [],
                "suggestions": [
                    "Example: I have fever and body aches",
                    "Example: I have stomach pain and vomiting"
                ]
            }

        return {
            "intent": "unknown",
            "response": "I did not recognize symptoms in that message. Please describe what you feel using simple words, for example: fever, cough, headache, stomach pain, dizziness, or rash.",
            "extracted_symptoms": [],
            "unknown_terms": unknown_terms,
            "predictions": [],
            "suggestions": [
                "Try listing symptoms separated by commas",
                "Use common words like toothache, pink eye, or sore throat",
                "Use /symptom-checker/symptoms to see supported symptoms"
            ]
        }

    def extract_symptoms_from_text(self, message: str) -> Tuple[List[str], List[str]]:
        """Extract known symptoms from free text using aliases and symptom names."""
        if self.symptoms_list is None:
            self.load_model()

        text = self._normalize_chat_text(message)
        found = []
        found_set = set()
        matched_spans = []

        phrase_map = self._build_phrase_map()

        for phrase in sorted(phrase_map, key=len, reverse=True):
            canonical = phrase_map[phrase]
            if canonical not in self.symptoms_list:
                continue
            for match in re.finditer(rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])", text):
                span = match.span()
                if self._span_overlaps(span, matched_spans):
                    continue
                if self._is_negated(text, span[0]):
                    matched_spans.append(span)
                    continue
                if canonical not in found_set:
                    found.append(canonical)
                    found_set.add(canonical)
                matched_spans.append(span)

        fuzzy_matches = self._fuzzy_symptom_matches(text, phrase_map, matched_spans)
        for canonical, span in fuzzy_matches:
            if canonical in self.symptoms_list and canonical not in found_set:
                found.append(canonical)
                found_set.add(canonical)
            matched_spans.append(span)

        if found:
            return found, self._unknown_terms_from_text(text, matched_spans)

        return [], self._unknown_terms_from_text(text, matched_spans)
    
    def get_wellness_advice(self, symptoms: List[str]) -> Dict:
        """Get general wellness advice based on symptoms"""
        predictions = self.predict(symptoms, top_k=1)
        
        if not predictions:
            return {
                "advice": [
                    "Stay hydrated and get adequate rest",
                    "Monitor your symptoms",
                    "Consult a healthcare provider if symptoms persist"
                ]
            }
        
        top_condition = predictions[0]
        
        general_advice = [
            "This is an AI-based suggestion and not a medical diagnosis",
            "Consult a healthcare professional for proper diagnosis and treatment"
        ]
        
        return {
            "primary_condition": top_condition["condition"],
            "confidence": top_condition["confidence"],
            "severity": top_condition["severity"],
            "recommendations": top_condition["recommendations"],
            "general_advice": general_advice,
            "when_to_seek_help": self._get_urgency_advice(top_condition["severity"])
        }
    
    def _get_urgency_advice(self, severity: str) -> List[str]:
        """Get urgency advice based on severity"""
        if severity == "serious":
            return [
                "⚠️ Seek medical attention promptly",
                "Consider visiting a healthcare provider soon",
                "Monitor symptoms closely"
            ]
        elif severity == "moderate":
            return [
                "Schedule an appointment with your healthcare provider",
                "Monitor symptoms for 24-48 hours",
                "Seek immediate help if symptoms worsen"
            ]
        else:  # mild
            return [
                "Self-care measures may help",
                "Seek medical advice if symptoms persist beyond a week",
                "Contact healthcare provider if symptoms worsen"
            ]

    @staticmethod
    def _normalize_chat_text(message: str) -> str:
        text = str(message or "").strip().lower().replace("-", " ")
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return " ".join(text.split())

    def _build_phrase_map(self) -> Dict[str, str]:
        phrase_map = {}
        for symptom in self.symptoms_list or []:
            readable = symptom.replace("_", " ")
            phrase_map[readable] = symptom
        phrase_map.update(SYMPTOM_ALIASES)
        return phrase_map

    @staticmethod
    def _span_overlaps(span: Tuple[int, int], spans: List[Tuple[int, int]]) -> bool:
        start, end = span
        return any(start < existing_end and end > existing_start for existing_start, existing_end in spans)

    @staticmethod
    def _is_negated(text: str, start_index: int) -> bool:
        before = text[:start_index].split()[-4:]
        negation_positions = [i for i, term in enumerate(before) if term in NEGATION_TERMS]
        if not negation_positions:
            return False
        connector_positions = [i for i, term in enumerate(before) if term in {"but", "except"}]
        return not connector_positions or max(connector_positions) < max(negation_positions)

    def _fuzzy_symptom_matches(
        self,
        text: str,
        phrase_map: Dict[str, str],
        matched_spans: List[Tuple[int, int]]
    ) -> List[Tuple[str, Tuple[int, int]]]:
        """Catch small typos such as fevr, couhg, dizzyness, or nausia."""
        words = re.findall(r"[a-z0-9]+", text)
        known_single_words = {
            phrase: canonical
            for phrase, canonical in phrase_map.items()
            if " " not in phrase and len(phrase) >= 5 and canonical in (self.symptoms_list or [])
        }

        fuzzy = []
        for word in words:
            if len(word) < 4 or word in STOP_TERMS:
                continue
            matches = get_close_matches(word, known_single_words.keys(), n=1, cutoff=0.76)
            if not matches:
                continue
            match = matches[0]
            canonical = known_single_words[match]
            word_match = re.search(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", text)
            if word_match and (
                self._span_overlaps(word_match.span(), matched_spans)
                or self._is_negated(text, word_match.start())
            ):
                continue
            fuzzy.append((canonical, word_match.span() if word_match else (0, 0)))
        return fuzzy[:3]

    @staticmethod
    def _unknown_terms_from_text(text: str, matched_spans: List[Tuple[int, int]]) -> List[str]:
        remaining = list(text)
        for start, end in matched_spans:
            for index in range(start, end):
                if index < len(remaining):
                    remaining[index] = " "
        words = [
            word for word in re.findall(r"[a-z0-9]+", "".join(remaining))
            if len(word) > 3 and word not in STOP_TERMS and word not in NEGATION_TERMS
        ]
        return words[:5]

    @staticmethod
    def _extract_message_context(text: str) -> Dict[str, Optional[str]]:
        duration_match = re.search(
            r"\b(?:for|since)\s+((?:\d+\s+)?(?:hour|hours|day|days|week|weeks|month|months|yesterday|today))\b",
            text
        )
        severity = None
        for term, value in SEVERITY_TERMS.items():
            if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text):
                severity = value
                break
        return {
            "duration": duration_match.group(1) if duration_match else None,
            "severity": severity,
            "emergency": any(
                re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text)
                for term in EMERGENCY_CHAT_TERMS
            )
        }

    @staticmethod
    def _contains_any(text: str, terms) -> bool:
        return any(
            re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text)
            for term in terms
        )
    
    def _auto_train_model(self):
        """Auto-train model if not found (first deployment)"""
        import subprocess
        import sys
        import os
        
        logger.info("🔄 Starting auto-training process...")
        
        try:
            # Generate dataset
            logger.info("Generating synthetic dataset...")
            result = subprocess.run(
                [sys.executable, "data/symptom_dataset.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                logger.error(f"Dataset generation failed: {result.stderr}")
                raise RuntimeError("Failed to generate dataset")
            
            # Train model
            logger.info("Training LightGBM model...")
            result = subprocess.run(
                [sys.executable, "train_symptom_model.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                logger.error(f"Model training failed: {result.stderr}")
                raise RuntimeError("Failed to train model")
            
            logger.info("✅ Auto-training completed successfully")
            
        except subprocess.TimeoutExpired:
            logger.error("Auto-training timed out")
            raise RuntimeError("Model training timed out")
        except Exception as e:
            logger.error(f"Auto-training failed: {e}")
            raise


# Global service instance
symptom_checker_service = SymptomCheckerService()
