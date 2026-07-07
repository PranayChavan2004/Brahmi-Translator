# Brahmi Script Recognition System

An AI-powered web application for ancient Brahmi script translation and inscription analysis. 
---

## Project Overview

Ancient Brahmi is one of the oldest writing systems in the world dating back to 3rd century BCE. These inscriptions are extremely difficult to interpret manually due to:

- Damaged and weathered stone surfaces
- Low quality inscription images
- Faded and incomplete characters
- Requirement of specialized expert knowledge
- Limited digitized datasets

This system provides three functional modules to solve these problems:

- **Module 1** — Devanagari text to Brahmi Unicode conversion
- **Module 2** — Brahmi Unicode text to Devanagari conversion
- **Module 3** — Brahmi inscription image to Devanagari conversion using CNN

---

## Modules

### Module 1 — Devanagari to Brahmi

Converts modern Devanagari text into corresponding Brahmi Unicode characters using a comprehensive character mapping dictionary.
- Accuracy: approximately 95%

![Devanagari to Brahmi](./screenshots/devtobrahmi.png)

---

### Module 2 — Brahmi to Devanagari

Reverse conversion from Brahmi Unicode characters to modern Devanagari text using an auto-inverted mapping dictionary.
- Accuracy: approximately 95%

![Brahmi to Devanagari](./screenshots/brahmitodev.png)

---

### Module 3 — Brahmi Image to Devanagari (Main Feature)

Analyzes uploaded Brahmi inscription images through a complete computer vision and deep learning pipeline to predict Brahmi characters and output Devanagari text.
**Accuracy: 80-85%**

![Brahmi Image to Devanagari](./screenshots/image.png)

---

## Accuracy Summary

| Module | Description | Method | Accuracy |
|--------|-------------|--------|----------|
| Module 1 | Devanagari to Brahmi | Dictionary Mapping | approximately 95% |
| Module 2 | Brahmi to Devanagari | Reverse Dictionary | approximately 95% |
| Module 3 | Brahmi Image to Devanagari | Custom CNN plus OpenCV | 80 to 85% |

---

## Tech Stack

### Backend
- Python 3.10
- Flask

### Machine Learning
- TensorFlow
- Keras
- Custom Sequential CNN stored in model.h5
- Input size 32x32 grayscale
- Output 287 Brahmi classes
- Total parameters 500267
- Model size 11 MB
- Trained on 60000 handwritten Brahmi character images

### Computer Vision
- OpenCV
- scikit-image
- PlantCV
- NumPy

### Frontend
- HTML5
- CSS3
- JavaScript
- Jinja2 Template Engine

---

## Project Structure

```
final_bramhi/
|
|-- app.py
|-- final.py
|
|-- templates/
|   |-- index.html
|
|-- static/
|   |-- style.css
|   |-- uploads/
|
|-- screenshots/
|   |-- home.png
|   |-- devtobrahmi.png
|   |-- brahmitodev.png
|   |-- image.png
|
|-- models/
    |-- MODEL/
        |-- model.h5
```



## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Virtual Environment

### Step 1 Clone Repository

```bash
git clone https://github.com/PranayChavan2004/brahmi-translation-system.git
cd brahmi-translation-system
```

### Step 2 Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux or Mac

```bash
python -m venv venv
source venv/bin/activate
```

### Step 3 Install Dependencies

```bash
pip install flask tensorflow opencv-python scikit-image plantcv numpy pillow
```

### Step 4 Run Application

```bash
python app.py
```

### Step 5 Open Browser

```
http://127.0.0.1:5000
```

---

## Full Project Download

Due to GitHub file size limitations the complete project including trained model and dataset is available on Google Drive.

[Google Drive - Full Brahmi Project](https://drive.google.com/drive/folders/1km2pnUuj3RqCbFDDajMgKNEPdfHN_vQm?usp=sharing)

---
