# Prakriti AI – Smart Women's Health Assistant

> **College Project | Final Year / Capstone Engineering Project**  
> **Domain:** Full-Stack Web Development, Applied Machine Learning & Healthcare Informatics  
> **Color Aesthetic:** Modern Lavender, Sage Green, and Warm Cream

---

## 1. Project Overview & Motivation

Women's hormonal health, menstrual cycle dynamics, and conditions such as **PCOS (Polycystic Ovary Syndrome)** and **PCOD (Polycystic Ovarian Disease)** are frequently accompanied by stigma, fragmented tracking, and misinformation. Many women lack an integrated, private platform to monitor their menstrual trends, understand potential symptom patterns, analyze lifestyle stress, and prepare structured records for medical consultations.

**Prakriti AI** addresses this need by providing:
- **Menstrual Cycle Tracking & Pattern Modeling**: Historical logging paired with a machine learning model trained on 1,665 authentic clinical cycles to evaluate cycle regularity and statistical ovulation timing.
- **Evidence-Based PCOS/PCOD Symptom Awareness**: A non-diagnostic screening assessment grounded in the international **Rotterdam Consensus Criteria**, providing both endocrinological context and traditional Ayurvedic holistic perspectives (*Vata*, *Pitta*, *Kapha*).
- **Sleep & Lifestyle Health Analytics**: An applied multi-class machine learning pipeline predicting sleep disorder risk indicators (*None*, *Insomnia*, *Sleep Apnea*) from daily lifestyle metrics.
- **Personalized Metabolic Nutrition**: Hormone-supportive Indian recipes selected for high dietary fiber and low glycemic impact.
- **Physician Consultation Report Generator**: Formatted medical summaries and printable PDF/text exports designed for clinical consultations with gynecologists.

---

## 2. System Architecture & Tech Stack

```text
┌─────────────────────────────────────────────────────────────┐
│                       Client Browser                        │
│   (HTML5, Responsive CSS3, JavaScript, Chart.js Charts)     │
└──────────────────────────────▲──────────────────────────────┘
                               │ HTTP / REST / JSON
┌──────────────────────────────▼──────────────────────────────┐
│                    Flask Web Application                    │
│   (app.py - Auth, Session Management, Input Sanitization)    │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼──────────────┐ ┌──────────────▼──────────────┐
│       SQLite Database       │ │    ML Inference Service     │
│        (database.py)        │ │      (ml/inference.py)      │
│  - users                    │ │                             │
│  - cycle_logs               │ │  - cycle_model.joblib       │
│  - pcos_assessments         │ │  - sleep_model.joblib       │
│  - wellness_logs            │ │                             │
│  - consultation_requests    │ │                             │
└─────────────────────────────┘ └─────────────────────────────┘
```

- **Backend**: Python 3.14 / Flask 3.1
- **Database**: SQLite 3 with Foreign Key constraints (`PRAGMA foreign_keys = ON;`) and WAL mode
- **Machine Learning**: `scikit-learn 1.9`, `pandas 3.0`, `numpy 2.5`, `joblib 1.6`
- **Frontend**: Clean semantic HTML5, custom responsive CSS (Lavender `#8673B8`, Sage Green `#5A7D65`, Warm Cream `#FAF7F2`), and **Chart.js 4.4**
- **Security**: PBKDF2:SHA256 password hashing, HTTP-only SameSite session cookies, zero client-side sensitive health data in `localStorage`.

---

## 3. Project Directory Structure

```text
Prakriti AI/
├── index.html                           # Original client-side prototype (preserved untouched)
├── README.md                            # Comprehensive project documentation & viva guide
├── requirements.txt                     # Project dependencies
├── database.py                          # SQLite database schema, connections, and tables
├── prakriti.db                          # Application database file
├── app.py                               # Main Flask application and API routes
├── datasets/                            # Verified clinical and lifestyle datasets
│   ├── FedCycleData071012.csv           # Clinical Menstrual Cycle dataset (1,665 cycles)
│   ├── Sleep_health_and_lifestyle_dataset.csv # Sleep & Lifestyle dataset (374 individuals)
│   └── IndianFoodDatasetCSV.csv         # Nutrition and recipe dataset (6,000+ entries)
├── ml/
│   ├── inspect_data.py                  # Dataset quality & label validation script
│   ├── train_cycle_model.py             # Menstrual cycle regularity & ovulation pipeline
│   ├── train_sleep_model.py             # Multi-class sleep disorder training pipeline
│   ├── test_inference.py                # Standalone inference verification script
│   ├── inference.py                     # Backend model loading & prediction wrapper
│   ├── models/                          # Serialized trained model bundles
│   │   ├── cycle_model.joblib
│   │   └── sleep_model.joblib
│   └── reports/                         # Authentic evaluation reports
│       ├── cycle_model_report.json
│       ├── cycle_model_report.txt
│       ├── sleep_model_report.json
│       └── sleep_model_report.txt
├── static/
│   └── css/
│       └── style.css                    # Modern Lavender, Sage Green, and Cream stylesheet
├── templates/
│   ├── base.html                        # Master layout, navigation, and medical disclaimers
│   ├── home.html                        # Landing page and project overview
│   ├── awareness.html                   # Educational women's health & PCOS guide
│   ├── register.html                    # Secure user registration
│   ├── login.html                       # User authentication
│   ├── dashboard.html                   # Dashboard with interactive Chart.js charts
│   ├── cycle.html                       # Cycle tracker & ML regularity predictor
│   ├── assessment.html                  # PCOS non-diagnostic symptom evaluation
│   ├── wellness.html                    # Sleep analytics & hormone-balancing recipes
│   └── report.html                      # Printable / PDF doctor consultation summary
└── tests/
    ├── test_backend.py                  # Unit & API test suite (12 tests)
    └── test_user_journey.py             # End-to-end user workflow integration test
```

