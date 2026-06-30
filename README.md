# TTV Prioritisation Pipeline

## Overview
Modular pipeline for ExoClock-based transit prioritisation.

## Features
✅ Automated output loading (daily from Excoclock, run via the pipeline)
✅ Dynamic filtering (Score, Observability, Next 5 days only, TTV selection)
✅ PIRATE-aware target selection (this could be enhanced for other telescopes and locations)
✅ Interactive plotting (based on filtering selection)
✅ Observation planning support with detailed observing information
✅ Scientific explainability: details on each scoring component
✅ SVG figure export and therefore Dissertation-ready visualisations
✅ GitHub Pages deployment (automated after the data pipeline ingestion has completed

## Run
python src/main.py

## Output
CSV of ranked targets which are then displayed via the interactive Dashboard to via and analyse the information
fran-zuch.github.io/ttv-prioritisation/
