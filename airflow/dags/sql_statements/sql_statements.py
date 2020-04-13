# COPY GZIP from S3>Redshift
# ref: https://docs.aws.amazon.com/redshift/latest/dg/t_loading-gzip-compressed-data-files-from-S3.html

# File in GDELT don't contain headers, so don't skip, i.e. skip 0 headers
COPY_SQL_GZIP = """
COPY {}
FROM '{}'
ACCESS_KEY_ID '{}'
SECRET_ACCESS_KEY '{}'
IGNOREHEADER 0
DELIMITER '\t' GZIP
"""

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

### GNIS database:
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