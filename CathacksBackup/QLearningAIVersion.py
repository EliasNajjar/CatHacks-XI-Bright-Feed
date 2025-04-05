import os
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import random

class QLearningTextClassifier:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, episodes=500):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.episodes = episodes

        # Less aggressive class names
        self.mapping = {0: 'strongly inappropriate', 1: 'possibly offensive', 2: 'neutral'}
        self.q_table = None
        self.vectorizer = None

    def model_exists(self, filepath="q_learning_model.pkl"):
        return os.path.exists(filepath)

    def load_model(self, filepath="q_learning_model.pkl"):
        with open(filepath, "rb") as f:
            model = pickle.load(f)
            self.q_table = model["q_table"]
            self.vectorizer = model["vectorizer"]
        print("📂 Trained model loaded from file.")

    def save_model(self, filepath="q_learning_model.pkl"):
        with open(filepath, "wb") as f:
            pickle.dump({
                "q_table": self.q_table,
                "vectorizer": self.vectorizer
            }, f)
        print("💾 Trained model saved to 'q_learning_model.pkl'")

    def load_data(self):
        df = pd.read_csv("C:/Users/ebrya/OneDrive/Documents/GitHub/CatHacks-Goated-Team-2.0/CathacksBackup/data/labeled_data.csv")
        print(f"✅ Dataset loaded: {df.shape[0]} rows")

        df = df[['tweet', 'class']].dropna()
        return train_test_split(df['tweet'], df['class'], test_size=0.2, random_state=42)

    def vectorize(self, texts):
        self.vectorizer = TfidfVectorizer(max_features=80, ngram_range=(1, 2), stop_words='english')
        return self.vectorizer.fit_transform(texts).toarray()

    def train(self):
        print("🔀 Splitting data into training and test sets...")
        X_train_texts, X_test_texts, y_train, y_test = self.load_data()
        X_train = self.vectorize(X_train_texts)

        num_states = X_train.shape[0]
        num_actions = 3
        self.q_table = np.zeros((num_states, num_actions))

        print(f"🧠 Starting Q-learning training for {self.episodes} episodes on {num_states} samples...")
    
        for ep in range(self.episodes):
            for i, state_vector in enumerate(X_train):
                state = i
                true_label = y_train.iloc[i]

                if random.random() < self.epsilon:
                    action = random.randint(0, num_actions - 1)
                else:
                    action = np.argmax(self.q_table[state])

                # Softer reward system
                if action == true_label:
                    reward = 1
                elif (action == 0 and true_label == 1) or (action == 1 and true_label == 0):
                    reward = -0.5
                else:
                    reward = -0.2

                next_state = (i + 1) % num_states
                max_future_q = np.max(self.q_table[next_state])

                self.q_table[state, action] += self.alpha * (
                    reward + self.gamma * max_future_q - self.q_table[state, action]
                )

            if ep % 50 == 0 or ep == self.episodes - 1:
                print(f"  ➤ Episode {ep + 1}/{self.episodes} completed.")

        print("✅ Q-learning training complete!")
        self.save_model()

    def predict(self, text: str):
        assert self.vectorizer is not None and self.q_table is not None, "Model not trained yet."

        vec = self.vectorizer.transform([text]).toarray()
        train_vectors = self.vectorizer.transform(self.vectorizer.get_feature_names_out()).toarray()
        closest_idx = np.argmin(np.linalg.norm(vec - train_vectors, axis=1))

        q_values = self.q_table[closest_idx]
        confidence_margin = np.max(q_values) - np.partition(q_values, -2)[-2]

        if confidence_margin < 0.2:
            action = 2  # neutral
            confidence_level = "low"
        else:
            action = np.argmax(q_values)
            confidence_level = "high"

        return {
            "text": text,
            "predicted_class": self.mapping[action],
            "confidence": confidence_level
        }

if __name__ == "__main__":
    clf = QLearningTextClassifier()

    if clf.model_exists():
        clf.load_model()
    else:
        clf.train()

    print("\n🤖 Type something to classify (Q-learning). Type 'exit' to quit:")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break

        result = clf.predict(user_input)
        print(f"\n📊 Predicted class: {result['predicted_class']} (Confidence: {result['confidence']})\n")
