# CS156: Machine Learning for Science and Profit
 
Coursework repository for CS156 at Minerva University, Fall 2026, taught by Prof. Watson.
 
**Author:** Omar Ibrahim
 
## Structure
 
```
.
├── assignments/     # Graded assignment submissions, one folder per assignment
├── pcw/             # Pre-class work notebooks and notes
├── notebooks/       # In-class work and personal exploration
└── data/            # Small datasets used by the notebooks
```
 
Each assignment folder contains its own README describing the task, the approach I took, and any results.
 
## Course Learning Outcomes
 
This repository is the primary evidence for three outcomes:
 
| Tag | Outcome |
|---|---|
| `#MLCode` | Produce working, readable, and performant Python implementations of machine learning systems using appropriate libraries and tools. |
| `#MLExplanation` | Clearly articulate machine learning systems, algorithms, and techniques using oral and written descriptions, mathematical notation, and visualizations. |
| `#MLMath` | Evaluate problems and derive solutions in linear algebra, multivariate calculus, and Bayesian statistics. |
 
## Environment
 
Python 3.11. Core stack:
 
```
numpy
scipy
pandas
matplotlib
scikit-learn
jupyter
```
 
Setup:
 
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
 
## Conventions
 
- Notebooks are committed with outputs cleared unless a figure is part of the deliverable.
- Derivations live in markdown cells using LaTeX rather than in separate documents, so the math sits next to the code it supports.
- Each notebook opens with a short statement of the problem and closes with what I concluded.
