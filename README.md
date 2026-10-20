# 🛡️ SMS Scam Detector

An end-to-end machine learning system that detects fraudulent SMS messages in **Chichewa and English**, built with supervised learning.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.143-green)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

##  Overview

Scam SMS messages are a growing problem in Malawi and across Africa. This project trains a **Multinomial Naive Bayes** classifier on the [SMS Fraud Chichewa Dataset](https://github.com/) to automatically classify incoming messages as either:

- **`fraud`** — scam / phishing attempts
- **`normal`** — legitimate messages (including telco notifications)

The system includes a **web application** where users can paste suspicious SMS messages and get instant predictions with confidence scores.

---

## ✨ Features

-  **Multilingual classification** — handles Chichewa, English, and mixed-language messages
-  **Real-time predictions** — FastAPI backend with sub-100ms response times
-  **Confidence scores** — shows the probability of fraud vs. normal
-  **SQLite logging** — every scan is saved for auditing and future retraining
-  **User feedback** — users can report false positives/negatives
-  **Clean web UI** — HTML/CSS/JavaScript dashboard with live stats
-  **Auto-generated API docs** — Swagger UI at `/docs`

---


