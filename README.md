<div align="center">

# Maxime Gourguechon

### Data Scientist · Finance & Luxury Analytics

*Turning financial complexity and luxury market signals into predictive intelligence*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/maxime-gourguechon)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:maxime.gourguechon76@gmail.com)
[![Portfolio](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=github&logoColor=white)](https://maxime2476.github.io)

</div>

---

## About Me

Data Scientist with a dual specialization in **quantitative finance** and **luxury market analytics**. I build end-to-end pipelines — from raw market data ingestion to interpretable ML models — with a strong emphasis on statistical rigor, reproducible research, and production-ready deployment.

- **Finance track:** NLP on Fed communications, econometric panel models, portfolio optimization
- **Luxury track:** demand forecasting, pricing analytics, consumer sentiment modeling
- **Stack:** Python · R · SQL · PyTorch / TensorFlow · Qiskit · Streamlit · Docker

Currently exploring **quantum machine learning** for financial optimization and **LLM-augmented research workflows**.

---

## Tech Stack

**Languages**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![R](https://img.shields.io/badge/R-276DC3?style=flat-square&logo=r&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat-square&logo=postgresql&logoColor=white)
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=flat-square&logo=latex&logoColor=white)

**Machine Learning & Deep Learning**

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

**Data & Visualization**

![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

**Infrastructure & MLOps**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)

**Quantum Computing**

![Qiskit](https://img.shields.io/badge/Qiskit-6929C4?style=flat-square&logo=qiskit&logoColor=white)

---

## Featured Projects

| Project | Domain | Stack | Status |
|---|---|---|---|
| [**sentiment-powell-nlp**](https://github.com/maxime2476/sentiment-powell-nlp) | Fed communication analysis · NLP | Python · BERT · HuggingFace · TensorFlow | ![Active](https://img.shields.io/badge/status-active-brightgreen?style=flat-square) |
| [**panel-project**](https://github.com/maxime2476/panel-project) | EU GDP determinants · Econometrics | Stata · Python · Streamlit | ![Active](https://img.shields.io/badge/status-active-brightgreen?style=flat-square) |
| [**Quantum_Computing**](https://github.com/maxime2476/Quantum_Computing) | Quantum ML · Portfolio optimization | Python · Qiskit · PyTorch | ![WIP](https://img.shields.io/badge/status-WIP-yellow?style=flat-square) |
| [**academic-stress**](https://github.com/maxime2476/academic-stress) | Behavioral data analysis | Python · R · Statistics | ![Complete](https://img.shields.io/badge/status-complete-blue?style=flat-square) |
| [**linux-sys-monitor**](https://github.com/maxime2476/linux-sys-monitor) | System observability | Python · Linux · Shell | ![Complete](https://img.shields.io/badge/status-complete-blue?style=flat-square) |

---

## Spotlight: NLP on Fed Communications

> **Problem:** Quantify the hawkish/dovish stance of FOMC press conferences over time to anticipate monetary policy shifts.

**Approach:**
1. Transcript collection and preprocessing (tokenization, TF-IDF, stopword removal)
2. Fine-tuning a BERT model on financial sentiment corpora (Stanford Sentiment Treebank + custom labels)
3. Embedding layers (dim=100) → BiLSTM / Deep CNN → sentiment score per conference
4. Statistical validation: Wilcoxon signed-rank tests with Bonferroni correction
5. Time-series overlay with rate decision outcomes

**Key finding:** Dovish language clusters (identified via Bag-of-Words) show a statistically significant lead of 2–3 sessions before rate cuts (p < 0.01).

→ [View repository](https://github.com/maxime2476/sentiment-powell-nlp)

---

## GitHub Stats

<div align="center">

![Maxime's GitHub Stats](https://github-readme-stats.vercel.app/api?username=maxime2476&show_icons=true&theme=default&hide_border=true&count_private=true)

![Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username=maxime2476&layout=compact&theme=default&hide_border=true)

</div>

---

## Currently

- **Building:** Interactive Streamlit dashboard on top of `panel-project` econometric models
- **Learning:** Quantum kernel methods with Qiskit for near-term quantum devices (NISQ)
- **Reading:** *Advances in Financial Machine Learning* — Marcos López de Prado
- **Open to:** Research collaborations at the intersection of NLP, quantitative finance, and luxury market analytics

---

## Repository Standards

All my projects follow a reproducible research structure:

```
project/
├── README.md          # Executive summary, results, install guide
├── notebooks/         # Numbered EDA & modelling iterations
├── src/               # Production-grade, modular Python code
├── data/              # Anonymised samples only (.gitignore for raw data)
├── report/            # Final PDFs, high-res figures
├── dashboard/         # Streamlit / Dash app + Dockerfile
├── requirements.txt   # Pinned dependencies
└── LICENSE
```

---

<div align="center">

*"Data without context is noise. Context without data is opinion."*

</div>
