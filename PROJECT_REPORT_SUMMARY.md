# Project Report Summary & Viva Voce Guide
## Prakriti AI – Smart Women's Health Assistant

**Student Name:** Shweta Ingole  
**Degree / Program:** Bachelor of Engineering / Technology (Computer Engineering / Information Technology / AI & Data Science)  
**Project Title:** Prakriti AI – Smart Women's Health Assistant  
**Date of Evaluation:** October 2026  

---

### 1. Abstract
Hormonal imbalances, menstrual irregularities, and conditions such as Polycystic Ovary Syndrome (PCOS) and Polycystic Ovarian Disease (PCOD) affect millions of women globally. However, women often experience delayed clinical diagnoses due to social stigma, lack of symptom awareness, and fragmented tracking tools. 

**Prakriti AI** is a modern, responsive full-stack web platform built using Python (Flask), SQLite, and scikit-learn. The system integrates machine learning models trained on authentic clinical and lifestyle datasets to predict menstrual cycle regularity, estimate statistical ovulation timing, and classify lifestyle-related sleep disorder risks. For PCOS/PCOD, the application provides an evidence-based, non-diagnostic symptom stratification engine grounded in the international Rotterdam Consensus Criteria, accompanied by traditional Ayurvedic holistic wellness perspectives (*Vata*, *Pitta*, *Kapha*) and hormone-balancing nutritional guidance.

---

### 2. Key Objectives & Scope
1. **Clinical Menstrual Tracking**: Provide structured recording of cycle dates, bleeding duration, flow intensity, and cramp levels.
2. **Applied Machine Learning**:
   - Model 1: Menstrual Cycle Regularity & Ovulation Timing (trained on 1,665 clinical cycles from the European Natural Family Planning cohort).
   - Model 2: Sleep Quality & Lifestyle Disorder Classifier (trained on 374 surveyed individuals).
3. **PCOS/PCOD Health Assessment**: Provide non-diagnostic symptom awareness and risk stratification (Lower, Moderate, Higher symptom-based risk) without fabricating unverified clinical diagnoses.
4. **Holistic Lifestyle & Nutrition Integration**: Offer Ayurvedic dosha correlations and curated Indian recipes designed for low glycemic load and insulin sensitivity.
5. **Secure Full-Stack Architecture**: Implement server-side authentication, salted password hashing, relational database storage, and downloadable clinical summary reports.

---

### 3. Database Schema Overview (`prakriti.db`)

| Table Name | Primary Purpose | Key Fields |
| :--- | :--- | :--- |
| `users` | Account credentials & physical baseline | `id`, `name`, `email`, `password_hash`, `age`, `height_cm`, `weight_kg`, `bmi`, `created_at` |
| `cycle_logs` | Menstrual cycle tracking records | `id`, `user_id` (FK), `start_date`, `end_date`, `cycle_length`, `menses_length`, `pain_level`, `flow_intensity`, `predicted_regularity`, `predicted_ovulation_day` |
| `pcos_assessments` | Symptom assessment history | `id`, `user_id` (FK), `age`, `cycle_length`, `primary_concern`, `symptoms_list`, `screening_score`, `risk_level`, `medical_assessment`, `ayurvedic_perspective` |
| `wellness_logs` | Daily lifestyle & sleep records | `id`, `user_id` (FK), `sleep_duration`, `quality_of_sleep`, `stress_level`, `activity_minutes`, `daily_steps`, `systolic_bp`, `diastolic_bp`, `predicted_disorder` |
| `consultation_requests`| Doctor appointment requests | `id`, `user_id` (FK), `doctor_name`, `specialty`, `preferred_date`, `notes`, `status` |

---

### 4. Machine Learning Methodology & Evaluation

#### Model 1: Menstrual Regularity & Ovulation Model
- **Data Source**: `FedCycleData071012.csv` (1,665 cycles across 159 clinical patients).
- **Leakage Prevention**: Group-based splitting using `GroupShuffleSplit` on `ClientID` (80% train / 20% test). Unseen patients in test set.
- **Classification Pipeline**: `SimpleImputer` (median) $\rightarrow$ `StandardScaler` $\rightarrow$ `RandomForestClassifier` with balanced class weights.
- **Regression Pipeline**: `SimpleImputer` $\rightarrow$ `StandardScaler` $\rightarrow$ `Ridge` regression.
- **Performance**:
  - Regularity Accuracy: **70.89%**
  - ROC-AUC: **0.7325**
  - Balanced Accuracy: **52.74%**
  * Ovulation Estimator MAE: **1.67 days** ($R^2 = 0.5845$)
- **Honest Limitation**: The modest balanced accuracy (52.74%) reflects real-world clinical imbalance where 92.6% of cycles were regular and only 7.4% were irregular. The system openly communicates this limitation.

