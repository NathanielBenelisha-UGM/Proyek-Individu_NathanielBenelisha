# Paper — Frequency-Constrained Unit Commitment with Multi-Source Virtual Inertia

## Status: DRAFT v0.1 (30 August 2026)

## Target Journal
IEEE Access (Q1, IF ~3.9) or Energies (MDPI, Q2)

## File Structure
- main.tex          — Full LaTeX paper (IEEEtran journal format)
- 
eferences.bib    — BibTeX references (to be created)
- igures/          — Figures directory (to be populated after simulation)

## How to Compile
`ash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
`
Requires: IEEEtran.cls, amsmath, booktabs, xcolor, graphicx

## Placeholder Tags
All \RESULT{TAG} entries (shown in RED in PDF) must be replaced
with actual simulation values after running the FCUC model.

## Paper Structure
1. Introduction (motivation, literature, contributions)
2. System Modeling (SG, BESS, Solar PV, Wind, SFR model)
3. FCUC Formulation (objective, UC constraints, BESS, IBR, frequency constraints)
4. Case Study (IEEE 10-unit + IBR, 7 scenarios)
5. Results (nadir validation, S0-S6 comparison, economic analysis)
6. Conclusion

## Simulation Scenarios
| ID | Description | IBR% |
|----|-------------|------|
| S0 | Classical UC | 0% |
| S1 | FCUC SG-only | 0% |
| S2 | FCUC + BESS VI | 40% |
| S3 | FCUC + BESS+Wind VI | 40% |
| S4 | **Proposed**: BESS+Wind+Solar VI | 40% |
| S5 | Proposed at 60% IBR | 60% |
| S6 | Proposed at 80% IBR | 80% |