---

## 4. Authentic Datasets & ML Methodology

### Dataset 1: Menstrual Cycle Study (`FedCycleData071012.csv`)
* **Source**: Natural Family Planning clinical observational study.
* **Size**: 1,665 recorded cycles across 159 unique patients.
* **Features Used**: `Age`, `BMI`, `MeanCycleLength`, `LengthofMenses`, `MeanMensesLength`, `TotalMensesScore`.
* **Clinical Insight on Demographics**: Baseline client attributes (`Age`, `BMI`) were recorded during Cycle 1. By grouping records by `ClientID`, baseline demographic parameters were forward-filled across subsequent cycles for that patient, achieving 100% complete records without synthetic data creation.
* **Leakage Prevention**: Evaluated using **`GroupShuffleSplit`** grouped strictly by `ClientID` (80% train / 20% test). Cycles belonging to a test-set client are completely unseen during training.
* **Model Tasks**:
  1. **Cycle Regularity Classification**: Predicts whether a cycle is likely to be Regular (21–35 days per FIGO/ACOG standard) or Atypical/Irregular (<21 or >35 days). Random Forest with `class_weight='balanced'`.
  2. **Ovulation Timing Estimation**: Linear Ridge Regression estimating ovulation day based on cycle parameters.
* **Actual Evaluated Metrics (Test Set: 371 cycles, 32 clients)**:
  * Accuracy: **70.89%**
  * ROC-AUC: **0.7325**
  * Balanced Accuracy: **52.74%**
  * Ovulation Estimator MAE: **1.67 days** ($R^2 = 0.5845$)
  * Confusion Matrix `[[TN, FP], [FN, TP]]`: `[[4, 8], [100, 259]]`
* **Limitation & Disclosure**: The balanced accuracy on atypical cycles is modest (52.74%) due to real-world class imbalance (92.6% regular vs. 7.4% irregular). The system explicitly discloses this limitation in the UI and does **not** claim clinical diagnostic accuracy.

### Dataset 2: Sleep & Lifestyle Health (`Sleep_health_and_lifestyle_dataset.csv`)
* **Source**: Comprehensive sleep and lifestyle survey dataset.
* **Size**: 374 individuals (185 females, 189 males).
* **Target Label**: `Sleep Disorder` (`None`: 219 [58.6%], `Sleep Apnea`: 78 [20.9%], `Insomnia`: 77 [20.6%]).
* **Validation**: Stratified 80/20 train/test split preserving exact class ratios.
* **Actual Evaluated Metrics (Test Set: 75 individuals)**:
  * Overall Accuracy: **93.33%**
  * Balanced Accuracy: **89.31%**
  * Macro F1-Score: **0.8925**
  * Weighted F1-Score: **0.9333**
  * Confusion Matrix:
    * `Insomnia`: 13 correct, 2 predicted as Sleep Apnea
    * `None` (Healthy): 44 correct (100% precision and recall)
    * `Sleep Apnea`: 13 correct, 3 predicted as Insomnia

### PCOS/PCOD Symptom Stratification (Non-Diagnostic)
* **Grounded in Clinical Rotterdam Criteria**: Stratifies user symptom reports based on hallmark markers (menstrual irregularity, hyperandrogenic phenotypic traits like acne and hirsutism, and metabolic indicators like insulin-resistant acanthosis nigricans).
* **Dual Interpretation**: Delivers modern endocrinological symptom context alongside traditional Ayurvedic dosha qualities (*Vata* nervous/motion balance, *Pitta* metabolic heat, *Kapha* fluid/tissue stability).
* **Strict Non-Diagnostic Disclaimer**: The application explicitly emphasizes that PCOS cannot be diagnosed by an app—it requires serum blood hormone tests and pelvic ultrasonography.

---

## 5. Local Setup & Installation Instructions

### Prerequisites
* Windows 10/11, macOS, or Linux
* Python 3.10+ (Tested on Python 3.14.6)
* Git & PowerShell / Bash terminal

### Step-by-Step Run Commands

