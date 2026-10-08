# Rule: CO4031 Telecom DSS Project Requirements & Academic Guidelines

Every assistant interaction in this workspace MUST follow these requirements:
1. **Academic Alignment (CO4031 - HCMUT)**:
   - Data Warehouse: Follow Inmon's 3-tier architecture (Staging -> EDW -> Data Marts/Views).
   - Dimensional Modeling: Grain at atomic level, Star Schema, always use auto-increment/surrogate keys for dimension tables.
   - ETL Pipeline: Extract from heterogeneous sources/staging, Transform (cleansing, standardizing, business rules), Load (Dim first, FK lookup, Fact).
   - Machine Learning: 3 mandatory models (Classification for Churn, K-Means Clustering for Segmentation, Regression for CLV/Billing). ML MUST only consume cleaned SQL Views/Data Marts produced by DW.
   - DSS Interface: Dashboard (Streamlit/FastAPI) supporting OLAP operations (Drill-down, Roll-up, Slice, Dice) and What-If Analysis for decision makers.
2. **Handoff Sequence**: Data Engineer Agent -> ML Engineer Agent -> Backend/Dashboard Agent.
3. **Deadlines & Deliverables**:
   - Deadline: 23:59 on 15/11/2026.
   - Final ZIP format: `Report.pdf`, `src/`, `data/`, `Slides.pdf`, Video Presentation Link.
