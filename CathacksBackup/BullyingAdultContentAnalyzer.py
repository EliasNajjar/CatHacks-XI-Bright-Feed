import os
import joblib
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


class TextClassifier:
    def __init__(self):
        base_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.model_path = os.path.join(base_dir, 'model.joblib')
        self.vec_path = os.path.join(base_dir, 'preprocess.joblib')

        self.estimator = joblib.load(self.model_path)
        self.preprocessor = joblib.load(self.vec_path)
        self.mapping = {0: 'hate_speech', 1: 'offensive_language', 2: 'neither'}

    def predict(self, text: str) -> dict:
        assert isinstance(text, str), "Input must be a string."

        vector = self.preprocessor.transform([text])
        proba = self.estimator.predict_proba(vector)[0]

        return {
            'text': text,
            'top_class': self.mapping[np.argmax(proba)],
            'classes': [
                {'class_name': self.mapping[i], 'confidence': float(proba[i])}
                for i in range(len(proba))
            ]
        }

    def get_weights(self, text: str) -> dict:
        class_idx = np.argmax(self.estimator.predict_proba(self.preprocessor.transform([text]))[0])
        features = self.preprocessor.get_feature_names_out()
        weights = self.estimator.coef_[class_idx]
        word2weight = dict(zip(features, weights))
        analyzer = self.preprocessor.build_analyzer()
        tokens = analyzer(text)

        return {token: word2weight.get(token, 0.0) for token in tokens}

    def predict_large_text(self, file_path: str) -> None:
        """Read and classify an entire text file without chunking."""
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='ISO-8859-1') as file:
                    text = file.read()
        except Exception as e:
            print(f"Error reading the file: {e}")
            return

        print(f"\n✅ File read successfully. Text length: {len(text)} characters.\n")

        result = self.predict(text)
        weights = self.get_weights(text)

        print(f"📊 Prediction: {result['top_class']}")
        for cls in result['classes']:
            print(f"  - {cls['class_name']}: {cls['confidence']:.4f}")

def train_and_save_model():
    print("🔁 Downloading and training...")
    url = 'https://raw.githubusercontent.com/EliasNajjar/CatHacks-Goated-Team-2.0/main/CathacksBackup/data/labeled_data.csv'
    df = pd.read_csv(url)
    df = df[['tweet', 'class']].dropna()

    texts = df['tweet'].astype(str).tolist()
    labels = df['class'].tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X_train_vec, y_train)

    os.makedirs("data", exist_ok=True)
    joblib.dump(classifier, "data/model.joblib")
    joblib.dump(vectorizer, "data/preprocess.joblib")
    print("✅ Model and vectorizer saved to ./data")

#Console implementation below

# if __name__ == "__main__":
#     if not os.path.exists("data/model.joblib"):
#         train_and_save_model()

#     clf = TextClassifier()

#     print("\n🤖 Type something to classify or enter a file path (.txt). Type 'exit' to quit:")
#     while True:
#         user_input = input(">> ").strip()
#         if user_input.lower() in ['exit', 'quit']:
#             break

#         if os.path.isfile(user_input):
#             clf.predict_large_text(user_input)
#         else:
#             result = clf.predict(user_input)
#             weights = clf.get_weights(user_input)

#             print(f"\n📊 Prediction: {result['top_class']}")
#             for cls in result['classes']:
#                 print(f"  - {cls['class_name']}: {cls['confidence']:.4f}")

#             print("\n🧠 Word weights (influence):")
#             for word, weight in weights.items():
#                 print(f"  {word}: {weight:.4f}")
#             print("\n---")
