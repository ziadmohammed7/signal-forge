"""
AI-Based Handover Prediction using logistic regression.
"""
import numpy as np


class HandoverPredictor:
    """
    Simple rule-based + logistic regression handover predictor.
    Features: SINR, SINR_delta, distance_to_serving, distance_to_best
    """

    def __init__(self):
        self._weights = np.array([-0.15, -0.25, 0.008, -0.006])
        self._bias = 0.5
        self._trained = False
        self._history_X = []
        self._history_y = []

    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-np.clip(z, -100, 100)))

    def predict_probability(self, sinr_serving: float, sinr_best: float,
                             dist_serving: float, dist_best: float) -> float:
        """Predict probability of handover."""
        features = np.array([sinr_serving, sinr_serving - sinr_best,
                              dist_serving, dist_best])
        z = np.dot(features, self._weights) + self._bias
        return float(self._sigmoid(z))

    def predict(self, sinr_serving: float, sinr_best: float,
                 dist_serving: float, dist_best: float, threshold: float = 0.5) -> bool:
        """Return True if handover predicted."""
        prob = self.predict_probability(sinr_serving, sinr_best, dist_serving, dist_best)
        return prob >= threshold

    def record_sample(self, sinr_serving: float, sinr_best: float,
                       dist_serving: float, dist_best: float, handover_occurred: bool):
        """Record training sample."""
        self._history_X.append([sinr_serving, sinr_serving - sinr_best,
                                  dist_serving, dist_best])
        self._history_y.append(int(handover_occurred))

    def train(self):
        """Train logistic regression on recorded samples."""
        if len(self._history_X) < 10:
            return False
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
            X = np.array(self._history_X)
            y = np.array(self._history_y)
            if len(np.unique(y)) < 2:
                return False
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            clf = LogisticRegression(max_iter=200)
            clf.fit(X_scaled, y)
            self._weights = clf.coef_[0]
            self._bias = clf.intercept_[0]
            self._trained = True
            return True
        except Exception:
            return False

    @property
    def is_trained(self):
        return self._trained

    def get_feature_importance(self):
        labels = ["SINR Serving", "SINR Delta", "Dist Serving", "Dist Best"]
        return list(zip(labels, np.abs(self._weights)))
