"""
Extracts features from a URL so a model can predict if it's phishing.

I use this same function both when training the model and inside the
API's /predict endpoint. That way the model always sees features
computed the exact same way, whether it's training or making a
live prediction.
"""

import math
import re
from urllib.parse import urlparse
from collections import Counter

# Common words phishing pages use to create urgency / trick users
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update",
    "confirm", "banking", "signin", "password", "urgent",
]

IP_PATTERN = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")


def get_entropy(text):
    # entropy = how "random" a string looks.
    # real domains (google.com) are low entropy, made-up ones
    # like xk29fpq.com are higher entropy since there's no pattern
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def extract_features(url):
    url = url.strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    host = parsed.hostname or ""

    features = {
        "url_length": len(url),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_special_chars": len(re.findall(r"[^a-zA-Z0-9./:-]", url)),
        "num_subdomains": max(host.count(".") - 1, 0) if host else 0,
        "has_ip_address": 1 if IP_PATTERN.match(host) else 0,
        "has_at_symbol": 1 if "@" in url else 0,
        "has_https": 1 if parsed.scheme == "https" else 0,
        "has_suspicious_keyword": 1 if any(k in url.lower() for k in SUSPICIOUS_KEYWORDS) else 0,
        "url_entropy": round(get_entropy(url), 3),
        "num_query_params": url.count("=") if "?" in url else 0,
    }

    return features


def feature_names():
    # just gives back the column names in order, used so training
    # and the live API always build feature vectors the same way
    return list(extract_features("http://example.com").keys())


def explain_top_signals(features, top_n=4):
    """
    Turns the raw feature numbers into short reasons a human can read,
    e.g. "Very long URL". Only includes signals that are actually
    true for this URL - nothing made up.
    """
    signals = []

    if features.get("has_ip_address"):
        signals.append("IP address used instead of domain name")
    if features.get("has_at_symbol"):
        signals.append("Contains '@' symbol")
    if not features.get("has_https"):
        signals.append("Not using HTTPS")
    if features.get("has_suspicious_keyword"):
        signals.append("Contains suspicious keyword")
    if features.get("num_subdomains", 0) >= 3:
        signals.append("Multiple subdomains")
    if features.get("url_length", 0) > 75:
        signals.append("Very long URL")
    if features.get("url_entropy", 0) > 4.0:
        signals.append("High randomness in URL")

    return signals[:top_n]


if __name__ == "__main__":
    # quick manual test - just run this file directly to check it works
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/paypal-login-verify-account",
        "https://secure-bank-update.xk29fpq.com/confirm@login",
    ]
    for u in test_urls:
        f = extract_features(u)
        print(u)
        print(" features:", f)
        print(" top_signals:", explain_top_signals(f))
        print()