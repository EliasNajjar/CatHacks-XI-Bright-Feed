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


def train_and_save_model():
    print("🔁 Downloading and training...")
    url = 'https://raw.githubusercontent.com/Hironsan/HateSonar/master/data/labeled_data.csv'
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


if __name__ == "__main__":
    if not os.path.exists("data/model.joblib"):
        train_and_save_model()

    clf = TextClassifier()

    print("\n🤖 Type something to classify (or type 'exit' to quit):")
    while True:
        user_input = input(">> ")
        if user_input.lower() in ['exit', 'quit']:
            break

        result = clf.predict(user_input)
        weights = clf.get_weights(user_input)

        print(f"\n📊 Prediction: {result['top_class']}")
        for cls in result['classes']:
            print(f"  - {cls['class_name']}: {cls['confidence']:.4f}")

        print("\n🧠 Word weights (influence):")
        for word, weight in weights.items():
            print(f"  {word}: {weight:.4f}")
        print("\n---")