#### Model 2: Sleep & Lifestyle Disorder Risk Model
- **Data Source**: `Sleep_health_and_lifestyle_dataset.csv` (374 individuals).
- **Target**: Multi-class `Sleep Disorder` (`None`, `Insomnia`, `Sleep Apnea`).
- **Validation**: Stratified 80/20 train/test split.
- **Pipeline**: ColumnTransformer (`StandardScaler` on numericals, `OneHotEncoder` on categoricals) $\rightarrow$ `RandomForestClassifier` with balanced class weights.
- **Performance**:
  - Overall Accuracy: **93.33%**
  - Balanced Accuracy: **89.31%**
  - Macro F1-Score: **0.8925**

---

### 5. Automated Test Matrix

| Test Module | Test Method | Tested Functionality | Result |
| :--- | :--- | :--- | :--- |
| `test_backend.py` | `test_user_registration_success` | User creation, PBKDF2 hashing, BMI calculation | **PASS** |
| `test_backend.py` | `test_registration_duplicate_email` | Rejection of existing emails | **PASS** |
| `test_backend.py` | `test_registration_invalid_inputs` | Password length (<8) & email regex validation | **PASS** |
| `test_backend.py` | `test_login_and_logout` | Password checking and session destruction | **PASS** |
| `test_backend.py` | `test_protected_routes_redirect_unauth`| 302 redirect on unauthenticated page access | **PASS** |
| `test_backend.py` | `test_cycle_ml_inference` | Cycle pipeline prediction & disclaimer formatting | **PASS** |
| `test_backend.py` | `test_sleep_ml_inference` | Multi-class sleep disorder classification | **PASS** |
| `test_backend.py` | `test_pcos_symptom_stratification` | High-risk and low-risk symptom scoring | **PASS** |
| `test_backend.py` | `test_api_cycle_logging` | Cycle record insertion and ML execution | **PASS** |
| `test_backend.py` | `test_api_cycle_invalid_bounds` | Rejection of negative / out-of-bound inputs | **PASS** |
| `test_backend.py` | `test_api_assessment_evaluate_and_save` | Assessment evaluation & database logging | **PASS** |
| `test_backend.py` | `test_report_download_generates_valid_text` | Downloadable text summary with disclaimers | **PASS** |
| `test_user_journey.py`| `test_complete_user_journey` | 9-step full end-to-end user workflow | **PASS** |

---

### 6. Viva Voce Q&A Cheat Sheet

**Q1: What is the main innovation in Prakriti AI compared to basic period trackers?**  
*Answer:* Standard apps merely record dates on a calendar without context. Prakriti AI brings together predictive machine learning (cycle regularity and sleep disorder classification), multi-factor clinical symptom stratification grounded in the Rotterdam criteria, traditional Ayurvedic dosha correlations, metabolic Indian recipes, and formatted clinical summaries designed to aid gynecologists during consultations.

**Q2: What is the Rotterdam Consensus Criteria for PCOS?**  
*Answer:* Established in 2003 by the European Society of Human Reproduction and Embryology (ESHRE) and the American Society for Reproductive Medicine (ASRM), it requires at least 2 of the following 3 features (after excluding other etiologies):
1. Oligo- or anovulation (infrequent or absent menstrual cycles).
2. Clinical and/or biochemical signs of hyperandrogenism (excess androgens, acne, hirsutism).
3. Polycystic ovaries visualized via pelvic ultrasound.

**Q3: Why did you not use synthetic oversampling techniques like SMOTE on the menstrual cycle dataset?**  
*Answer:* In clinical longitudinal healthcare data, generating synthetic records using interpolation algorithms can introduce artificial physiological artifacts that do not correspond to authentic human biology. Instead, we addressed class imbalance naturally using algorithmic class weighting (`class_weight='balanced'`) in Random Forest, penalizing misclassifications on minority classes proportionally.

**Q4: How does the application prevent sensitive health data exposure?**  
*Answer:* In our initial prototype, health data was saved in the browser's insecure `localStorage`. In our final full-stack implementation, all health logs and assessment histories are stored in an encrypted SQLite database on the server. Sessions are authenticated using signed HTTP-only, SameSite cookies. Passwords are never stored in plain text; they are hashed using salted PBKDF2:SHA256.

**Q5: How does Prakriti AI ensure it does not cross into unlicensed medical practice?**  
*Answer:* The application incorporates explicit, non-bypassable educational disclaimers across all pages, API endpoints, and report outputs. It explicitly states that it is an academic health awareness tool, does not claim to diagnose PCOS or any medical disorder, and instructs users to consult qualified physicians for definitive diagnostic tests.
