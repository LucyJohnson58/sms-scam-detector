import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import os

# ---------------------------------------------------------------
# 1. LOAD MULTIPLE SHEETS FROM THE EXCEL FILE
# ---------------------------------------------------------------
file_path = 'data/SMS_Fraud_Chichewa_Dataset_SM.xlsx'

# These sheets have both fraud and normal messages
data_sheets = ['D_CHI', 'D_HT', 'D_MT']

# These sheets are all normal (real telco messages) — great for balance
telco_sheets = ['telcoSMS_CHI', 'telcoSMS_HT', 'telcoSMS_MT']

frames = []

# Load the mixed-label sheets
for sheet in data_sheets:
    df = pd.read_excel(file_path, sheet_name=sheet)
    df = df[['Text', 'Label']].dropna()
    df['source'] = sheet
    frames.append(df)
    print(f"Loaded {sheet}: {len(df)} rows")

# Load the telco sheets (all normal)
for sheet in telco_sheets:
    df = pd.read_excel(file_path, sheet_name=sheet)
    df = df[['Text', 'Label']].dropna()
    df['source'] = sheet
    frames.append(df)
    print(f"Loaded {sheet}: {len(df)} rows")

# Combine everything into one DataFrame
data = pd.concat(frames, ignore_index=True)

print("-" * 50)
print(f"Total rows: {len(data)}")
print("Label distribution:")
print(data['Label'].value_counts())
print("-" * 50)

# ---------------------------------------------------------------
# 2. CLEAN AND PREPARE
# ---------------------------------------------------------------
# Remove duplicates (same text appearing in multiple sheets)
data = data.drop_duplicates(subset=['Text'])
print(f"After removing duplicates: {len(data)} rows")

# Convert labels to numbers: fraud = 1, normal = 0
data['label_num'] = data['Label'].map({'fraud': 1, 'normal': 0})

# Drop any rows where label was something unexpected
data = data.dropna(subset=['label_num'])
data['label_num'] = data['label_num'].astype(int)

print("Final label distribution:")
print(data['label_num'].value_counts())
print("-" * 50)

# ---------------------------------------------------------------
# 3. SPLIT INTO TRAIN AND TEST
# ---------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    data['Text'],
    data['label_num'],
    test_size=0.2,
    random_state=42,
    stratify=data['label_num']
)

# ---------------------------------------------------------------
# 4. BUILD THE PIPELINE
# ---------------------------------------------------------------
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),   # unigrams + bigrams
        max_features=15000,
        sublinear_tf=True
    )),
    ('nb', MultinomialNB(alpha=0.3))
])

# ---------------------------------------------------------------
# 5. TRAIN
# ---------------------------------------------------------------
print("Training the model...")
model_pipeline.fit(X_train, y_train)
print("Training complete!")
print("-" * 50)

# ---------------------------------------------------------------
# 6. EVALUATE
# ---------------------------------------------------------------
predictions = model_pipeline.predict(X_test)
print("Model Evaluation on Test Data:")
print(classification_report(
    y_test, predictions,
    target_names=['normal (0)', 'fraud (1)']
))
print("Confusion Matrix:")
print(confusion_matrix(y_test, predictions))
print("-" * 50)

# ---------------------------------------------------------------
# 7. SAVE THE MODEL
# ---------------------------------------------------------------
os.makedirs('models', exist_ok=True)
model_filename = 'models/sms_scam_model.pkl'
with open(model_filename, 'wb') as file:
    pickle.dump(model_pipeline, file)

print(f"Model saved to {model_filename}")