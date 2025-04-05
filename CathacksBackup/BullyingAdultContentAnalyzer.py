import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Load the trained Q-learning model and vectorizer from file
def load_q_learning_model(filepath="q_learning_model.pkl"):
    with open(filepath, "rb") as f:
        model = pickle.load(f)
    return model["q_table"], model["vectorizer"]

# Class label mapping (for readability in output)
mapping = {
    0: 'strongly inappropriate',
    1: 'possibly offensive',
    2: 'neutral'
}

# Make a prediction using the Q-table and vectorizer
def q_predict(text, q_table, vectorizer, threshold=0.2):
    # Vectorize the input text
    vec = vectorizer.transform([text]).toarray()

    # Compare input to existing vocabulary to find closest vector
    train_vectors = vectorizer.transform(vectorizer.get_feature_names_out()).toarray()
    closest_idx = np.argmin(np.linalg.norm(vec - train_vectors, axis=1))

    # Retrieve Q-values for this closest state
    q_values = q_table[closest_idx]

    # Calculate confidence margin between top and second-best prediction
    confidence_margin = np.max(q_values) - np.partition(q_values, -2)[-2]

    # Apply threshold logic: if confidence too low, default to 'neutral'
    if confidence_margin < threshold:
        action = 2  # neutral
        confidence = "low"
    else:
        action = np.argmax(q_values)
        confidence = "high"

    # Return detailed prediction info
    return {
        "text": text,
        "top_class": mapping[action],
        "confidence": confidence,
        "margin": confidence_margin,
        "q_values": {mapping[i]: float(q) for i, q in enumerate(q_values)}
    }

# Console-based user interface
if __name__ == "__main__":
    # Check for saved model
    if not os.path.exists("q_learning_model.pkl"):
        print("⚠️ Trained model not found. Please train the model first.")
        exit()

    # Load trained Q-table and vectorizer
    q_table, vectorizer = load_q_learning_model()

    print("\n🤖 Type something to classify or enter a file path (.txt). Type 'exit' to quit:")

    while True:
        user_input = input(">> ").strip()

        # Exit condition
        if user_input.lower() in ['exit', 'quit']:
            break

        # If input is a path to a .txt file, read and classify its contents
        if os.path.isfile(user_input) and user_input.lower().endswith(".txt"):
            with open(user_input, "r", encoding="utf-8") as f:
                content = f.read()
            result = q_predict(content, q_table, vectorizer)
        else:
            # Otherwise, treat the input as text
            result = q_predict(user_input, q_table, vectorizer)

        # Show prediction and confidence information
        print(f"\n📊 Prediction: {result['top_class']} (Confidence: {result['confidence']} | Margin: {result['margin']:.4f})")

        # Show Q-values for all classes for transparency
        for cls, val in result["q_values"].items():
            print(f"  - {cls}: {val:.4f}")

        print("\n---")
