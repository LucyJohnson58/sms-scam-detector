import pickle
import sys
from database import init_db, save_scan, save_report, get_stats

# ---------------------------------------------------------------
# 1. INITIALIZE DATABASE
# ---------------------------------------------------------------
init_db()

# ---------------------------------------------------------------
# 2. LOAD THE TRAINED MODEL
# ---------------------------------------------------------------
model_path = 'models/sms_scam_model.pkl'

try:
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully!\n")
except FileNotFoundError:
    print(f"ERROR: Could not find {model_path}")
    print("Please run train.py first to create the model.")
    sys.exit(1)

# ---------------------------------------------------------------
# 3. HELPER FUNCTION TO SCAN + SAVE
# ---------------------------------------------------------------
def scan_message(msg, source='terminal'):
    """Predict, save to DB, and return (prediction, confidence, scan_id)."""
    prediction = model.predict([msg])[0]
    proba = model.predict_proba([msg])[0]
    confidence = float(proba[prediction])

    scan_id = save_scan(msg, int(prediction), confidence, source)
    return prediction, confidence, proba, scan_id

# ---------------------------------------------------------------
# 4. RUN PRE-SET TEST MESSAGES
# ---------------------------------------------------------------
test_messages = [
    "MIRACLE MONEY: lowani mpingo wathu wa satanic kuti mulemele. imbani phone ku nambala iyi 0999994330 kuti mujoine",
    "JB FOUNDATION MTUKULA PAKHOMO PROJECT: mwachita mwayi olandila ndalama zokwana MK75000.00 kuti muthandize imbani 0981682601.",
    "You have won 1 million prize from Zilimwaife TNM. Call 09930223043 to collect",
    "I am a transporter, I have reached the border from South Africa. I am carrying your relative's package, call me for communication.",
    "MINISTRY OF HEALTH: Dear beneficiary, your number has been chosen to receive money for covid 19 worth MK105,000. Call us.",
    "Hey, are we still on for lunch at 12?",
    "Okondedwa akasitomala, mwatsala ndi MK-2199.20. Imbani *533# kuti mubwereke mayunitsi ndi KUTAPA.",
    "Dear customer, you have a balance of MK -2,199.20. Dial 533# to borrow airtime or data.",
    "ndanyamuka kale sindingabweleleso panopa",
    "Trans ID: CO221115.1429.I89181. You have sent MK 15000.00 to 123724. Your balance is MK 580.44",
    "Katema wa Polio akupelekedwabe kwa ana onse osakwana zaka 15.",
]

print("=" * 70)
print(f"{'PREDICTION':<12} {'CONFIDENCE':<12} MESSAGE")
print("=" * 70)

for msg in test_messages:
    prediction, confidence, _, _ = scan_message(msg, source='terminal')
    label = "FRAUD 🚨" if prediction == 1 else "NORMAL ✅"
    short_msg = msg[:60] + "..." if len(msg) > 60 else msg
    print(f"{label:<12} {confidence:.2%}      {short_msg}")

print("=" * 70)
print("\nPre-set test messages scanned and saved to DB.\n")

# ---------------------------------------------------------------
# 5. INTERACTIVE MODE
# ---------------------------------------------------------------
print("=" * 70)
print("INTERACTIVE MODE — type a message to test it")
print("Commands:")
print("  - Type any message to scan it")
print("  - Type 'report <scan_id> correct|wrong' to report feedback")
print("  - Type 'stats' to see database statistics")
print("  - Type 'quit' or 'exit' to stop")
print("=" * 70)

last_scan_id = None

while True:
    try:
        user_input = input("\nEnter message: ").strip()

        if user_input.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break

        if not user_input:
            print("(Empty input — please type something)")
            continue

        # --- stats command ---
        if user_input.lower() == 'stats':
            stats = get_stats()
            print("\n📊 Database stats:")
            for k, v in stats.items():
                print(f"   {k}: {v}")
            continue

        # --- report command ---
        if user_input.lower().startswith('report '):
            parts = user_input.split()
            if len(parts) < 3 or parts[2].lower() not in ('correct', 'wrong'):
                print("Usage: report <scan_id> correct|wrong")
                continue
            try:
                scan_id = int(parts[1])
                feedback = parts[2].lower()
                save_report(scan_id, feedback)
                print(f"✅ Report saved: scan #{scan_id} → {feedback}")
            except ValueError:
                print("Invalid scan_id. It must be a number.")
            continue

        # --- normal scan ---
        prediction, confidence, proba, scan_id = scan_message(user_input)
        last_scan_id = scan_id

        if prediction == 1:
            print(f"🚨 FRAUD (confidence: {confidence:.2%})  [scan id: {scan_id}]")
            print(f"   Probability of being normal: {proba[0]:.2%}")
        else:
            print(f"✅ NORMAL (confidence: {confidence:.2%})  [scan id: {scan_id}]")
            print(f"   Probability of being fraud: {proba[1]:.2%}")

    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")