```powershell
# 1. Clone or open the project folder
cd "c:\Users\Shweta Ingole\OneDrive\Desktop\Prakriti AI"

# 2. Create and activate a Python virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# (If PowerShell script execution is restricted on your machine, run directly):
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Verify dataset quality and labels
.\.venv\Scripts\python.exe ml\inspect_data.py

# 4. Train the ML models (already pre-trained and saved in ml/models/)
.\.venv\Scripts\python.exe ml\train_cycle_model.py
.\.venv\Scripts\python.exe ml\train_sleep_model.py

# 5. Run automated tests to verify system integrity
.\.venv\Scripts\python.exe tests\test_backend.py
.\.venv\Scripts\python.exe tests\test_user_journey.py

# 6. Start the Flask application
.\.venv\Scripts\python.exe app.py
```

Open your browser to: **`http://127.0.0.1:5000`**

---

## 6. Demonstration & Examiner Viva Guide

When presenting Prakriti AI to your college evaluation panel, follow this demonstration workflow:

### A. Demonstration Flow
1. **Home & Awareness (`/`, `/awareness`)**:
   - Highlight the modern Lavender, Sage Green, and Cream UI.
   - Explain the educational mission and show the Rotterdam consensus criteria guide and Ayurvedic dosha principles.
2. **Account Creation & Login (`/register`, `/login`)**:
   - Show input validation (minimum 8 characters, email formatting, baseline BMI calculation).
   - Demonstrate that sensitive health data is protected behind server-side authentication.
3. **Cycle Tracking & ML Regularity Prediction (`/cycle`)**:
   - Enter a cycle length (e.g., 29 days) and bleeding details.
   - Show the real-time inference returning predicted regularity, confidence score, and estimated ovulation timing.
   - Point out the honest limitation disclosure (European NFP data, 52.7% balanced accuracy on irregular cycles).
4. **PCOS/PCOD Health Assessment (`/assessment`)**:
   - Check symptoms (acne, hair thinning, cycle irregularity).
   - Show the generated score, risk level badge, medical endocrinology explanation, and Ayurvedic wellness notes.
   - Emphasize the clear medical disclaimer stating the app does not diagnose PCOS.
5. **Sleep & Lifestyle Analytics (`/wellness`)**:
   - Submit sleep duration, stress levels, and blood pressure.
   - Observe the multi-class probability breakdown and view curated Indian recipes (*Methi Moong Dal*, *Bitter Gourd stir fry*).
6. **Dashboard & Visualization (`/dashboard`)**:
   - Show the interactive **Chart.js** line chart displaying cycle length variations against the clinical 21–35 day normal band, and the sleep/stress bar chart.
7. **Doctor Consultation & Report Generation (`/report/view`, `/report/download`)**:
   - Show the printable medical summary formatted with patient data, cycle logs, and screening scores.
   - Demonstrate the `.txt` download button.
8. **Logout & Authorization Check (`/logout`)**:
   - Log out and demonstrate that attempting to access `/dashboard` or `/cycle` automatically redirects to `/login`.

---

### B. Common Viva Questions & Model Answers

#### Q1: Why didn't you train a machine learning model to diagnose PCOS directly?
> **Answer:** *"Academic integrity and medical ethics are paramount. Neither of the verified public datasets on our system contained clinical PCOS diagnosis labels (which require pelvic ultrasound and hormone blood work). Rather than fabricating synthetic labels or claiming unverified diagnostic accuracy, we used an authentic clinical menstrual cycle dataset and an authentic sleep health dataset for real ML modeling. For PCOS, we implemented an evidence-based symptom-awareness screening aligned with the international Rotterdam criteria, paired with prominent disclaimers that only a certified gynecologist can diagnose PCOS."*

#### Q2: How did you prevent data leakage in your menstrual cycle model?
> **Answer:** *"The FedCycle dataset is longitudinal, containing multiple consecutive cycles from the same patient. Using a naive random split would place cycles from the same individual in both training and test sets, artificially inflating accuracy. We used `GroupShuffleSplit` grouped strictly by `ClientID`, ensuring that all cycles of any patient exist exclusively in either the training set or the test set."*

#### Q3: Why is the balanced accuracy on the cycle model 52.7%?
> **Answer:** *"The European NFP dataset exhibits significant real-world class imbalance: 92.6% of recorded cycles are regular (21–35 days), while only 7.4% are irregular. While overall accuracy is 70.89% and ROC-AUC is 0.7325, the balanced accuracy accurately reflects the challenge of predicting infrequent irregularities. We explicitly documented this limitation in our UI, project report, and code rather than hiding it."*

#### Q4: How is user health data secured?
> **Answer:** *"Passwords are hashed using salted PBKDF2:SHA256 via Werkzeug. User sessions are managed via secure, HTTP-only SameSite cookies. All health entries, cycle logs, and assessments are stored server-side in SQLite tables mapped to authenticated user IDs with foreign key constraints, avoiding vulnerable browser `localStorage` for sensitive medical information."*

---

## 7. Medical & Ethical Disclaimer

**Prakriti AI is an academic educational prototype developed for college project demonstration and health informatics exploration.** It does **not** provide a medical diagnosis for PCOS, PCOD, sleep apnea, or any medical condition. Ovulation estimates are statistical approximations and must never be utilized as a contraceptive technique. Users should always consult a licensed medical doctor, gynecologist, or healthcare professional for diagnostic assessments and medical treatment.

---

*Authored by Shweta Ingole | Final Year College Project | October 2026*
