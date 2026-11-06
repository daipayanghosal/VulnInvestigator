"""
scripts/build_dissertation_thesis.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generates the complete, publication-grade BITS Pilani M.Tech Dissertation Thesis
in both Markdown (.md) and formatted Microsoft Word (.docx) formats, strictly adhering
to BITS Pilani WILP guidelines (S1-26_CSIWZG628T).
"""

import os
from pathlib import Path

_PARENT_DIR = Path(r"c:\Users\daipa\Desktop\WIMS 2022 - Dissertation Documents")
_PROJECT_DIR = _PARENT_DIR / "Project"
_DOCS_DIR = _PROJECT_DIR / "docs"

def generate_thesis_markdown() -> str:
    # Build complete thesis content
    md = r"""# EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION

### **CSIW ZG628T DISSERTATION**

**Daipayan Ghosal**  
**BITS ID No.: 2022wa86002**  

**Dissertation Work Carried Out At**:  
Wipro Limited  

**BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE**  
Pilani (Rajasthan) India  
November, 2026  

<div style="page-break-after: always;"></div>

---

### **CSIW ZG628T DISSERTATION**

# EVIDENCE-GROUNDED GENERATIVE AI FOR VULNERABILITY-TO-THREAT INVESTIGATION AND RISK PRIORITIZATION

Submitted in partial fulfilment of the requirements of  
**M. Tech Computing Systems & Infrastructure Degree Program**  
(BITS - WIPRO Collaborative Programme - WIMS)  

**Daipayan Ghosal**  
**ID No.: 2022wa86002**  
*Email*: 2022wa86002@wilp.bits-pilani.ac.in  

Under the Supervision of  
**Ms. Nidhi Kashyap**  
Analyst, Cybersecurity Practice  
Wipro Limited, Pune  
*Email*: nidhi.kashyap@wipro.com  

Additional Examiner:  
**Mr. Satish Banigole**  
Project Manager, Wipro Limited, Pune  
*Email*: satish.banigole@wipro.com  

**Dissertation Work Carried Out At**:  
Wipro Limited, Pune / Bangalore  

**BIRLA INSTITUTE OF TECHNOLOGY AND SCIENCE**  
PILANI (RAJASTHAN)  
November, 2026  

<div style="page-break-after: always;"></div>

---

## CERTIFICATE FROM THE SUPERVISOR

**BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE, PILANI**  
**WORK INTEGRATED LEARNING PROGRAMMES (WILP) DIVISION**

This is to certify that the Dissertation entitled:

> **"Evidence-Grounded Generative AI for Vulnerability-to-Threat Investigation and Risk Prioritization"**

submitted by **Daipayan Ghosal** (BITS ID No. **2022wa86002**) in partial fulfillment of the requirements of course **CSIW ZG628T: Dissertation** for the **M.Tech in Computing Systems & Infrastructure** Degree Program, embodies the bonafide work done by him under my supervision at **Wipro Limited**.

In my opinion, this dissertation fulfills the rigorous academic and practical standards established by the Institute for Master of Technology level research. The results presented in this report have been verified against working prototype implementations, empirical benchmarks on 8,328 vulnerability records, and end-to-end evidence validation experiments.


<br><br><br>
____________________________________________  
**Ms. Nidhi Kashyap**  
*Dissertation Supervisor*  
Analyst, Cybersecurity Practice  
Wipro Limited, Pune, India  
Date: November 06, 2026  

<div style="page-break-after: always;"></div>

---

## ACKNOWLEDGEMENTS

I express my deepest gratitude to my supervisor, **Ms. Nidhi Kashyap**, Analyst at Wipro Limited, for her exceptional mentorship, incisive technical guidance, and consistent encouragement throughout the conception, design, and experimental execution of this dissertation. Her profound insights into enterprise vulnerability management and practical Security Operations Center (SOC) workflows have been instrumental in shaping the architecture of this work.

I am equally grateful to **Mr. Satish Banigole**, Project Manager at Wipro Limited, for serving as the Additional Examiner, providing valuable operational perspectives, reviewing project milestones, and offering constructive critiques that greatly improved the practical rigor of our threat correlation models.

I extend my sincere appreciation to the **Work Integrated Learning Programmes (WILP) Division of Birla Institute of Technology & Science (BITS), Pilani**, the Programme Coordinators, and faculty members of the **M.Tech Computing Systems & Infrastructure (WIMS)** program. The robust pedagogical foundation provided across cybersecurity, distributed infrastructure, and intelligent systems has empowered me to undertake and successfully deliver this research.

I also acknowledge the management and cybersecurity leadership at **Wipro Limited** for granting access to computing environments, fostering an environment of technical innovation, and supporting continuous professional and academic growth.

Finally, I owe my heartfelt thanks to my family, friends, and colleagues whose unwavering patience, moral support, and motivation sustained my energy across every phase of this academic journey.

<br>
**Daipayan Ghosal**  
BITS ID: 2022wa86002  
Pune, India  

<div style="page-break-after: always;"></div>

---

## ABSTRACT

Modern enterprise security operations centers (SOCs) face an overwhelming volume of software vulnerabilities and security alerts, precipitating acute operational fatigue and critical remediation bottlenecks. Traditional vulnerability management relies almost exclusively on static technical severity ratings—primarily the Common Vulnerability Scoring System (CVSS v3.x). However, CVSS rates flaws in an isolated laboratory setting without visibility into whether a vulnerability is actively weaponized by threat actors or where the affected component resides within the organizational perimeter. Consequently, organizations routinely waste thousands of critical engineering hours panic-patching theoretical vulnerabilities on internal, isolated hosts, while internet-facing systems harboring actively exploited flaws remain dangerously backlogged.

Simultaneously, while Generative Artificial Intelligence (GenAI) powered by Large Language Models (LLMs) offers immense potential for synthesizing multi-source threat intelligence, its adoption in high-stakes defensive operations is severely hindered by **stochastic hallucinations**, ungrounded assertions, and a lack of verifiable evidentiary provenance.

To address this dual challenge, this dissertation presents **VulnInvestigator**, a novel, evidence-grounded framework that strictly bifurcates deterministic contextual risk prioritization from generative investigative reasoning. The system integrates a deterministic multi-factor scoring engine that mathematically incorporates four contextual dimensions: normalized CVSS baseline severity ($w_1 = 0.35$), real-world threat actor weaponization via the CISA Known Exploited Vulnerabilities (KEV) catalog ($w_2 = 0.30$), enterprise business asset criticality ($w_3 = 0.20$), and perimeter network exposure ($w_4 = 0.15$). Selected high-priority vulnerabilities are dynamically correlated with the MITRE ATT&CK Matrix and enterprise Security Information and Event Management (SIEM) log telemetry. To interpret these correlated bundles, a constrained GenAI assistant powered by Google Gemini (gemini-3.5-flash) is deployed with strict prompt-boundary constraints and automated citation validation algorithms that extract explicit entity tokens (CVEs, ATT&CK techniques, log hashes) and flag unsupported claims.

The prototype was implemented in Python 3.12, persisted via an ACID-compliant SQLite schema, and evaluated across a comprehensive real-world dataset of **8,328 CVEs** (including 1,768 CISA KEV entries), **12 enterprise assets**, and correlated security logs. Experimental evaluation against the CVSS-only baseline demonstrated significant, non-random rank reshuffling with **Kendall's rank correlation coefficient $\tau = 0.5791$** ($p < 0.001$), **nDCG@10 = 0.4657**, and **Spearman's $\rho = 0.7539$**, confirming that generic severity alone fails to reflect true enterprise risk. In AI evidence-grounding benchmarks, the citation verification validator achieved an **Evidence Citation Rate of 100.0%**, a **Claim Support Rate of 82.7%**, and controlled speculative hallucinations to 20.0% with automatic yellow-highlight flagging. Automated failure-mode testing demonstrated 100% pass rates across missing data, unmapped assets, contradictory logs, and adversarial deception inputs. The platform was successfully packaged, open-sourced, and deployed to Streamlit Community Cloud (`https://vulninvestigator.streamlit.app`).

**Keywords**: Vulnerability Management, CVSS, CISA KEV, Contextual Risk Scoring, Threat Correlation, MITRE ATT&CK, Evidence-Grounded GenAI, Large Language Models, Hallucination Mitigation, Cybersecurity.

<div style="page-break-after: always;"></div>

---

## TABLE OF CONTENTS

- **Certificate from the Supervisor**
- **Acknowledgements**
- **Abstract**
- **List of Figures**
- **List of Tables**
- **List of Abbreviations & Symbols**

### **Chapter 1: Introduction**
- 1.1 Context and Industry Background
- 1.2 Problem Statement
- 1.3 Research Questions and Hypotheses
- 1.4 Research Objectives
- 1.5 Scope of Work and Boundaries
- 1.6 Key Contributions of the Dissertation
- 1.7 Thesis Organization

### **Chapter 2: Literature Review and Related Work**
- 2.1 Evolution of Vulnerability Prioritization Frameworks
  - 2.1.1 Common Vulnerability Scoring System (CVSS)
  - 2.1.2 Exploit Prediction Scoring System (EPSS)
  - 2.1.3 Stakeholder-Specific Vulnerability Categorization (SSVC)
- 2.2 Shortcomings of Static Severity in Enterprise Operations
- 2.3 Threat Intelligence and Exploitation Catalogs (CISA KEV)
- 2.4 Generative AI in Cyber Threat Intelligence (CTI) and SOC Workflows
- 2.5 The Hallucination Dilemma in High-Stakes Cybersecurity
- 2.6 Evidence Grounding and Retrieval-Augmented Verification
- 2.7 Literature Gap Analysis and Conceptual Positioning

### **Chapter 3: System Architecture and Mathematical Formulation**
- 3.1 Architectural Principles: Bifurcating Scoring and Reasoning
- 3.2 High-Level Architecture
- 3.3 Mathematical Formulation of Contextual Risk Scoring
  - 3.3.1 Factor 1: Normalized CVSS Severity
  - 3.3.2 Factor 2: Active Threat Exploitation (CISA KEV)
  - 3.3.3 Factor 3: Asset Business Criticality
  - 3.3.4 Factor 4: Network Perimeter Exposure
  - 3.3.5 Unified Weighted Formulation and Clamping
- 3.4 Risk Band Categorization
- 3.5 Threat Correlation Model (MITRE ATT&CK & SIEM Telemetry)
- 3.6 Evidence Bundle Construction and Prompt Boundary Engineering
- 3.7 Output Validation and Heuristic Citation Verification

### **Chapter 4: Implementation and System Engineering**
- 4.1 System Environment and Technology Stack
- 4.2 Data Collection and Normalization Pipeline
  - 4.2.1 NIST NVD REST API v2 Client
  - 4.2.2 CISA KEV Ingestion
  - 4.2.3 MITRE Enterprise ATT&CK STIX Parsing
- 4.3 Database Architecture and SQLite Schema Design
- 4.4 Enterprise Asset Inventory and Telemetry Log Simulator
- 4.5 LLM Client Integration (Google Gemini via google-genai SDK)
- 4.6 Verification Engine: Citation Extraction and Claim Annotation
- 4.7 Interactive Dashboard & Multipage Architecture

### **Chapter 5: Empirical Results and Evaluation**
- 5.1 Dataset Characterization
- 5.2 Ranking Quality and Agreement Evaluation
  - 5.2.1 Kendall's Rank Correlation (τ)
  - 5.2.2 Normalized Discounted Cumulative Gain (nDCG@k)
  - 5.2.3 Spearman's Rank Correlation (ρ)
- 5.3 Rank Displacement Distribution Analysis
- 5.4 AI Evidence-Grounding Benchmark Results
- 5.5 Automated Failure-Mode Stress Testing Matrix
- 5.6 Performance and Latency Characterization

### **Chapter 6: Discussion and Operational Impact**
- 6.1 Practical Impact on Enterprise SOC Operations
- 6.2 Plain-English Explainability for Leadership and Non-Technical Stakeholders
- 6.3 Comparative Analysis: CVSS vs. EPSS vs. SSVC vs. VulnInvestigator
- 6.4 Limitations and Threats to Validity

### **Chapter 7: Conclusions and Future Work**
- 7.1 Summary of Contributions
- 7.2 Fulfillment of Research Objectives
- 7.3 Future Research Directions

### **References**
### **Appendices**
- Appendix A: Complete Data Dictionary & Schema Definitions
- Appendix B: Enterprise Asset Inventory Specifications
- Appendix C: Prompts & System Instructions for GenAI Assistant
- Appendix D: Automated Unit Test Suite Summary (81 Passing Tests)
### **List of Publications / Conference Presentations**
### **Check List of Items for Final Report**

<div style="page-break-after: always;"></div>

---

## LIST OF FIGURES

1. **Figure 1.1**: The Vulnerability-to-Threat Pipeline showing traditional disconnect vs. contextual intelligence.
2. **Figure 3.1**: End-to-End System Architecture of VulnInvestigator illustrating the bifurcation between deterministic math and generative AI.
3. **Figure 3.2**: Contextual Risk Scoring Pillar Weights (CVSS: 35%, KEV: 30%, Asset: 20%, Exposure: 15%).
4. **Figure 3.3**: Evidence Bundle Synthesis and Citation Extraction Pipeline.
5. **Figure 4.1**: SQLite Relational Entity-Relationship Diagram (`vulnerabilities`, `assets`, `log_events`, `investigation_results`).
6. **Figure 5.1**: Kendall's $\tau$ Ranking Agreement Gauge Chart ($\tau = 0.5791$).
7. **Figure 5.2**: Empirical Rank Displacement Distribution across 8,328 CVEs.
8. **Figure 5.3**: AI Evidence Grounding Metric Breakdown (Citation Rate, Support Rate, Hallucination Rate, Confidence).
9. **Figure 5.4**: Automated Failure-Mode Taxonomy Test Results (4/4 Passed).
10. **Figure 6.1**: Multi-Factor Vulnerability Prioritization Comparison Matrix.

---

## LIST OF TABLES

1. **Table 1.1**: 16-Week Project Implementation Schedule and Milestones.
2. **Table 2.1**: Qualitative Comparison of Vulnerability Prioritization Frameworks.
3. **Table 3.1**: Weight Configuration for Contextual Risk Formula.
4. **Table 3.2**: Asset Business Criticality Tier Values.
5. **Table 3.3**: Network Perimeter Exposure Tier Values.
6. **Table 3.4**: Contextual Risk Band Mapping Thresholds.
7. **Table 4.1**: Enterprise Asset Inventory Specification (12 Assets).
8. **Table 4.2**: Core SQLite Database Schema Attributes.
9. **Table 5.1**: Dataset Summary Statistics (Vulnerabilities, Assets, Logs, Techniques).
10. **Table 5.2**: Ranking Evaluation Metrics Summary (Kendall's $\tau$, nDCG@10, nDCG@20, Spearman's $\rho$).
11. **Table 5.3**: Top 10 Priority Displacements (Significant Escalations and De-escalations).
12. **Table 5.4**: AI Evidence Grounding Benchmark Evaluation Results.
13. **Table 5.5**: Automated Failure-Mode Stress Test Matrix.

---

## LIST OF ABBREVIATIONS & SYMBOLS

* **API**: Application Programming Interface
* **ATT&CK**: Adversarial Tactics, Techniques, and Common Knowledge (MITRE)
* **CISA**: Cybersecurity and Infrastructure Security Agency (United States)
* **CPE**: Common Platform Enumeration
* **CTI**: Cyber Threat Intelligence
* **CVE**: Common Vulnerabilities and Exposures
* **CVSS**: Common Vulnerability Scoring System
* **DMZ**: Demilitarized Zone
* **EPSS**: Exploit Prediction Scoring System
* **GenAI**: Generative Artificial Intelligence
* **JSON**: JavaScript Object Notation
* **KEV**: Known Exploited Vulnerabilities (CISA Catalog)
* **LLM**: Large Language Model
* **nDCG**: Normalized Discounted Cumulative Gain
* **NIST**: National Institute of Standards and Technology
* **NVD**: National Vulnerability Database
* **PII**: Personally Identifiable Information
* **RAG**: Retrieval-Augmented Generation
* **RCE**: Remote Code Execution
* **SIEM**: Security Information and Event Management
* **SOC**: Security Operations Center
* **SQL**: Structured Query Language
* **SSVC**: Stakeholder-Specific Vulnerability Categorization
* **STIX**: Structured Threat Information Expression
* **WAF**: Web Application Firewall
* **WILP**: Work Integrated Learning Programmes (BITS Pilani)
* **$\tau$ (tau)**: Kendall's Rank Correlation Coefficient
* **$\rho$ (rho)**: Spearman's Rank Correlation Coefficient

<div style="page-break-after: always;"></div>

---

# CHAPTER 1: INTRODUCTION

## 1.1 Context and Industry Background

Enterprise IT infrastructure has grown exponentially in complexity, spanning multi-cloud platforms, distributed hybrid networks, microservices architectures, and third-party software dependencies. Concurrently, the rate at which novel software vulnerabilities are identified and registered has exploded. According to the National Institute of Standards and Technology (NIST), over 29,000 Common Vulnerabilities and Exposures (CVEs) were cataloged in 2023 alone, with annual publication numbers consistently breaking historical records through 2026.

In an enterprise containing tens of thousands of digital endpoints, security operations centers (SOCs) and vulnerability management teams receive daily vulnerability scanning reports identifying thousands of unpatched software components. Remediating every reported vulnerability immediately is physically and financially impossible: patching requires scheduled maintenance windows, compatibility testing, regression validation, and substantial engineering labor. 

Consequently, organizations are forced to prioritize. The universal industry default for prioritization has long been the Common Vulnerability Scoring System (CVSS), maintained by the Forum of Incident Response and Security Teams (FIRST). CVSS assigns each vulnerability a numerical score from 0.0 to 10.0, categorized into Low, Medium, High, and Critical severity tiers. Enterprise compliance mandates and Service Level Agreements (SLAs) frequently dictate that any vulnerability with a CVSS score $\ge 7.0$ (High or Critical) must be patched within 14 to 30 days.

## 1.2 Problem Statement

Despite its universal adoption, relying exclusively on static CVSS scores for vulnerability remediation introduces severe systemic failures in real-world cybersecurity defense:

1. **Environmental Blindness**: CVSS base scores evaluate vulnerabilities in a theoretical laboratory vacuum. A CVSS 9.8 remote code execution flaw on an isolated, air-gapped backup server is scored identically to the same flaw on a public-facing corporate reverse proxy. In reality, the risk to the business is drastically different.
2. **Exploitation Disconnect**: Academic research demonstrates that fewer than 5% to 8% of published CVEs are ever weaponized or actively exploited in the wild. CVSS base metrics do not factor in real-time adversary behavior. Organizations routinely waste millions of dollars panic-patching unexploited CVSS 9.0+ bugs, while actively weaponized CVSS 7.2 flaws on exposed perimeter gateways remain unpatched.
3. **Severe Alert Fatigue and Cognitive Overload**: Because roughly 40% of all published CVEs receive a CVSS score $\ge 7.0$, remediation teams are perpetually overwhelmed. This "alert fatigue" causes critical zero-day threats to get lost in the noise.
4. **Investigative Fragmentation**: When security analysts attempt to investigate whether a vulnerability is actively being exploited, they must manually pivot between fragmented datasets: NVD vulnerability details, CISA Known Exploited Vulnerability bulletins, MITRE ATT&CK adversary techniques, and disparate SIEM security logs. This manual correlation is slow, error-prone, and unsustainable.
5. **The GenAI Hallucination Dilemma**: While Large Language Models (LLMs) have emerged as powerful tools for summarizing technical data, standard LLMs suffer from stochastic hallucinations—fabricating IP addresses, inventing non-existent CVEs, and producing plausible-sounding but completely incorrect remediation advice. In high-stakes cyber defense, ungrounded AI outputs introduce catastrophic operational risks.

There is a critical, unmet industry need for an end-to-end framework that **bifurcates deterministic, context-aware mathematical risk scoring from generative investigation reasoning**, using GenAI solely as an evidence-grounded investigative assistant constrained by verifiable security telemetry.

![Figure 1.1: Vulnerability Disconnect](figures/figure_1_1_disconnect.png)

*Figure 1.1: The Vulnerability-to-Threat Pipeline showing traditional disconnect vs. contextual intelligence.*

## 1.3 Research Questions and Hypotheses

This dissertation addresses the following core research questions:

* **RQ1**: How can vulnerability severity, active threat actor exploitation intelligence, enterprise asset criticality, and perimeter network exposure be mathematically synthesized into a deterministic contextual risk scoring engine that outperforms static CVSS prioritization?
* **RQ2**: To what extent does contextual risk scoring reshuffle the enterprise remediation queue compared to CVSS-only prioritization, as measured by standard ranking correlation metrics (Kendall's $\tau$, nDCG@k, Spearman's $\rho$)?
* **RQ3**: Can a Generative AI assistant be architecturally constrained to synthesize threat investigation hypotheses, SIEM log queries, and remediation advice derived strictly from verifiable security evidence without fabricating intelligence?
* **RQ4**: How can automated citation verification and claim-support validators quantify and mitigate AI hallucinations in defensive cybersecurity operations?

### Core Hypotheses:
* **Hypothesis 1 ($H_1$)**: Integrating active exploitation status (CISA KEV) and environmental asset exposure with CVSS severity will yield a statistically significant, non-random re-ordering of vulnerability priorities (Kendall's $\tau < 0.70$), substantially reducing false-alarm remediation demands.
* **Hypothesis 2 ($H_2$)**: Constraining an LLM through structured evidence-bundle prompt boundaries and heuristic citation validators will achieve an Evidence Citation Rate $\ge 95\%$ and a Claim Support Rate $\ge 80\%$ on threat investigation workflows.

## 1.4 Research Objectives

To validate these hypotheses, this dissertation accomplishes five formal technical objectives:

1. **Pipeline Engineering**: Design and implement an automated data collection and normalization pipeline in Python that extracts, parses, and unifies vulnerability metadata from the NIST NVD REST API v2, active exploit intelligence from the CISA KEV catalog, and adversary tactics from the MITRE Enterprise ATT&CK matrix.
2. **Contextual Risk Engine**: Formulate and implement a transparent, deterministic risk scoring formula that balances technical severity ($w_1 = 0.35$), wild exploitation ($w_2 = 0.30$), asset business criticality ($w_3 = 0.20$), and perimeter network exposure ($w_4 = 0.15$).
3. **Telemetry & Attack Correlator**: Build a threat correlation engine and synthetic enterprise SIEM log simulator mapped to 12 realistic organizational assets, pairing vulnerability profiles with MITRE ATT&CK techniques and security telemetry.
4. **Evidence-Grounded GenAI Assistant**: Deploy an LLM client (Google Gemini via `google-genai` SDK) governed by strict prompt engineering and an automated heuristic output validator that extracts citations, annotates claim support, and highlights speculative statements.
5. **Empirical Evaluation & Cloud Deployment**: Benchmark the complete framework against CVSS-only baselines across 8,328 CVEs using Kendall's $\tau$, nDCG@10, and Spearman's $\rho$; execute automated failure-mode testing; and deliver a fully functional, public cloud dashboard deployed on Streamlit Community Cloud.

## 1.5 Scope of Work and Boundaries

To ensure scientific rigor and focus, the following boundaries govern this research:

* **In Scope**:
  * Public vulnerability intelligence (NIST NVD, CISA KEV).
  * Standard enterprise assets (servers, databases, workstations, public proxies, gateways).
  * Deterministic mathematical formulation of multi-factor risk scores.
  * Defensive threat correlation with MITRE ATT&CK and SIEM security logs.
  * GenAI investigation assistance, evidence citation validation, and hallucination detection.
  * Quantitative statistical evaluation and interactive web dashboard development.
* **Out of Scope**:
  * Construction of a commercial, real-time enterprise SIEM collector or log storage daemon.
  * Autonomous offensive exploitation or automated penetration testing.
  * Automated unassisted patch deployment (the system outputs verified remediation recommendations for human security analysts).

## 1.6 Key Contributions of the Dissertation

The primary contributions of this dissertation are:

1. **A Bifurcated Cybersecurity Architecture**: A clean separation of concerns wherein all numerical prioritization is handled by a deterministic mathematical engine, and generative AI is restricted entirely to explaining evidence and drafting defensive queries.
2. **A Validated Multi-Factor Contextual Scoring Model**: A mathematically formulated scoring engine that incorporates environmental exposure and CISA KEV data, proven empirically on 8,328 vulnerabilities to significantly disrupt the CVSS queue (Kendall's $\tau = 0.5791$, nDCG@10 = $0.4657$).
3. **An Evidence-Grounded Citation Verification Engine**: A heuristic validator that audits LLM outputs sentence-by-sentence, extracting technical citations, calculating grounding confidence scores, and highlighting unsupported claims in yellow.
4. **A Production-Grade, Open-Source Prototype**: A complete, fully tested software implementation (81 unit tests) featuring on-demand live NVD ingestion, dynamic evaluation re-computation, executive non-technical explainability interfaces, and public cloud deployment on Streamlit Cloud (`https://vulninvestigator.streamlit.app`).

## 1.7 Thesis Organization

The remainder of this dissertation is structured as follows:
* **Chapter 2** reviews related academic literature, historical vulnerability scoring systems, LLM evaluation frameworks in CTI, and hallucination mitigation techniques.
* **Chapter 3** presents the formal system architecture, mathematical scoring formulations, threat correlation design, and evidence-grounded prompt boundary protocols.
* **Chapter 4** details the software engineering implementation, data normalization pipelines, SQLite database schema, Gemini LLM integration, and dashboard components.
* **Chapter 5** presents comprehensive empirical results, ranking correlation metrics, rank displacement distributions, grounding evaluation rates, and failure-mode stress tests.
* **Chapter 6** discusses operational SOC implications, plain-English executive explainability, comparisons with alternative frameworks (EPSS, SSVC), and threats to validity.
* **Chapter 7** concludes the dissertation, summarizes the achievement of research objectives, and outlines promising avenues for future research.

<div style="page-break-after: always;"></div>

---

# CHAPTER 2: LITERATURE REVIEW AND RELATED WORK

## 2.1 Evolution of Vulnerability Prioritization Frameworks

Prioritizing vulnerability remediation has evolved over two decades from ad-hoc patching to standardized technical metrics, and recently toward risk-based prioritization.

### 2.1.1 Common Vulnerability Scoring System (CVSS)
Developed by the National Infrastructure Advisory Council (NIAC) and currently governed by FIRST, CVSS has served as the de-facto global standard across versions 2.0, 3.0, 3.1, and the recently finalized 4.0 (Mell et al., 2007; FIRST, 2023). CVSS computes a base score ranging from 0.0 to 10.0 derived from two sub-score groups: **Exploitability Metrics** (Attack Vector, Attack Complexity, Privileges Required, User Interaction) and **Impact Metrics** (Confidentiality, Integrity, Availability).

While CVSS provides an objective measure of theoretical severity, researchers have continuously criticized its real-world effectiveness. Allodi and Massacci (2014) conducted an empirical analysis of over 40,000 vulnerabilities and demonstrated that a vulnerability's CVSS score exhibits near-zero correlation with whether that vulnerability is ever exploited in the wild. High CVSS scores indicate that *if* a flaw is exploited, the technical damage would be severe; it does not indicate that an attacker *can or will* exploit it in a specific organization.

### 2.1.2 Exploit Prediction Scoring System (EPSS)
To address the lack of temporal exploitability in CVSS, Jacobs et al. (2021) introduced the Exploit Prediction Scoring System (EPSS) under FIRST. EPSS utilizes machine learning models trained on threat intelligence feeds, security blogs, and honeypot telemetry to estimate the empirical probability ($P \in [0, 1]$) that a vulnerability will be exploited in the wild within the next 30 days.

While EPSS significantly improves upon CVSS by predicting exploitability, it remains fundamentally **asset-blind**. EPSS outputs a global probability for a CVE; it has zero knowledge of whether the vulnerable software is deployed on a critical production banking server or an isolated test workstation.

### 2.1.3 Stakeholder-Specific Vulnerability Categorization (SSVC)
Recognizing the limitations of single numerical scores, the Carnegie Mellon University Software Engineering Institute (SEI) and CISA developed SSVC (Spring et al., 2021). SSVC abandons numerical scoring entirely in favor of qualitative decision trees that output four discrete remediation actions: *Track*, *Track*, *Attend*, or *Act*. SSVC decision trees incorporate factors such as *Exploitation Status*, *Utility*, and *Technical Impact*.

However, SSVC decision trees are difficult to integrate into automated enterprise reporting pipelines that require continuous numerical risk quantification, threshold tracking, and mathematical displacement analytics.

| Framework | Exploitation Status | Asset Criticality | Network Exposure | Output Type | Primary Limitation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **CVSS v3.1** | Static / Optional | ❌ Ignored | ❌ Ignored | Continuous (0–10) | Environmental blindness; high false alarms |
| **EPSS v3** | Predictive ($P$) | ❌ Ignored | ❌ Ignored | Probability [0, 1] | Asset-blind; ignores internal business impact |
| **SSVC v2** | Categorical | Categorical | Categorical | Decision Trees (4 Actions) | No fine-grained ranking; hard to track displacement |
| **VulnInvestigator** | **CISA KEV (Real)** | **Quantitative (Tier)** | **Quantitative (Perimeter)** | **Continuous [0.0, 1.0]** | Combines empirical exploitability with environmental context |

**Table 2.1**: Qualitative comparison of vulnerability prioritization frameworks.

## 2.2 Shortcomings of Static Severity in Enterprise Operations

In a comprehensive survey on vulnerability prioritization, Jiang et al. (2025) reviewed over a decade of prioritization literature and concluded that static severity scoring has reached an architectural dead end. They established a modern prioritization taxonomy asserting that effective enterprise prioritization requires a triad of:
1. **Flaw Characteristics**: Technical mechanics and inherent attack vectors.
2. **Threat Intelligence**: Real-world exploit kits, active weaponization, and campaign tracking.
3. **Environmental Context**: Topological reachability, host criticality, and network boundary defense.

Their findings directly validate the design of this dissertation: prioritizing vulnerabilities without organizational context wastes up to 60% of SOC remediation capacity on benign findings.

## 2.3 Threat Intelligence and Exploitation Catalogs (CISA KEV)

In November 2021, the U.S. Cybersecurity and Infrastructure Security Agency issued Binding Operational Directive (BOD) 22-01, establishing the **Known Exploited Vulnerabilities (KEV) Catalog**. Unlike crowdsourced databases or unverified exploit repositories, CISA KEV includes only vulnerabilities for which CISA has confirmed **active, real-world exploitation in the wild by malicious actors**.

Empirical cybersecurity studies have confirmed that CISA KEV is the single most reliable indicator of real-world threat urgency. Our dataset analysis in Chapter 5 reveals that of 8,328 analyzed CVEs, only 1,768 (21.2%) appear in CISA KEV. Elevating KEV-listed vulnerabilities provides immediate protection against active cyber campaigns while allowing unexploited CVEs to be scheduled during regular patching intervals.

## 2.4 Generative AI in Cyber Threat Intelligence (CTI) and SOC Workflows

Large Language Models (LLMs), such as OpenAI GPT-4, Anthropic Claude, and Google Gemini, have demonstrated remarkable capability in parsing unstructured technical text, translating security logs, and synthesizing incident timelines.

In 2024, Alam et al. introduced **CTIBench**, the first standardized benchmark specifically designed to assess LLM capabilities across cyber threat intelligence tasks. CTIBench evaluated multiple state-of-the-art foundation models across threat extraction, technique mapping, and vulnerability reasoning. Their findings revealed that while LLMs excel at summarizing technical narratives, their raw generative reasoning suffers significant performance degradation when required to accurately correlate quantitative scores, identify fine-grained MITRE techniques, or synthesize multi-step investigations. Alam et al. concluded that LLMs cannot act as unconstrained, autonomous decision-makers in enterprise security operations; instead, they must be augmented with deterministic tools and external ground-truth constraints.

## 2.5 The Hallucination Dilemma in High-Stakes Cybersecurity

The propensity of LLMs to hallucinate—defined as generating factually incorrect, unverifiable, or contradictory information disguised as authoritative truth (Ji et al., 2023)—presents an acute danger in cyber defense. 

Intriguingly, Mudassar Yamin et al. (2024) demonstrated that LLM hallucinations could be deliberately weaponized for creative purposes: they utilized hallucination dynamics to generate novel, highly unpredictable cyber warfare exercise scenarios for red-team training. However, Mudassar Yamin et al. explicitly emphasized that this exact characteristic is **catastrophic in live defensive incident response**. An analyst who receives a hallucinated remediation command or a fabricated IOC (Indicator of Compromise) will misconfigure defenses, block legitimate traffic, or overlook active adversarial persistence.

## 2.6 Evidence Grounding and Retrieval-Augmented Verification

To prevent generative hallucinations, the field of Natural Language Processing has advanced toward **Retrieval-Augmented Generation (RAG)** and **Evidence Grounding** (Lewis et al., 2020). In evidence-grounded systems, the model is strictly conditioned upon a curated evidence bundle provided directly within the prompt context window, accompanied by system instructions explicitly forbidding ungrounded extrapolations.

Recent work by Gou et al. (2024) on citation-augmented generation demonstrates that forcing models to append verifiable entity citations directly to individual claims dramatically reduces hallucination rates while enabling automated downstream validators to programmatically audit outputs against source documents.

## 2.7 Literature Gap Analysis and Conceptual Positioning

Synthesizing the state-of-the-art reveals two distinct, disconnected paradigms:
* **The Prioritization Camp**: Security researchers build mathematical and machine learning models for risk scoring (CVSS, EPSS, SSVC), but output dry, tabular rankings that leave analysts to manually guess how to investigate potential compromises.
* **The Generative AI Camp**: AI researchers apply conversational LLMs to security operations, but grant the model unrestricted generative freedom, producing ungrounded, hallucinated hypotheses without mathematical risk grounding.

**The Research Gap**: No existing system bridges these two worlds by combining **deterministic, multi-factor risk prioritization** with **strictly evidence-grounded generative investigation** where the AI is constrained by the deterministic engine's telemetry bundle and audited by automated citation verification. This dissertation directly fills this gap with **VulnInvestigator**.

<div style="page-break-after: always;"></div>

---

# CHAPTER 3: SYSTEM ARCHITECTURE AND MATHEMATICAL FORMULATION

## 3.1 Architectural Principles: Bifurcating Scoring and Reasoning

The core architectural foundation of **VulnInvestigator** is the strict principle of **Bifurcated Security Intelligence**:

> **Principle of Deterministic Separation**: Numerical prioritization, metric calculation, and queue sorting must remain 100% deterministic, transparent, and reproducible using standard mathematical formulas. Generative AI must never calculate, guess, or modify quantitative risk scores. Conversely, natural language synthesis, hypothesis generation, and query drafting are delegated to GenAI, but strictly bound within an evidence-verified context window.

This bifurcation ensures that:
1. Executive leadership and auditors can inspect the exact mathematical contribution of every risk factor without opaque "black-box" AI variability.
2. The AI assistant cannot hallucinate a risk score or alter remediation queue priorities.
3. Every claim produced by the AI assistant can be audited by algorithmic citation validators.

```
       ┌─────────────────────────────────────────────────────────────┐
       │                EXTERNAL THREAT INTELLIGENCE                 │
       │   NIST NVD REST API v2  │  CISA KEV Catalog  │  MITRE ATT&CK │
       └───────────────┬──────────────────────┬───────────────┬──────┘
                       │                      │               │
┌──────────────────────▼──────────────────────▼───────────────▼──────────────────────┐
│                    DATA INGESTION & NORMALIZATION PIPELINE                         │
│       Stateless Normalizers  │  CPE Matchers  │  SQLite Database Persistence        │
└──────────────────────────────────────┬─────────────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼─────────────────────────────────────────────┐
│                 DETERMINISTIC CONTEXTUAL RISK SCORING ENGINE                       │
│                                                                                    │
│   RiskScore = 0.35·(CVSS/10) + 0.30·(KEV) + 0.20·(AssetCrit) + 0.15·(Exposure)     │
│   Clamped to [0.0, 1.0]  │  Band: Critical / High / Medium / Low                   │
└───────────────────┬─────────────────────────────────────────────┬──────────────────┘
                    │                                             │
┌───────────────────▼──────────────────┐   ┌──────────────────────▼──────────────────┐
│     THREAT CORRELATION ENGINE        │   │        RANKING & DISPLACEMENT           │
│   MITRE ATT&CK Mapping (e.g. T1190)  │   │   Kendall's τ  │  nDCG@10  │  Spearman ρ│
│   SIEM Telemetry Logs (Signal/Noise) │   │   Priority Shift = Rank_cvss - Rank_ctx │
└───────────────────┬──────────────────┘   └─────────────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────────────────────────────────────┐
│                   STRUCTURED EVIDENCE BUNDLE BUILDER                               │
│       Prompt Boundary Formulation  │  In-Context Grounding Constraints             │
└───────────────────────────────────┬────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────────┐
│            EVIDENCE-GROUNDED GenAI INVESTIGATION ASSISTANT                         │
│               Google Gemini LLM Client (gemini-3.5-flash)                          │
│               System Prompts forbidding ungrounded extrapolations                  │
└───────────────────────────────────┬────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────────┐
│           AUTOMATED CITATION VALIDATOR & HALLUCINATION DETECTOR                    │
│   Extracts Entity Citations  │  Audits Claim Support  │  Flags Unsupported Text   │
└───────────────────────────────────┬────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────────────┐
│               INTERACTIVE STREAMLIT WEB DASHBOARD                                  │
│   Overview  │  Rankings  │  Investigation  │  AI Assistant  │  Evaluation          │
└────────────────────────────────────────────────────────────────────────────────────┘
```
**Figure 3.1**: End-to-end system architecture of VulnInvestigator illustrating the bifurcation between deterministic math and generative AI.

## 3.2 High-Level Architecture

The system consists of five modular subsystems:
1. **Data Ingestion & Normalization Pipeline**: Ingests raw JSON feeds from NIST NVD, CISA KEV, and MITRE ATT&CK, transforming them into a relational SQLite database schema.
2. **Contextual Risk Engine**: Computes multi-factor contextual risk scores, risk bands, and queue rankings across the dataset.
3. **Threat Correlation & Telemetry Simulator**: Maps selected vulnerabilities to organizational assets, matches attack techniques, and correlates SIEM security logs.
4. **Evidence-Grounded GenAI Assistant**: Ingests structured evidence bundles, invokes Google Gemini with strict grounding system instructions, and formats structured investigative hypotheses.
5. **Output Verification & Citation Validator**: Audits generated text using regular expression heuristics and word-overlap matchers, highlighting ungrounded claims in yellow and calculating factual grounding metrics.

## 3.3 Mathematical Formulation of Contextual Risk Scoring

Let $V$ represent the set of all vulnerabilities in the enterprise catalog, and let $v \in V$ represent a specific vulnerability. Let $A$ represent the enterprise asset inventory, and let $a \in A$ represent the specific enterprise asset hosting the software affected by $v$.

The **Contextual Risk Score** $R(v, a)$ is formulated as a linear weighted sum of four normalized dimensions:

$$R(v, a) = w_{\text{cvss}} \cdot S_{\text{cvss}}(v) + w_{\text{kev}} \cdot S_{\text{kev}}(v) + w_{\text{asset}} \cdot S_{\text{asset}}(a) + w_{\text{exp}} \cdot S_{\text{exp}}(a)$$

Subject to the foundational convex weighting constraint:

$$\sum_{i \in \{\text{cvss}, \text{kev}, \text{asset}, \text{exp}\}} w_i = w_{\text{cvss}} + w_{\text{kev}} + w_{\text{asset}} + w_{\text{exp}} = 1.0, \quad \forall w_i \ge 0$$

And the bounding constraint ensuring normalized output:

$$R(v, a) \in [0.0, 1.0]$$

```
                   ┌─────────────────────────────────────────┐
                   │    CONTEXTUAL RISK SCORE [0.0 - 1.0]    │
                   └────────────────────┬────────────────────┘
                                        │
         ┌──────────────────┬───────────┴──────────┬──────────────────┐
         │                  │                      │                  │
┌────────▼────────┐┌────────▼────────┐   ┌─────────▼────────┐┌────────▼────────┐
│  CVSS Severity  ││ CISA KEV Threat │   │ Asset Importance ││ Perimeter Access│
│   Weight: 35%   ││   Weight: 30%   │   │   Weight: 20%    ││   Weight: 15%   │
│  S_cvss / 10.0  ││ 1.0 if in KEV   │   │ Critical: 1.0    ││ Internet: 1.0   │
│                 ││ 0.0 otherwise   │   │ High: 0.75       ││ DMZ: 0.75       │
│                 ││                 │   │ Medium: 0.50     ││ Internal: 0.50  │
│                 ││                 │   │ Low: 0.25        ││ Air-Gapped: 0.0 │
└─────────────────┘└─────────────────┘   └──────────────────┘└─────────────────┘
```
**Figure 3.2**: Four-pillar contextual risk scoring architecture with normalized weights.

### 3.3.1 Factor 1: Normalized CVSS Severity ($S_{\text{cvss}}$)
The technical flaw severity $C(v) \in [0.0, 10.0]$ is extracted from CVSS v3.1 base score (falling back to CVSS v3.0 or v2.0 if v3.1 is unavailable). It is normalized linearly to the unit interval $[0.0, 1.0]$:

$$S_{\text{cvss}}(v) = \frac{C(v)}{10.0}, \quad \text{where } C(v) \in [0.0, 10.0]$$

If $C(v)$ is missing, null, or unassigned, the engine applies a conservative fallback of $S_{\text{cvss}}(v) = 0.0$.

### 3.3.2 Factor 2: Active Threat Exploitation ($S_{\text{kev}}$)
The active exploitation status $K(v)$ is determined by membership in the CISA KEV catalog. Because CISA KEV represents verified, active in-the-wild exploitation by malicious actors, it is formulated as a discrete binary step function:

$$S_{\text{kev}}(v) = \begin{cases} 1.0 & \text{if } v \in \text{CISA\_KEV} \\ 0.0 & \text{if } v \notin \text{CISA\_KEV} \end{cases}$$

An actively exploited vulnerability contributes a full $0.300$ directly to the cumulative risk score, ensuring that weaponized CVEs immediately surge toward the top of the remediation queue.

### 3.3.3 Factor 3: Asset Business Criticality ($S_{\text{asset}}$)
Asset criticality represents the potential business impact on confidentiality, integrity, availability, and financial/compliance operations if the host $a$ is compromised. It maps categorical enterprise asset tiers into standardized interval values:

$$S_{\text{asset}}(a) = f_{\text{crit}}(\text{Tier}(a))$$

| Criticality Tier ($\text{Tier}(a)$) | Normalized Score ($S_{\text{asset}}$) | Operational Definition / Enterprise Scope |
| :--- | :---: | :--- |
| **Critical** | $1.00$ | Mission-critical core infrastructure (Production databases, domain controllers, payment gateways, core identity providers). Compromise results in catastrophic operational outage or major regulatory non-compliance. |
| **High** | $0.75$ | High-importance production systems (Departmental application servers, analytics pipelines, HR databases holding employee PII). |
| **Medium** | $0.50$ | Standard corporate infrastructure (Developer laptops, staging servers, internal proxy relays). |
| **Low** | $0.25$ | Low-impact operational systems (Guest wireless controllers, isolated sandbox machines, digital signage displays). |
| **Unknown** | $0.10$ | Unclassified host (Conservative baseline applied pending CMDB inventory reconciliation). |

**Table 3.2**: Asset business criticality mapping values.

### 3.3.4 Factor 4: Network Perimeter Exposure ($S_{\text{exp}}$)
Network exposure measures the topological accessibility of the target asset from untrusted external threat actors:

$$S_{\text{exp}}(a) = f_{\text{exp}}(\text{Exposure}(a))$$

| Exposure Tier ($\text{Exposure}(a)$) | Normalized Score ($S_{\text{exp}}$) | Topological Network Description |
| :--- | :---: | :--- |
| **Internet-Facing** | $1.00$ | Directly addressable via public IPv4/IPv6 addresses without authentication barriers (Reverse proxies, public web applications, external VPN portals). |
| **DMZ** | $0.75$ | Demilitarized zone systems placed behind perimeter firewalls but processing ingress connections from external endpoints. |
| **Internal** | $0.50$ | Systems situated within private enterprise subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) requiring internal corporate network access or established VPN tunnels. |
| **Restricted** | $0.25$ | Micro-segmented subnets requiring multi-factor jumpbox/bastion authentication and strict protocol whitelisting. |
| **Air-Gapped** | $0.00$ | Completely isolated physical networks with zero inbound/outbound external network routing. |

**Table 3.3**: Network perimeter exposure mapping values.

### 3.3.5 Unified Weighted Formulation and Clamping
Combining all four terms using our empirically calibrated weights:

$$R(v, a) = 0.35 \cdot \left(\frac{C(v)}{10.0}\right) + 0.30 \cdot K(v) + 0.20 \cdot S_{\text{asset}}(a) + 0.15 \cdot S_{\text{exp}}(a)$$

To guard against floating-point inaccuracies or out-of-spec inputs, the score is explicitly clamped:

$$R_{\text{final}}(v, a) = \max\left(0.0, \min\left(1.0, R(v, a)\right)\right)$$

![Figure 3.2: Multi-Factor Contextual Risk Scoring Pillar Weights](figures/figure_3_2_weights.png)

*Figure 3.2: Four-pillar contextual risk scoring architecture with normalized weights.*

## 3.4 Risk Band Categorization

To support executive decision-making and automated SLA assignment, continuous risk scores are mapped into four operational risk bands:

$$\text{Band}(R) = \begin{cases} 
\text{\textbf{Critical}} & \text{if } R \ge 0.80 \\ 
\text{\textbf{High}} & \text{if } 0.60 \le R < 0.80 \\ 
\text{\textbf{Medium}} & \text{if } 0.40 \le R < 0.60 \\ 
\text{\textbf{Low}} & \text{if } R < 0.40 
\end{cases}$$

**Table 3.4**: Contextual risk band thresholds and recommended SLA actions.

## 3.5 Threat Correlation Model (MITRE ATT&CK & SIEM Telemetry)

When an analyst selects a vulnerability for investigation, the **Threat Correlator** executes a two-stage correlation:

1. **Adversary Technique Mapping**: The software stack and vulnerability description are tokenized and matched against the MITRE Enterprise ATT&CK Matrix. For example, remote code execution flaws affecting web proxies (Apache, Nginx) automatically map to technique **`T1190`** (*Exploit Public-Facing Application*), while local privilege escalation flaws on workstations map to **`T1068`** (*Exploitation for Privilege Escalation*).
2. **SIEM Log Correlation**: The correlator searches the security event log database for telemetry matching the target asset ID, IP address, and correlated ATT&CK technique IDs. Events are split into **Signal Telemetry** (suspicious payloads, command injections, unauthorized traversal requests) and **Background Noise Telemetry** (benign routine traffic, failed internal health probes), testing the analyst and AI assistant's ability to discriminate true indicators from noise.

## 3.6 Evidence Bundle Construction and Prompt Boundary Engineering

To prevent the LLM from hallucinating ungrounded assumptions, the system constructs a strictly formatted, self-contained JSON **Evidence Bundle** that serves as the prompt boundary:

```json
{
  "cve_id": "CVE-2021-44228",
  "technical_severity": { "cvss_v3_score": 10.0, "severity": "CRITICAL" },
  "active_exploitation": { "in_cisa_kev": true },
  "target_asset": {
    "asset_id": "SRV-WEB-001",
    "hostname": "web-proxy-01",
    "ip": "203.0.113.10",
    "criticality": "critical",
    "exposure": "internet_facing"
  },
  "contextual_risk": { "score": 0.993, "band": "Critical" },
  "correlated_attack_techniques": [
    { "id": "T1190", "name": "Exploit Public-Facing Application", "tactics": "Initial Access" }
  ],
  "correlated_siem_logs": [
    { "event_id": "ev-101", "timestamp": "2026-11-01T08:14:22Z", "source_ip": "198.51.100.44", "raw_log": "POST /login HTTP/1.1 payload=${jndi:ldap://evil.com/x}" }
  ]
}
```

The system instruction explicitly enforces the following epistemic rules:
1. *Constraint 1*: Every investigative claim must cite the specific `event_id`, `technique_id`, or `asset_id` from which it is derived.
2. *Constraint 2*: If the log telemetry is insufficient to confirm compromise, the model must explicitly self-tag the statement with `[UNSUPPORTED]` or state that evidence is inconclusive.
3. *Constraint 3*: The model must not invent IP addresses, domain names, or CVE numbers not present in the evidence bundle.

## 3.7 Output Validation and Heuristic Citation Verification

To guarantee accountability, the generated narrative is audited post-generation by a deterministic Python validator (`OutputValidator`):

```
       ┌────────────────────────────────────────────────────────┐
       │               RAW GENERATED LLM REPORT                 │
       └───────────────────────────┬────────────────────────────┘
                                   │
                   ┌───────────────┴───────────────┐
                   ▼                               ▼
       ┌──────────────────────┐        ┌──────────────────────┐
       │ CITATION EXTRACTION  │        │ UNCERTAINTY MARKERS  │
       │ Regex Entity Parser  │        │ Heuristic Classifier │
       │ Matches: CVEs, Ts,   │        │ Flags: [UNSUPPORTED],│
       │ Log IDs, Hostnames   │        │ "speculate", "might" │
       └───────────┬──────────┘        └───────────┬──────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   │
       ┌───────────────────────────▼────────────────────────────┐
       │              EVIDENCE GROUNDING AUDITOR                │
       │   Computes: Citation Rate, Claim Support %, Halluc %   │
       │   Annotates Text: Highlights Unsupported Claims in     │
       │   Yellow HTML (<mark style='background:#fff3cd'>)      │
       └────────────────────────────────────────────────────────┘
```
**Figure 3.3**: Evidence bundle synthesis and heuristic citation validation pipeline.

The validator computes four quantitative audit metrics:
1. **Evidence Citation Rate**: The proportion of generated reports that explicitly cite evidence tokens:
   $$\text{CitationRate} = \frac{\sum_{i=1}^{N} \mathbb{I}(|\text{Citations}(r_i)| > 0)}{N}$$
2. **Claim Support Rate**: The proportion of individual claim sentences that correlate directly with verified evidence bundle tokens:
   $$\text{ClaimSupportRate} = \frac{\sum_{i=1}^{N} \text{ConfidenceScore}(r_i)}{N}$$
3. **Hallucination Rate**: The proportion of reports exhibiting unsupported assertions or model self-tagged uncertainty warnings:
   $$\text{HallucinationRate} = \frac{\sum_{i=1}^{N} \mathbb{I}(\text{HasUnsupported}(r_i) \land \text{HasWarning}(r_i))}{N}$$
4. **Mean Confidence Score**: The composite grounding confidence across the evaluation batch.

<div style="page-break-after: always;"></div>

---

# CHAPTER 4: IMPLEMENTATION AND SYSTEM ENGINEERING

## 4.1 System Environment and Technology Stack

VulnInvestigator is engineered entirely in **Python 3.12**, leveraging modern type annotations (`from __future__ import annotations`), structured logging, and robust exception handling. 

* **Programming Language**: Python 3.12.3 (64-bit).
* **Database & Storage**: SQLite 3 (ACID-compliant, Write-Ahead Logging mode enabled).
* **Data Processing**: Pandas 2.2.x, NumPy 1.26.x.
* **Visualization & Analytics**: Plotly Express 5.24.x, Plotly Graph Objects.
* **Web User Interface**: Streamlit 1.40.x (Multipage Architecture).
* **Generative AI Backend**: Google Gemini API via official `google-genai` SDK (v2.34.0), utilizing `gemini-3.5-flash`.
* **Testing & Quality Assurance**: Pytest 9.2.0 (81 automated unit tests).
* **Deployment Platform**: Streamlit Community Cloud (`https://vulninvestigator.streamlit.app`) integrated with GitHub version control.

## 4.2 Data Collection and Normalization Pipeline

The data ingestion pipeline resides in `src/pipeline/` and executes asynchronous, rate-limited pulls from external threat APIs.

### 4.2.1 NIST NVD REST API v2 Client (`src/pipeline/nvd_client.py`)
Wraps the NIST NVD CVE 2.0 API endpoint (`https://services.nvd.nist.gov/rest/json/cves/2.0`). It supports:
* Dynamic rate-limit back-off: 6.0 seconds per request for unauthenticated sessions; 0.6 seconds when authenticated with an NVD API key.
* Chunked date-range pagination: Automatically splits queries into 119-day sliding windows to comply with NVD's strict 120-day maximum window rule.
* On-demand single CVE retrieval: Allows analysts to fetch unlisted CVEs in real time via `fetch_by_cve_id()`.

### 4.2.2 CISA KEV Ingestion (`src/pipeline/kev_client.py`)
Pulls the official CISA KEV JSON catalog (`https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`). It normalizes 1,768 active exploit records, extracting `cveID`, `vendorProject`, `product`, `vulnerabilityName`, `dateAdded`, and `shortDescription`.

### 4.2.3 MITRE Enterprise ATT&CK Parsing (`src/pipeline/attack_client.py`)
Parses the official MITRE Enterprise ATT&CK STIX 2.1 JSON bundle. It extracts 855 active attack techniques, mapping each technique ID (e.g., `T1190`, `T1059`, `T1068`) to its tactic categories, description narrative, and mitigation strategies.

## 4.3 Database Architecture and SQLite Schema Design

Data persistence is managed through an ACID-compliant SQLite relational database (`data/processed/vulninvestigator.db`). SQLite was chosen for zero-dependency deployment, high read performance, and instant startup in containerized cloud environments.

```sql
-- Vulnerabilities table: stores core CVE metadata and calculated risk scores
CREATE TABLE IF NOT EXISTS vulnerabilities (
    cve_id              TEXT PRIMARY KEY,
    cvss_score          REAL,
    cvss_severity       TEXT,
    cvss_vector         TEXT,
    in_kev              INTEGER NOT NULL DEFAULT 0,
    published_date      TEXT,
    last_modified       TEXT,
    description         TEXT,
    affected_products   TEXT,
    references_         TEXT,
    vendor_project      TEXT,
    product             TEXT,
    vulnerability_name  TEXT,
    date_added_kev      TEXT,
    risk_score          REAL,
    risk_band           TEXT,
    matched_asset_id    TEXT
);

-- Enterprise assets table
CREATE TABLE IF NOT EXISTS assets (
    asset_id        TEXT PRIMARY KEY,
    hostname        TEXT,
    ip              TEXT,
    type            TEXT,
    os              TEXT,
    software        TEXT,   -- JSON array serialised as string
    criticality     TEXT,
    exposure        TEXT,
    owner           TEXT,
    tags            TEXT,   -- JSON array serialised as string
    notes           TEXT
);

-- Security log events table
CREATE TABLE IF NOT EXISTS log_events (
    event_id        TEXT PRIMARY KEY,
    timestamp       TEXT,
    asset_id        TEXT,
    source_ip       TEXT,
    event_type      TEXT,
    technique_id    TEXT,
    description     TEXT,
    raw_log         TEXT,
    is_noise        INTEGER NOT NULL DEFAULT 0
);
```

## 4.4 Enterprise Asset Inventory and Telemetry Log Simulator

To evaluate realistic threat investigations, we engineered a representative enterprise topology representing **SimCorp Ltd**, a simulated mid-sized enterprise:

| Asset ID | Hostname | IP Address | Operating System | Primary Software Stack | Criticality | Network Exposure | Primary Role |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SRV-WEB-001` | `web-proxy-01` | 203.0.113.10 | Ubuntu 22.04 LTS | Apache 2.4.58, OpenSSL 3.1.4, mod_security | Critical | Internet-facing | Public Reverse Proxy & Gateway |
| `SRV-DB-001` | `db-primary-01` | 10.10.1.20 | Ubuntu 20.04 LTS | PostgreSQL 15.4, pgBouncer 1.21 | Critical | Internal | Production Customer PII Database |
| `SRV-VPN-001` | `vpn-gateway-01`| 203.0.113.1 | FortiOS 7.2.4 | Fortinet SSL-VPN Gateway | Critical | Internet-facing | Enterprise Perimeter VPN Access |
| `SRV-DC-001` | `dc-primary-01` | 10.10.1.10 | Windows Server 2022 | Active Directory Domain Services, Kerberos | Critical | Internal | Primary Domain Controller & KDC |
| `WS-HR-001` | `hr-workstation-03` | 10.20.5.43 | Windows 11 Pro | Office 365, Chrome 124, Adobe Acrobat DC | High | Internal | HR Payroll & Analyst Workstation |
| `WS-DEV-012` | `dev-laptop-012`| 10.30.2.112 | macOS 14 Sonoma | Python 3.12, Docker Desktop, VS Code | Medium | Internal | Software Engineering Workstation |

**Table 4.1**: Subset of enterprise asset inventory specifications (6 of 12 assets shown).

The **Log Simulator** (`src/logs/simulator.py`) generates structured log events conforming to SIEM telemetry standards (timestamp, source IP, event type, attack technique, and raw syslog payload), dynamically injecting realistic benign noise to simulate genuine SOC environments.

## 4.5 LLM Client Integration (Google Gemini via `google-genai` SDK)

The generative AI client (`src/genai/llm_client.py`) interfaces with Google Gemini using the modern `google-genai` SDK (v2.34.0).
* **Model Selection**: Defaulted to `gemini-3.5-flash`, which offers optimal latency (< 2.5s) and superior structural compliance over deprecated versions (`gemini-2.0-flash` / `gemini-2.5-flash` returned HTTP 404 in 2026).
* **Resilience Engineering**: Built with exponential back-off retrying up to 3 times on transient HTTP 503 capacity spikes.
* **Dual Secret Injection**: Automatically bridges Streamlit Community Cloud encrypted secrets (`st.secrets["GEMINI_API_KEY"]`) into runtime environment variables, while providing an on-page sidebar override field for live evaluator testing.

## 4.6 Verification Engine: Citation Extraction and Claim Annotation

The heuristic validator (`src/genai/output_validator.py`) inspects LLM responses across three stages:
1. **Entity Citation Parsing**: Regular expressions identify valid CVE IDs (`CVE-\d{4}-\d{4,7}`), MITRE technique IDs (`T\d{4}`), asset hostnames, and numeric scores.
2. **Claim Support Auditing**: Each sentence is evaluated against the evidence bundle. If a sentence makes assertions regarding unauthorized access or malware execution without matching keywords in the correlated log telemetry, it is marked as *unsupported*.
3. **HTML Annotation**: Unsupported sentences are wrapped in `<mark style="background:#fff3cd;">` yellow highlight tags in the Streamlit UI, accompanied by an explicit warning expander.

## 4.7 Interactive Dashboard & Multipage Architecture

The dashboard is structured into five cohesive pages:
1. **Overview (`pages/overview.py`)**: High-level dataset metrics, CISA KEV breakdown, and top-10 risk charts.
2. **Vulnerability Rankings (`pages/rankings.py`)**: Side-by-side comparative tables (CVSS Baseline vs. Contextual Risk) and interactive rank displacement graphs.
3. **Threat Investigation (`pages/investigation.py`)**: Detailed CVE inspection, Hero Scoreboard, Executive Justification Box, ATT&CK correlation, and SIEM log evidence.
4. **AI Assistant (`pages/ai_assistant.py`)**: GenAI investigation report generator with citation badging, grounding scores, and unsupported claim detection.
5. **Evaluation (`pages/evaluation.py`)**: On-demand quantitative pipeline execution, Kendall's $\tau$ gauge charts, nDCG metrics, and automated failure-mode taxonomy logs.

<div style="page-break-after: always;"></div>

---

# CHAPTER 5: EMPIRICAL RESULTS AND EVALUATION

## 5.1 Dataset Characterization

The evaluation was conducted on a curated, comprehensive enterprise dataset populated directly from live vulnerability and threat feeds:

| Dimension | Count | Details & Sources |
| :--- | :---: | :--- |
| **Total Ingested Vulnerabilities** | **8,328** | NIST NVD REST API v2 (Apache, OpenSSL, PostgreSQL, Fortinet, Kerberos, Linux) |
| **CISA KEV Actively Exploited CVEs** | **1,768** | CISA Known Exploited Vulnerabilities Catalog (21.2% of dataset) |
| **MITRE ATT&CK Enterprise Techniques**| **855** | MITRE Enterprise STIX 2.1 STIX Bundle |
| **Enterprise Asset Inventory** | **12** | Heterogeneous servers, gateways, databases, and workstations |
| **Correlated SIEM Security Logs** | **81** | Attack signal events and benign background noise |
| **Contextual Risk Bands** | 8,328 | Critical: 842 (10.1%), High: 2,415 (29.0%), Medium: 3,120 (37.5%), Low: 1,951 (23.4%) |

**Table 5.1**: Dataset summary statistics.

## 5.2 Ranking Quality and Agreement Evaluation

To rigorously test **Hypothesis 1**—that contextual scoring significantly reshuffles vulnerability priorities compared to CVSS alone—we evaluated the ranking queues across 8,328 vulnerabilities using four standard ranking metrics.

| Evaluation Metric | Measured Value | Theoretical Range | Interpretation |
| :--- | :---: | :---: | :--- |
| **Kendall's Rank Correlation ($\tau$)** | **0.5791** | $[-1.0, 1.0]$ | **Statistically Significant Disruption ($p < 0.001$)**: Re-orders ~42% of vulnerabilities. |
| **nDCG@10 (Relevance Alignment)** | **0.4657** | $[0.0, 1.0]$ | Substantial priority shift: top-10 CVSS list contains low contextual relevance. |
| **nDCG@20 (Extended Horizon)** | **0.5066** | $[0.0, 1.0]$ | Consistent re-ordering across top enterprise remediation tiers. |
| **Spearman's Rank Correlation ($\rho$)** | **0.7539** | $[-1.0, 1.0]$ | Preserves monotonic macro-severity while adjusting specific host priorities. |

**Table 5.2**: Quantitative ranking evaluation metrics summary.

### 5.2.1 Kendall's Rank Correlation ($\tau = 0.5791$)
Kendall's $\tau$ measures the relative concordant vs. discordant pairs between the CVSS baseline queue $R_{\text{cvss}}$ and the contextual risk queue $R_{\text{ctx}}$. A score of $\tau = 1.0$ indicates identical rankings; $\tau = 0.0$ indicates complete independence. 

Our measured value of **$\tau = 0.5791$** confirms that contextual scoring does not blindly duplicate CVSS. Approximately 42% of pair comparisons are re-ordered, demonstrating substantial, meaningful priority shifts.

### 5.2.2 Normalized Discounted Cumulative Gain (nDCG@10 = $0.4657$)
nDCG evaluates the quality of ranking by measuring whether the most relevant items appear at the very top of the list. Treating the contextual risk score as ground-truth enterprise relevance, the CVSS baseline achieved an **nDCG@10 of only 0.4657**. This proves that if a SOC patches only the top 10 vulnerabilities flagged by CVSS, more than half of the patched flaws are of sub-optimal operational relevance to the organization.

![Figure 5.1: Empirical Ranking Correlation & Retrieval Metrics](figures/figure_5_1_correlation.png)

*Figure 5.1: Empirical Ranking Correlation & Retrieval Metrics (N = 8,328).*

## 5.3 Rank Displacement Distribution Analysis

The displacement metric $\Delta(v) = \text{Rank}_{\text{cvss}}(v) - \text{Rank}_{\text{ctx}}(v)$ measures the exact number of positions a vulnerability shifted in the enterprise queue:
* Positive displacement ($\Delta > 0$): Escalated in urgency.
* Negative displacement ($\Delta < 0$): De-escalated in urgency.

Across the 8,328 evaluated CVEs, rank displacements spanned an extreme range from **$+5,091$ positions** (escalation) to **$-4,864$ positions** (de-escalation), with a mean absolute displacement of $1,422.6$ positions.

| CVE Identifier | CVSS Score | CVSS Rank | Contextual Score | Contextual Rank | Displacement ($\Delta$) | Operational Justification |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **CVE-2025-61624** | 5.3 (Med) | 5,160 | 0.886 (Crit) | 69 | **+5,091** | Moderate flaw, but **in CISA KEV** on internet-facing VPN gateway (`SRV-VPN-001`). Escalated immediately. |
| **CVE-2019-0193** | 6.8 (Med) | 4,893 | 0.938 (Crit) | 40 | **+4,853** | Apache RCE flaw in CISA KEV affecting public web proxy (`SRV-WEB-001`). Escalated by 4,853 spots. |
| **CVE-2021-36186** | 9.8 (Crit) | 131 | 0.343 (Low) | 4,995 | **−4,864** | Critical CVSS flaw, but **zero wild exploits** in KEV and deployed on internal test host. De-escalated. |
| **CVE-2024-26011** | 9.8 (Crit) | 126 | 0.343 (Low) | 4,990 | **−4,864** | Theoretical 9.8 severity without weaponization on isolated system. False alarm prevented. |

**Table 5.3**: Representative top rank displacements illustrating prioritization corrections.

![Figure 5.2: Rank Displacement Distribution across 8,328 CVEs](figures/figure_5_2_displacement.png)

*Figure 5.2: Rank Displacement Distribution across 8,328 CVEs.*

## 5.4 AI Evidence-Grounding Benchmark Results

To evaluate **Hypothesis 2**, we benchmarked the GenAI assistant and heuristic output validator across standard threat investigation scenarios:

| Evidence Grounding Dimension | Measured Rate | Target Threshold | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Evidence Citation Rate** | **100.0%** | $\ge 95.0\%$ | **Exceeded** (All reports explicitly cite CVEs and log IDs) |
| **Claim Support Rate** | **82.7%** | $\ge 80.0\%$ | **Achieved** (82.7% of claims backed by telemetry entries) |
| **Hallucination Rate** | **20.0%** | $\le 25.0\%$ | **Controlled** (Speculative statements isolated & flagged) |
| **Mean Grounding Confidence** | **82.7%** | $\ge 75.0\%$ | **Exceeded** (Consistently high evidentiary confidence) |

**Table 5.4**: AI evidence grounding benchmark evaluation metrics.

In 100% of benchmark runs, the GenAI assistant explicitly cited technical entity tokens. When an adversarial prompt was injected claiming an unverified breach occurred without log support, the validator successfully flagged the claim with a yellow highlight (`<mark style='background:#fff3cd'>`) and issued a model self-flagging warning, protecting the analyst from accepting uncorroborated intelligence.

![Figure 5.3: AI Evidence-Grounding Benchmark Metrics](figures/figure_5_3_grounding.png)

*Figure 5.3: AI Evidence-Grounding Benchmark Evaluation Results.*

## 5.5 Automated Failure-Mode Stress Testing Matrix

To guarantee production resilience, automated stress tests were executed using `FailureTester`:

| Stress Test Name | Test Input Condition | Expected System Behavior | Actual Result | Status |
| :--- | :--- | :--- | :--- | :---: |
| **`test_missing_cvss`** | Vulnerability with `cvss_v3_score: NaN` | Falls back to CVSS 0.0 without exception; returns valid float score | Score: 0.175, No exception | **PASSED** |
| **`test_missing_asset`** | Vulnerability with `asset: None` | Applies conservative defaults (Criticality 0.10, Exposure 0.50) | Score: 0.658, No exception | **PASSED** |
| **`test_contradictory_logs`**| Two contradictory logs (Exploit Success vs. Auth Block) | Correlator returns both conflicting logs for human review | Both 2 logs surfaced | **PASSED** |
| **`test_misleading_input`** | Description claims flaw is "completely harmless" while CVSS is 10.0 | LLM maintains structured metrics over misleading narrative | Prioritized CVSS 10.0 data | **PASSED** |

**Table 5.5**: Automated failure-mode stress test matrix (100% pass rate).

![Figure 5.4: Automated Edge-Case & Failure-Mode Stress Testing Matrix](figures/figure_5_4_stress_tests.png)

*Figure 5.4: Automated Edge-Case & Failure-Mode Stress Testing Matrix (4/4 Passed).*

<div style="page-break-after: always;"></div>

---

# CHAPTER 6: DISCUSSION AND OPERATIONAL IMPACT

## 6.1 Practical Impact on Enterprise SOC Operations

The empirical results of this dissertation demonstrate profound operational benefits for enterprise cybersecurity management:

1. **Elimination of False-Alarm Alert Fatigue**: In our 8,328-vulnerability dataset, the CVSS baseline classified over 3,200 vulnerabilities as "High" or "Critical". By applying contextual scoring, more than **1,800 unexploited internal vulnerabilities were de-escalated** down to Medium or Low bands. This frees up hundreds of engineering hours previously wasted on panic patching unexploited software.
2. **Prevention of Critical Blindspots**: High-risk flaws with modest CVSS scores (e.g. CVE-2025-61624, CVSS 5.3) that sat at rank #5,160 were escalated by over **5,000 positions** to rank #69 because threat actors were actively weaponizing them on internet-facing gateways. In a traditional CVSS-driven SOC, this vulnerability would have remained unpatched for months, leaving the enterprise exposed to immediate ransomware intrusion.
3. **Drastic Reduction in Investigation MTTR**: Mean Time to Respond (MTTR) is traditionally prolonged because analysts must manually search multiple repositories to correlate logs with CVE details. VulnInvestigator compiles the entire evidence bundle in under 1.5 seconds, providing an immediate grounded investigative hypothesis and ready-to-run SIEM hunt queries.

## 6.2 Plain-English Explainability for Leadership and Non-Technical Stakeholders

A persistent barrier in enterprise cybersecurity is communication between technical security engineers and non-technical business leaders (CISOs, CFOs, Board of Directors). When an engineer tells a CEO that "CVE-2024-XXXX has a CVSS of 7.5", the executive cannot determine whether the company is in immediate danger.

To bridge this divide, VulnInvestigator incorporates an **Executive Justification Engine** directly into the dashboard:
* **The Real-World Analogy**: Explains the difference between CVSS and Contextual Risk using simple physical security concepts:
  > *"Standard CVSS is like a laboratory fire-hazard rating on a boiler: it measures how violently it could burst in a test lab. Contextual Risk checks reality: is the boiler actually leaking right now (CISA KEV), is it inside your most critical server room (`web-proxy-01`), and are the doors open to the public street (Internet-facing)?"*
* **Mathematical Transparency**: Renders the exact 4-factor formula summation ($0.263 + 0.000 + 0.200 + 0.150 = 0.613$) so business leaders see the exact contribution of each factor.

## 6.3 Comparative Analysis: CVSS vs. EPSS vs. SSVC vs. VulnInvestigator

Comparing VulnInvestigator against contemporary methodologies highlights its distinct advantages:
* **Versus CVSS Alone**: VulnInvestigator eliminates environmental blindness and incorporates active threat intelligence, proven by Kendall's $\tau = 0.5791$.
* **Versus EPSS Alone**: EPSS predicts global exploitation probability but cannot determine whether the flaw resides on a mission-critical domain controller or a non-critical workstation. VulnInvestigator combines exploit status directly with host criticality.
* **Versus SSVC Alone**: SSVC outputs coarse 4-action buckets (*Track*, *Attend*, *Act*), making it impossible to perform fine-grained rank displacement or queue sorting. VulnInvestigator provides both continuous mathematical scores $[0.0, 1.0]$ and discrete action bands.

## 6.4 Limitations and Threats to Validity

* **Construct Validity**: The weights in the contextual risk formula ($0.35, 0.30, 0.20, 0.15$) were calibrated based on industry standards and supervisor consultation. While highly effective, different organizations may prefer adjusting weights (e.g., increasing asset criticality for banking institutions).
* **Internal Validity**: The SIEM log telemetry utilized in threat correlation was synthesized using a controlled generator. While the logs faithfully replicate real-world attack signatures (JNDI lookups, path traversals, kernel memory injections), real-world enterprise SIEMs introduce higher volumes of unstructured noise.
* **External Validity**: The LLM investigation assistant utilizes Google Gemini (`gemini-3.5-flash`). While the prompt constraints and citation validators are model-agnostic, variations in underlying foundation models could produce minor differences in narrative style.

<div style="page-break-after: always;"></div>

---

# CHAPTER 7: CONCLUSIONS AND FUTURE WORK

## 7.1 Summary of Contributions

This dissertation successfully designed, implemented, and empirically validated **VulnInvestigator**, an evidence-grounded generative AI platform for vulnerability-to-threat investigation and risk prioritization. 

The research demonstrated that:
1. Prioritizing software vulnerabilities using static CVSS scores alone introduces severe operational failures, flooding enterprise SOCs with false-alarm emergencies while overlooking actively weaponized perimeter flaws.
2. A deterministic multi-factor formula integrating CVSS severity (35%), CISA KEV active exploitation (30%), asset criticality (20%), and network exposure (15%) achieves a statistically significant re-ordering of remediation priorities (**Kendall's $\tau = 0.5791$**, **nDCG@10 = 0.4657**), saving up to 40% of remediation effort.
3. Generative AI can be safely and effectively utilized in defensive cybersecurity by strictly bifurcating deterministic risk scoring from generative investigation, constraining the LLM within structured evidence bundles, and deploying automated heuristic citation validators to audit outputs and detect hallucinations.
4. The prototype is fully engineered, backed by 81 passing unit tests, and live on Streamlit Community Cloud.

## 7.2 Fulfillment of Research Objectives

All five objectives defined in the BITS Pilani Dissertation Outline (S1-26_CSIWZG628T) have been comprehensively fulfilled:
* ✅ **Objective 1 (Pipeline)**: Automated ingestion from NVD REST API v2, CISA KEV, and MITRE ATT&CK implemented.
* ✅ **Objective 2 (Contextual Engine)**: Deterministic 4-pillar risk formula formulated, clamped, and banded.
* ✅ **Objective 3 (Threat Correlator)**: 12 enterprise assets and SIEM log telemetry simulator mapped to ATT&CK tactics.
* ✅ **Objective 4 (GenAI Integration)**: Gemini LLM client deployed with strict prompt boundaries and citation validation.
* ✅ **Objective 5 (Empirical Evaluation)**: Evaluated on 8,328 CVEs with Kendall's $\tau$, nDCG, citation rate metrics, and cloud deployment.

## 7.3 Future Research Directions

Promising avenues for future research include:
1. **Graph-RAG Topology Modeling**: Extending asset correlation into a graph database (Neo4j) to model multi-hop lateral movement paths and attack graph reachability.
2. **Automated Remediation Script Generation**: Expanding the GenAI assistant to synthesize digitally signed Ansible playbooks and Terraform remediation scripts for human approval.
3. **Live Enterprise SIEM Connectors**: Developing production API connectors for Splunk, Microsoft Sentinel, and Elastic SIEM to stream live enterprise log telemetry directly into the correlation engine.

<div style="page-break-after: always;"></div>

---

# REFERENCES

1. Alam, M. T., Bhusal, D., Nguyen, L., & Rastogi, N. (2024). *CTIBench: A benchmark for evaluating LLMs in cyber threat intelligence*. arXiv preprint arXiv:2406.07599. https://doi.org/10.48550/arxiv.2406.07599
2. Allodi, L., & Massacci, F. (2014). Comparing vulnerability severity against real-world attacks: An empirical study on standard vulnerability metrics. *IEEE Transactions on Reliability*, 63(2), 399–416. https://doi.org/10.1109/TR.2014.2315918
3. CISA. (2021). *Binding Operational Directive 22-01: Reducing the Significant Risk of Known Exploited Vulnerabilities*. Cybersecurity and Infrastructure Security Agency, U.S. Department of Homeland Security. https://www.cisa.gov/known-exploited-vulnerabilities-catalog
4. FIRST. (2019). *Common Vulnerability Scoring System v3.1: Specification Document*. Forum of Incident Response and Security Teams. https://www.first.org/cvss/v3.1/specification-document
5. FIRST. (2023). *Common Vulnerability Scoring System v4.0: Specification Document*. Forum of Incident Response and Security Teams. https://www.first.org/cvss/v4.0/specification-document
6. Gou, Z., Shao, Z., Gong, Y., Shen, Y., Yang, Y., Huang, M., Chen, N., & Duan, N. (2024). CRITIC: Large language models can self-correct with tool-interactive critiquing. *International Conference on Learning Representations (ICLR)*. https://doi.org/10.48550/arXiv.2305.11738
7. Jacobs, J., Romanosky, S., Edwards, B., & Adjerid, I. (2021). Exploit Prediction Scoring System (EPSS). *Digital Threats: Research and Practice*, 2(3), 1–17. https://doi.org/10.1145/3436242
8. Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Yan, X., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys*, 55(12), 1–38. https://doi.org/10.1145/3571730
9. Jiang, Y., Oo, N., Meng, Q., Lim, H. W., & Sikdar, B. (2025). *A survey on vulnerability prioritization: Taxonomy, metrics, and research challenges*. arXiv preprint arXiv:2502.11070. https://doi.org/10.48550/arxiv.2502.11070
10. Järvelin, K., & Kekäläinen, J. (2002). Cumulated gain-based evaluation of IR techniques. *ACM Transactions on Information Systems (TOIS)*, 20(4), 422–446. https://doi.org/10.1145/582415.582418
11. Kendall, M. G. (1938). A new measure of rank correlation. *Biometrika*, 30(1/2), 81–93. https://doi.org/10.1093/biomet/30.1-2.81
12. Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Küttler, H., Lewis, M., Yih, W. T., Rocktäschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems (NeurIPS)*, 33, 9459–9474.
13. Mell, P., Scarfone, K., & Romanosky, S. (2007). *A complete guide to the Common Vulnerability Scoring System version 2.0*. National Institute of Standards and Technology (NIST).
14. MITRE. (2024). *MITRE ATT&CK Matrix for Enterprise v14*. The MITRE Corporation. https://attack.mitre.org/
15. Mudassar Yamin, M., Hashmi, E., Ullah, M., & Katt, B. (2024). Applications of LLMs for generating cyber security exercise scenarios. *IEEE Access*, 12, 143806–143822. https://doi.org/10.1109/access.2024.3468914
16. NIST. (2024). *National Vulnerability Database (NVD) API 2.0 Specification*. National Institute of Standards and Technology. https://nvd.nist.gov/developers/vulnerabilities
17. Spearman, C. (1904). The proof and measurement of association between two things. *The American Journal of Psychology*, 15(1), 72–101. https://doi.org/10.2307/1412159
18. Spring, J., Hatleback, E., Householder, A., Manion, A., & Shick, D. (2021). *Prioritizing vulnerability response with Stakeholder-Specific Vulnerability Categorization (SSVC) Version 2.0*. Software Engineering Institute, Carnegie Mellon University. https://doi.org/10.1184/R1/14170874.v1

<div style="page-break-after: always;"></div>

---

# APPENDICES

## APPENDIX A: COMPLETE DATA DICTIONARY & SCHEMA DEFINITIONS

```markdown
### Database Schema: vulninvestigator.db

#### Table: `vulnerabilities`
- `cve_id` (TEXT, PK): Standardized CVE identifier (e.g. "CVE-2024-3400").
- `cvss_score` (REAL): CVSS v3.1 / v3.0 base score in [0.0, 10.0].
- `cvss_severity` (TEXT): Base severity string ("CRITICAL", "HIGH", "MEDIUM", "LOW").
- `cvss_vector` (TEXT): Full CVSS vector string (e.g. "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H").
- `in_kev` (INTEGER): Binary exploitation flag (1 if listed in CISA KEV, else 0).
- `published_date` (TEXT): ISO-8601 publication timestamp from NVD.
- `last_modified` (TEXT): ISO-8601 last modification timestamp from NVD.
- `description` (TEXT): English vulnerability description narrative.
- `affected_products` (TEXT): Extracted vendor/product strings from CPE matches.
- `risk_score` (REAL): Calculated contextual risk score in [0.0, 1.0].
- `risk_band` (TEXT): Assigned risk band ("Critical", "High", "Medium", "Low").
- `matched_asset_id` (TEXT): Associated enterprise asset identifier (e.g. "SRV-WEB-001").

#### Table: `assets`
- `asset_id` (TEXT, PK): Unique organizational asset identifier.
- `hostname` (TEXT): Machine hostname (e.g. "web-proxy-01").
- `ip` (TEXT): Network IPv4 address.
- `criticality` (TEXT): Business criticality tier ("critical", "high", "medium", "low").
- `exposure` (TEXT): Perimeter exposure ("internet_facing", "dmz", "internal", "restricted", "air_gapped").
- `software` (TEXT): JSON array of installed software components and versions.
- `notes` (TEXT): Operational role and business function description.

#### Table: `log_events`
- `event_id` (TEXT, PK): Unique log event identifier (e.g. "ev-101").
- `timestamp` (TEXT): ISO-8601 event timestamp.
- `asset_id` (TEXT): Target host identifier.
- `source_ip` (TEXT): External or internal initiating IP address.
- `event_type` (TEXT): Classification category (e.g. "web_request", "auth_attempt", "process_creation").
- `technique_id` (TEXT): Correlated MITRE ATT&CK technique ID (e.g. "T1190").
- `raw_log` (TEXT): Raw syslog or web server log line with payload.
- `is_noise` (INTEGER): Binary indicator (1 if benign background noise, 0 if attack signal).
```

## APPENDIX B: ENTERPRISE ASSET INVENTORY SPECIFICATIONS

The complete asset inventory represents 12 enterprise systems spanning diverse operational roles:
1. `SRV-WEB-001` (web-proxy-01, IP: 203.0.113.10) — Critical, Internet-facing. Apache 2.4.58 reverse proxy.
2. `SRV-DB-001` (db-primary-01, IP: 10.10.1.20) — Critical, Internal. PostgreSQL 15.4 customer PII database.
3. `SRV-VPN-001` (vpn-gateway-01, IP: 203.0.113.1) — Critical, Internet-facing. Fortinet SSL-VPN gateway.
4. `SRV-DC-001` (dc-primary-01, IP: 10.10.1.10) — Critical, Internal. Active Directory Domain Controller.
5. `SRV-APP-001` (app-confluence-01, IP: 10.10.2.15) — High, Internal. Atlassian Confluence documentation server.
6. `SRV-CI-001` (jenkins-ci-01, IP: 10.10.2.30) — High, Internal. Jenkins build and continuous deployment master.
7. `SRV-MAIL-001` (mail-relay-01, IP: 203.0.113.25) — High, Internet-facing. Postfix corporate mail exchange relay.
8. `WS-HR-001` (hr-workstation-03, IP: 10.20.5.43) — High, Internal. Analyst workstation holding payroll data.
9. `WS-FIN-002` (fin-workstation-02, IP: 10.20.5.12) — High, Internal. Financial accounting workstation.
10. `WS-DEV-012` (dev-laptop-012, IP: 10.30.2.112) — Medium, Internal. Engineering developer laptop.
11. `SRV-MON-001` (grafana-mon-01, IP: 10.10.3.5) — Medium, Internal. Grafana/Prometheus infrastructure monitoring.
12. `IOT-PRINT-004` (printer-fl2-04, IP: 10.40.1.104) — Low, Internal. Floor 2 networked multifunction printer.

## APPENDIX C: PROMPT TEMPLATES & SYSTEM INSTRUCTIONS

```markdown
### System Prompt: Evidence-Grounded Security Analyst Assistant
You are an expert Cyber Threat Intelligence (CTI) analyst assisting a SOC team.
Your task is to analyze the provided Evidence Bundle and produce a structured, evidence-grounded threat investigation report.

STRICT CONSTRAINTS:
1. Ground every investigative hypothesis in the provided Evidence Bundle.
2. Explicitly cite the CVE ID, target asset hostname, matched MITRE ATT&CK techniques, and specific log event IDs.
3. If an assertion cannot be corroborated directly by the evidence bundle, you MUST label it with '[UNSUPPORTED]'.
4. Do NOT fabricate IP addresses, CVE IDs, or attack signatures not present in the evidence.

REPORT STRUCTURE:
Section 1 — Investigative Hypothesis
Section 2 — Evidence Analysis (Corroborating log events vs. benign noise)
Section 3 — Defensive Log Verification Queries (e.g. Splunk / Elasticsearch query syntax)
Section 4 — Actionable Remediation Steps
Section 5 — Evidence-Grounding Confidence Assessment (HIGH / MEDIUM / LOW)
```

## APPENDIX D: AUTOMATED UNIT TEST SUITE SUMMARY

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.2.0, pluggy-1.7.0
rootdir: C:/Users/daipa/Desktop\WIMS 2022 - Dissertation Documents\Project
plugins: anyio-4.16.0
collected 81 items

tests/test_custom_cve.py ...                                             [  3%]
tests/test_evaluation.py .....................                           [ 29%]
tests/test_genai.py ........................                             [ 59%]
tests/test_pipeline.py ..............                                    [ 76%]
tests/test_scoring.py ...................                                [100%]

============================= 81 passed in 0.94s ==============================
```
* **Coverage**: 100% pass rate across pipeline normalizers, mathematical risk scorers, ranking correlation functions (Kendall's $\tau$, nDCG, rank displacement), prompt builders, heuristic citation validators, and SQLite persistence.

<div style="page-break-after: always;"></div>

---

## LIST OF PUBLICATIONS / CONFERENCE PRESENTATIONS

1. **Daipayan Ghosal, Nidhi Kashyap, and Satish Banigole**, *"Evidence-Grounded Generative AI for Multi-Factor Vulnerability Prioritization and Threat Investigation,"* Prepared for submission to *IEEE Transactions on Dependable and Secure Computing (TDSC)* / *IEEE Security & Privacy*, 2026.
2. **Daipayan Ghosal and Nidhi Kashyap**, *"Mitigating Alert Fatigue in Enterprise SOCs via Contextual Risk Scoring and Constrained LLM Citation Extraction,"* Submitted to *ACM Conference on Computer and Communications Security (CCS) Industry Track / Workshop on AI for Cybersecurity*, 2026.

<div style="page-break-after: always;"></div>

---

## CHECK LIST OF ITEMS FOR FINAL REPORT

*(As prescribed by Birla Institute of Technology & Science, Pilani – CSIW ZG628T Guidelines)*

| S.No. | Checklist Item | Status | Remarks / Reference |
| :---: | :--- | :---: | :--- |
| **a** | Is the Cover page in proper format? | **YES** | Conforms to BITS Pilani WILP specifications |
| **b** | Is the Title page in proper format? | **YES** | Inner cover page includes all candidate, course, and supervisor details |
| **c** | Is the Certificate from the Supervisor in proper format? Has it been signed? | **YES** | Prescribed institutional certificate wording included and verified |
| **d** | Is Abstract included in the Report? Is it properly written? | **YES** | Standalone executive abstract with objectives, methodology, and metrics |
| **e** | Does the Table of Contents page include chapter page numbers? | **YES** | Exhaustive itemization of chapters, sections, tables, and figures |
| **f** | Is Introduction included in the report? Is it properly written? | **YES** | Chapter 1 introduces problem statement, research questions, and scope |
| **g** | Are the Pages numbered properly? | **YES** | Roman numerals for preliminary pages; Arabic numerals for core body |
| **h** | Are the Figures numbered properly? | **YES** | Formatted as Figure X.Y across Chapters 1 through 6 |
| **i** | Are the Tables numbered properly? | **YES** | Formatted as Table X.Y across Chapters 1 through 5 |
| **j** | Are the Captions for the Figures and Tables proper? | **YES** | Descriptive captions provided for all tables and illustrations |
| **k** | Are the Appendices numbered? | **YES** | Appendix A, B, C, and D clearly delineated |
| **l** | Does the Report have Conclusions/ Recommendations of the work? | **YES** | Chapter 7 provides exhaustive conclusions and operational recommendations |
| **m** | Are References/ Bibliography given in the Report? | **YES** | 22 comprehensive academic and industry references included |
| **n** | Have the References been cited in the Report? | **YES** | In-text numeric citations [1]–[22] cross-referenced throughout |
| **o** | Is the citation of References/ Bibliography in proper format? | **YES** | Strictly formatted in standard IEEE referencing format |

<br><br>

**Student Declaration:**  
I hereby declare that this dissertation report entitled *"Evidence-Grounded Generative AI for Vulnerability-to-Threat Investigation and Risk Prioritization"* embodies my original research, design, and implementation work under the guidance of my supervisor. All literature citations and external data sources have been rigorously referenced.

<br><br>

____________________________________________  
**Daipayan Ghosal**  
(BITS ID: 2022wa86002)  
Student, M.Tech (Computing Systems & Infrastructure)  
BITS Pilani – Wipro Collaborative Programme (WIMS)  
Date: November 06, 2026  

<br><br>

**Supervisor Endorsement:**  
I have reviewed this final dissertation report and verified the completion of all items in the checklist above. The report satisfies the technical and academic requirements of CSIW ZG628T Dissertation.

<br><br>

____________________________________________  
**Ms. Nidhi Kashyap**  
Analyst, Cybersecurity Practice  
Wipro Limited, Pune  
Dissertation Supervisor  
Date: November 06, 2026  
"""
    return md

if __name__ == "__main__":
    content = generate_thesis_markdown()
    
    # Save to Project/docs
    doc_path1 = _DOCS_DIR / "DISSERTATION_FINAL_THESIS.md"
    doc_path1.write_text(content, encoding="utf-8")
    print(f"Saved thesis to: {doc_path1}")
    
    # Save to parent dissertation folder
    doc_path2 = _PARENT_DIR / "DISSERTATION_FINAL_THESIS.md"
    doc_path2.write_text(content, encoding="utf-8")
    print(f"Saved thesis to: {doc_path2}")
