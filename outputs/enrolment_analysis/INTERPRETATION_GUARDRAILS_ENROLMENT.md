# Forensic Interpretation Guardrails: Enrolment Analysis

**Status**: ACTIVE
**Applicability**: All Enrolment Visualizations (Plots 01-14)
**Audit Level**: STRICT

---

## 1. Prohibited Interpretations

| Observation | **PROHIBITED Interpretation** ❌ | **CORRECT Interpretation** ✅ |
| :--- | :--- | :--- |
| **Low Vol. District** | "The district is failing to enroll people." | "The district may be saturated (adults already enrolled)." |
| **High Child Share** | "Adults are losing interest." | "System has shifted to birth-registry mode; adult stock is exhausted." |
| **High Volatility** | "Operations are chaotic/unstable." | "Operations are episodic (Camp Mode) rather than continuous (Center Mode)." |
| **Weekend Drop** | "Operators are lazy/inactive." | "Reliance on institutional venues (schools/anganwadis) dictates schedule." |
| **High Gini (Conc)** | "Inequitable access to centers." | "Strategic centralization for efficiency (hubs) vs dispersed low-yield centers." |

---

## 2. Common Misinterpretations of Administrative Data

### The "Saturation Fallacy"
* **Error**: Assuming low enrolment numbers imply poor performance.
* **Reality**: In a mature ID system (>95% coverage), low enrolment is a **success signal** (saturation). High enrolment is only expected in birth cohorts (0-5) or catch-up zones (North-East).

### The "Demand vs Supply" Confusion
* **Error**: Interpreting enrolment spikes as "demand surges."
* **Reality**: Enrolment is supply-constrained. Spikes usually strictly track **camp availability** or **administrative mandates** (e.g., school admission deadlines), not organic demand.

---

## 3. Forensic Scope & Limitations

### Data Blind Spots
1.  **Rejection Rate**: We only see *successful* generations. We do not see failed attempts. A "low volume" district might have high attempts but high biometric failure.
2.  **Update vs New**: While we separate Enrolment (New) from Updates, some "New" enrolments might be re-enrolments of people who lost IDs (duplicates), inflating coverage > 100%.
3.  **Census Lag**: We normalize using 2021 projections. Real-time migration (urbanization) is not captured, potentially overstating rural saturation.

### Methodological Constraints
*   **Infrastructure Proxy**: We use "Total Historical Enrolment" as a proxy for "Infrastructure Size." This assumes constant efficiency, which may vary.
*   **Volatility Metric**: Coefficient of Variation (CV) punishes small districts. A district with 0, 0, 10, 0 enrolments looks highly volatile but may just be "on demand."

---

## 4. Citation Requirements

Any downstream report citing these plots MUST include the following caveat:
> *"Analysis reflects successful Aadhaar generation volume and does not account for rejected packets, biometric failure rates, or pre-enrolment fluctuations. Saturation estimates are based on 2021 population projections."*
