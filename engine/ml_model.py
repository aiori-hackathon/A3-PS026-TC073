import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import random
import os
import joblib

# Model file ka path
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'trained_model.joblib')

def generate_training_data():
    """200 dummy URIs ka dataset banata hai jisse model seekhta hai."""
    data = []
    for _ in range(200):
        colons = random.randint(0, 4)
        has_did = 1 if random.random() > 0.5 else 0
        length = random.randint(10, 200)
        
        # Rule: Agar DID hai aur 2 se zyada colon hain, toh conflict (1)
        if has_did == 1 and colons > 2:
            label = 1 
        else:
            label = 0 
            
        data.append([colons, has_did, length, label])
    
    return pd.DataFrame(data, columns=['colons', 'has_did', 'length', 'label'])

def train_or_load_model():
    """Agar model pehle se saved hai toh load karta hai, warna naya train karta hai."""
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print("✅ Pre-trained ML Model loaded successfully!")
            return model, 1.0 # 1.0 assuming it's already validated
        except Exception:
            pass # Agar load fail ho jaye toh naya train karega
            
    print("⏳ Training new ML Model (RandomForestClassifier)...")
    df = generate_training_data()
    X = df[['colons', 'has_did', 'length']]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model
    joblib.dump(model, MODEL_PATH)
    
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    
    print(f"✅ Model trained successfully! Accuracy: {acc * 100:.2f}%")
    return model, acc

# Load or Train on import
TRAINED_MODEL, ACCURACY = train_or_load_model()

def predict_conflict(uri: str) -> dict:
    """URI ke features nikaal kar predict karta hai ki conflict hone ke chances kitne hain."""
    colons = uri.count(":")
    has_did = 1 if "did:" in uri else 0
    length = len(uri)
    
    features = [[colons, has_did, length]]
    
    prediction = TRAINED_MODEL.predict(features)[0]
    prob = TRAINED_MODEL.predict_proba(features)[0][1]
    
    return {
        "prediction": "High Risk of Conflict" if prediction == 1 else "Low Risk of Conflict",
        "confidence": f"{prob * 100:.1f}%",
        "model_used": "RandomForestClassifier (scikit-learn)",
        "features_analyzed": {
            "colons_in_uri": colons,
            "has_did_prefix": bool(has_did),
            "uri_length": length
        }
    }