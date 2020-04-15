# DEND-Capstone
Udacity Data Engineering Capstone Project.

The main goal of the project is to ..


# Project Info

## 1. Project environment


## Conda
Install required conda environment: `conda env create -f env/environment.yml`

Activate environment: `conda activate DEND`

Whenever updating conda environment, export it after changes with `conda env export > env/environment.yml`.

## Environmental variables

From the **main repository directory, type:"

>  ```export AIRFLOW_HOME=$(pwd)/airflow```


## 2. Data sources  

TODO: delete
gdelt hooks: 
- date
- location
- country code (2 characters)
		https://www.geodatasource.com/resources/tutorials/international-country-code-fips-versus-iso-3166/

- GNIS/GNS ID from ActionGeo_FeatureID
		https://www.usgs.gov/core-science-systems/ngp/board-on-geographic-names/download-gnis-data




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

- geographic region selected by latitude and longitude
- 
## 4. Data pipelines

In order to run Airflow data pipelines, switch to `/airflow` folder from the main repository, and export environmental variable `export AIRFLOW_HOME=$(pwd)`, then it is possible to start the scheduler by running `airflow scheduler` and/or a webserver on a `8080` port: `airflow webserver -p 8080`.

**Note:** that the Web UI currently only runs in UTC timezone, and is the standard default.


### GDELT data stream

TODO: implement dynamic schedule interval
Data pipeline for GDELT stream is published based on EST time-zone, which: UTC-4=EST **or** EST-5=EST, depending on the daylight savings time. In order to deliver the data as fast as possible, and avoid time-zone hardships, pipeline performs dynamic date conversion from EST to UTC, as `schedule_interval` depends on a variable. 


TODO:
	Apache airflow defines `GDELT_stream` for handling a daily influx of event data from GDELT database. For brief overview of the database see: `documentation/GDELT_1.0_EVENTS.md`. 

	The GDELT stream is updated **daily** at 6AM EST or the previous day. The main tasks of this pipeline:

	- download the raw data stream on a regular basis (6:15 EST each day) and push it to AWS S3 bucket,

	- perform automatic set of data quality checks

	- insert data into star-schema on AWS Redshift
 
## 5. Data modelling
TODO

## 6. Infrastructure

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
 

## 7. Analytics support
TODO

---

# 8. Project Structure

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


