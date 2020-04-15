
##########################################
############## GDELT STREAM ##############
##########################################

# File in GDELT don't contain headers, so don't skip, i.e. skip 0 headers
# COPY GZIP from S3>Redshift
# ref: https://docs.aws.amazon.com/redshift/latest/dg/t_loading-gzip-compressed-data-files-from-S3.html

COPY_SQL_GZIP = """
COPY {}
FROM '{}'
ACCESS_KEY_ID '{}'
SECRET_ACCESS_KEY '{}'
IGNOREHEADER 0
DELIMITER '\t' GZIP
DATEFORMAT AS 'YYYYMMDD'
"""

gdelt_fact_columns = """GLOBALEVENTID,SQLDATE,Actor1Code,Actor1Name,Actor1CountryCode,Actor2Code,Actor2Name,Actor2CountryCode,GoldsteinScale,NumMentions,NumSources,NumArticles,AvgTone,Actor1Geo_Type,Actor1Geo_FullName,Actor1Geo_CountryCode,Actor1Geo_Lat,Actor1Geo_Long,Actor1Geo_FeatureID,Actor2Geo_Type,Actor2Geo_FullName,Actor2Geo_CountryCode,Actor2Geo_Lat,Actor2Geo_Long,Actor2Geo_FeatureID,ActionGeo_Type,ActionGeo_FullName,ActionGeo_CountryCode,ActionGeo_Lat,ActionGeo_Long,ActionGeo_FeatureID,DATEADDED,SOURCEURL"""


gdelt_events_table_insert = """
SELECT {}
FROM staging_gdelt_events s
WHERE NOT EXISTS (
    select 1 from gdelt_events g where g.GLOBALEVENTID = s.GLOBALEVENTID and g.SQLDATE = s.SQLDATE
)   
""".format(gdelt_fact_columns )
 


gdelt_check_nulls = ("""
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE   (GLOBALEVENTID          IS NULL OR
                SQLDATE        IS NULL) AND
                sqldate='{{ds}}' ;
    """)

gdelt_num_records = ("""
        SELECT COUNT(*)
        FROM gdelt_events
        WHERE sqldate='{{ds}}';
    """)


##########################################
############## GNIS DATABASE #############
##########################################

# COPY SQL STATEMENT for GNIS
COPY_SQL = """
COPY {}
FROM '{}'
ACCESS_KEY_ID '{}'
SECRET_ACCESS_KEY '{}'
IGNOREHEADER 1
DELIMITER '|' 
DATEFORMAT AS 'MM/DD/YYYY'
"""

# Selects distinctly specified columns in gnis_staging not already present in gnis dimension table
# This helps with:
# - avoiding duplicate entries
# - adding future new entries, if GNIS database is re-released, but keeping old definitions for potentially updated entries
gnis_table_insert = ("""
    SELECT distinct FEATURE_ID, FEATURE_NAME, FEATURE_CLASS, STATE_ALPHA, COUNTY_NAME, PRIMARY_LAT_DMS, PRIM_LONG_DMS, ELEV_IN_M, MAP_NAME, DATE_CREATED, DATE_EDITED
    FROM gnis_staging
    WHERE FEATURE_ID NOT IN (SELECT DISTINCT FEATURE_ID from gnis ) 
""")

gnis_check_nulls = ("""
        SELECT COUNT(*)
        FROM gnis
        WHERE   FEATURE_ID          IS NULL OR
                FEATURE_NAME        IS NULL OR
                FEATURE_CLASS       IS NULL;
    """)

gnis_num_records = ("""
        SELECT COUNT(*)
        FROM gnis
    """)