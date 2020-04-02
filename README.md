# DEND-Capstone
Udacity Data Engineering Capstone Project.

The main goal of the project is to ..


# Project Info

## 1. Project environment

Install required conda environment: `conda env create -f env/environment.yml`

Activate environment: `conda activate DEND`

Whenever updating conda environment, export it after changes with `conda env export > env/environment.yml`.



## 2. Data sources  


	- https://github.com/curran/data
	- https://www.gdeltproject.org/data.html#rawdatafiles
	- CAMEO database (EVENT CAMEO Actor Code Lookups): https://www.gdeltproject.org/data.html#documentation


TODO: brief documentation for data sources can be found in the `documentation` folder. 

## 3. Design goals & requirements


- `GoldsteinScale`  an approximation of the stability of a location over time.
- `NumMentions` Identify importance of an event:
	over time analysis:
	- diminishing events
	- emerging events
	- with `AvgTone`: positive and negative
- 

## 4. Data modelling
TODO

## 5. Infrastructure

Graph on https://app.cloudcraft.co/
<img src="documentation/imgs/DENDArchitecture.png" width="600">

1. `EC2` compute instance is running an **Apache Airflow** for automated set of tasks related to:
	- data transfer from data sources into a data lake (S3 bucket)
	- data quality checks
	- data staging in temporary staging tables on AWS Redshift
	- data modelling in set of dimensional tables on AWS Redshift
	- storing logs to a separate S3 bucket

2. `AWS Redshift` serving as a data warehouse for modelled data, 

3. `AWS EMR` serving as a service for internal analytics team, with connections both to Data Lake on `S3` and `AWS Redshift` data warehouse.
 

## 6. Analytics support
TODO

---

# Project Structure

TODO: insert a tree view of the project structure:


## Environment

Recreate conda environment with
`conda env create -f env/environment.yml`

## Notebooks

- `Raw data placement`
- `IaC.ipynb` infrastructure as code
- 

## AIRFLOW

TODO: 


