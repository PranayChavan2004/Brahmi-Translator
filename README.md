# Brahmi Script Recognition System

An Deep learning system designed for ancient Brahmi script translation and inscription analysis Project focused on cultural heritage digitization and intelligent inscription processing

---

## Project Overview

Ancient Brahmi inscriptions are difficult to interpret manually due to:
- Low-quality inscription images
- Limited digitized datasets

This system provides an end-to-end pipeline to:

- Recognize Brahmi characters from inscription images using CNN
- Translate between Brahmi Unicode and Devanagari script
- Perform OCR-based inscription analysis

---

## Application Home Page

![Home Page](./screenshots/home.png)

---

## Modules

### Module 1 — Devanagari to Brahmi Translation

Converts modern Devanagari text into corresponding Brahmi Unicode characters using a character mapping dictionary.

- Character-level mapping
- Covers vowels, consonants, matras, numbers, punctuation

![Devanagari to Brahmi](./screenshots/devtobrahmi.png)

---

### Module 2 — Brahmi to Devanagari Translation

Reverse conversion from Brahmi Unicode characters to Devanagari using an auto-inverted mapping dictionary.

- Reverse of Module 1 mapping
- Character-level conversion

![Brahmi to Devanagari](./screenshots/brahmitodev.png)

---

### Module 3 — Brahmi Image Recognition

Analyzes uploaded Brahmi inscription images and predicts the Brahmi characters and their Devanagari equivalents using a trained CNN model.

![Image Analysis](./screenshots/image.png)

---

## Accuracy

| Module | Accuracy |
|---|---|
| Devanagari to Brahmi | 100% (dictionary-based) |
| Brahmi to Devanagari | 100% (dictionary-based) |
| Image OCR (CNN) | 78-90% (varies by image quality) |

---

## Tech Stack

### Backend

- Python 3.10
- Flask

### Machine Learning and Computer Vision

- TensorFlow
- Keras
- OpenCV
- NumPy

### Frontend

- HTML5
- CSS3
- JavaScript

### Model

- Custom Sequential CNN
- Trained on 60,000 Brahmi character images

---

## Project Structure

```
final_bramhi/
|
|-- app.py                  # Flask application — routes and request handling
|-- final.py                # Complete OCR pipeline — run_ocr() function
|
|-- templates/
|   |-- index.html          # Main UI — forms and result display
|
|-- static/
|   |-- style.css           # Stylesheet
|
|-- screenshots/            # Project screenshots
|
|-- models/
    |-- MODEL/
        |-- model.h5        # Trained CNN model (287 classes)
```

---

## Dataset

- 60,000 Brahmi character images
- ~200 images per class
- 287 unique Brahmi syllable classes

---

## Full Project Download

The complete project including trained model and dataset is available on Google Drive.

[Google Drive - Full Brahmi Project](https://drive.google.com/drive/folders/1km2pnUuj3RqCbFDDajMgKNEPdfHN_vQm?usp=sharing)

---

## Installation and Setup

### Prerequisites

- Python 3.10+
- pip
- Virtual Environment

### Clone Repository

```bash
git clone https://github.com/PranayChavan2004/brahmi-translation-system.git
cd brahmi-translation-system
```

### Create Virtual Environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / Mac

```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

Application runs at:

```
http://127.0.0.1:5000
```

---

## Research Contribution

- OCR pipeline for ancient low-resource scripts
- End-to-end Brahmi inscription digitization
- Connected component based noise removal for historical images
- Skeletonization and pruning for character standardization
- Custom CNN trained on 60,000 Brahmi characters
