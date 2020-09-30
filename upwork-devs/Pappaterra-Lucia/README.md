# Organization Chart Visualization


Jupyter-Notebook Org_Chart_Vis.pynb generates visualizations from the sheets in 

https://docs.google.com/spreadsheets/d/1GCDWsyRc2CIkunovZ2-zZaqOdaienEBy/view

that are constantly being updated. 

Jupyter-Notebook Make_PowerPoint_Presentation.pynb autocreate power point presentation
for 'Project Team Structure' sheet.

Easy to consume outputs are save in *outputs* folder.

Before running those two notebooks, it's necessary to generate csv and yaml files from 
spreadsheets latest version. To do so Jupyter-Notebook Generate_files.ipynb must be run.

This generates the required files that will be saved in the folders *csv_files* 
and *yaml_files* respectively, for later use in updated visualizations. 

*csv_files* and *yam_files* folders must be created locally since they 
may contain sensitive information.


# Pull Request Report

Create a PR report for all current projects. Name, link, reviewers and creation 
date of each PR are listed.