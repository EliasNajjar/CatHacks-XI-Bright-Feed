import os
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

        self.mapping = {0: 'hate_speech', 1: 'offensive_language', 2: 'neither'}
        self.q_table = None
        self.vectorizer = None

    def load_data(self):
        url = 'https://raw.githubusercontent.com/EliasNajjar/CatHacks-Goated-Team-2.0/main/CathacksBackup/data/labeled_data.csv'
        df = pd.read_csv(url)
        df = df[['tweet', 'class']].dropna()
        return train_test_split(df['tweet'], df['class'], test_size=0.2, random_state=42)

    def vectorize(self, texts):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        return self.vectorizer.fit_transform(texts).toarray()

    def train(self):
        X_train_texts, X_test_texts, y_train, y_test = self.load_data()
        X_train = self.vectorize(X_train_texts)

        num_states = X_train.shape[0]
        num_actions = 3  # 3 classes
        self.q_table = np.zeros((num_states, num_actions))

        for ep in range(self.episodes):
            for i, state_vector in enumerate(X_train):
                state = i
                true_label = y_train.iloc[i]

                # Epsilon-greedy action
                if random.random() < self.epsilon:
                    action = random.randint(0, num_actions - 1)
                else:
                    action = np.argmax(self.q_table[state])

                reward = 1 if action == true_label else -1
                next_state = (i + 1) % num_states
                max_future_q = np.max(self.q_table[next_state])

                # Q-value update
                self.q_table[state, action] = self.q_table[state, action] + self.alpha * (
                    reward + self.gamma * max_future_q - self.q_table[state, action])

        print("✅ Q-learning training complete!")

    def predict(self, text: str):
        assert self.vectorizer is not None and self.q_table is not None, "Model not trained yet."

        vec = self.vectorizer.transform([text]).toarray()
        closest_idx = np.argmin(np.linalg.norm(vec - self.vectorizer.transform(self.vectorizer.get_feature_names_out()).toarray(), axis=1))
        action = np.argmax(self.q_table[closest_idx])

        return {
            "text": text,
            "predicted_class": self.mapping[action]
        }


if __name__ == "__main__":
    clf = QLearningTextClassifier()
    clf.train()

    print("\n🤖 Type something to classify (Q-learning). Type 'exit' to quit:")
    while True:
        user_input = input(">> ").strip()
        if user_input.lower() in ['exit', 'quit']:
            break

        result = clf.predict(user_input)
        print(f"\n📊 Predicted class: {result['predicted_class']}\n")
