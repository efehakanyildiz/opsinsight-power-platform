# OpsInsight — Future Improvements (V2+)

**Version:** 1.0  
**Status:** Documented — NOT implemented in V1  

---

## V2 Enhancements

### V2.1 — Microsoft Teams Integration

**Feature:** Native Teams notifications via Adaptive Cards  
**Benefit:** Agents and managers receive rich interactive cards directly in Teams  
**Implementation:**
- Power Automate Teams connector (Post adaptive card to channel)
- Adaptive Card format for escalation and SLA alerts
- Action buttons directly in card (Accept, Transfer, Resolve)

**Complexity:** Medium  
**Cost:** Free (Teams is included in M365)

---

### V2.2 — Business-Hours-Aware SLA Calculation

**Feature:** SLA calculations based on working hours only (Mon-Fri, 09:00-18:00)  
**Benefit:** Fairer SLA measurement — excludes nights and weekends  
**Implementation:**
- Holiday calendar table in Dataverse
- Business hours calculator function in Power Automate
- Modified SLA deadline calculation on issue creation

**V1 Approach:** Calendar time (simpler, documented as limitation)  
**Complexity:** High  
**Rationale for V1 skip:** Adds 3–4 weeks of development for marginal demo value

---

### V2.3 — Advanced Approval Workflow

**Feature:** Structured approval process integrated into issue lifecycle  
**Benefit:** Finance and Procurement approval steps become trackable events  
**Implementation:**
- Power Automate approval action (built-in)
- Approval request sent to designated approver
- Auto-status change to "Waiting" when approval pending
- Auto-resume to "In Progress" when approved
- Full history trail of approval decision + timestamp

---

### V2.4 — Microsoft Outlook Integration

**Feature:** Reply to email notifications updates issue status  
**Benefit:** Agents can update issues without leaving email client  
**Implementation:** Custom connector or Power Automate Outlook trigger

---

### V2.5 — Multi-Company Architecture

**Feature:** Multiple organizations/business units in single platform  
**Benefit:** Suitable for shared-services or holding-company model  
**Implementation:**
- Company dimension table
- All queries filtered by CompanyId
- Cross-company reporting for group management

---

## V3 Enhancements

### V3.1 — Microsoft Fabric Integration

**Feature:** Dataverse → Microsoft Fabric Lakehouse for large-scale analytics  
**Benefit:** Enables historical analysis at millions-of-events scale  
**Implementation:**
- Dataverse → Fabric link (native, no ETL)
- OneLake as analytical storage
- Power BI DirectLake mode for real-time large queries

**Current Scale:** 2,000 issues (Power BI Import mode is adequate)  
**Target Scale:** 500,000+ issues over several years

---

### V3.2 — Copilot Studio Integration

**Feature:** Natural language query interface for operational data  
**Benefit:** Managers ask questions in plain English: "Which team had the most SLA breaches last month?"  
**Implementation:** Copilot Studio bot connected to Power BI semantic model

---

### V3.3 — Predictive SLA Risk

**Feature:** ML model predicts probability of SLA breach at issue creation  
**Benefit:** Proactive intervention before issues become critical  
**Implementation:**
- Azure ML (if budget permits) or simple heuristic rules
- Feature set: category, priority, department, current team workload
- Risk score displayed on Team Queue

**V1 Decision:** Transparent business rules are more appropriate and more trustworthy at V1 scale  
**V3 Trigger:** When historical dataset exceeds 50,000 issues

---

### V3.4 — External Customer Portal

**Feature:** External customers can submit and track issues  
**Benefit:** Extends operational transparency beyond internal teams  
**Implementation:** Power Pages (low-code external portal)

---

## Architecture Evolution

```
V1 (Current):
Users → Power Apps → Dataverse → Power Automate → Power BI

V2:
Users → Power Apps + Teams + Outlook → Dataverse → Power Automate → Power BI
                                         ↑
                              Advanced SLA + Approvals

V3:
Users → Omnichannel → Dataverse → Fabric Lakehouse → Power BI Premium
                          ↓
                    Copilot Studio NL interface
```

---

## What Was Intentionally Excluded from V1

| Feature | Reason for Exclusion |
|---------|---------------------|
| Machine learning | Transparent rules more appropriate at V1 scale |
| Microsoft Fabric | Overengineered for 2,000 issues |
| Customer portal | Out of scope (internal platform only) |
| Multi-tenant architecture | Not needed for single-org demo |
| AI chatbot | Not aligned with core platform value proposition |
| Microservices | Massively overengineered for this problem |
| ServiceNow clone | Too broad — focus on process intelligence, not ITSM |

The platform's value comes from **data modelling, process automation, and analytics** — not from feature volume.
