CREATE TABLE  IF NOT EXISTS public.staging_gdelt_events (
/* EVENTID AND DATE ATTRIBUTES */
GLOBALEVENTID                   PRIMARY KEY INTEGER,
SQLDATE                         INTEGER NOT NULL,
MonthYear                       INTEGER,
Year                            INTEGER,
FractionDate                    NUMERIC,

/* ACTOR ATTRIBUTES */
Actor1Code                      VARCHAR(20),                
Actor1Name                      VARCHAR(256),
Actor1CountryCode               VARCHAR(20),
Actor1KnownGroupCode            VARCHAR(20),
Actor1EthnicCode                VARCHAR(20),
Actor1Religion1Code             VARCHAR(20),
Actor1Religion2Code             VARCHAR(20),
Actor1Type1Code                 VARCHAR(20),
Actor1Type2Code                 VARCHAR(20),
Actor1Type3Code                 VARCHAR(20),
Actor2Code                      VARCHAR(20),
Actor2Name                      VARCHAR(256),
Actor2CountryCode               VARCHAR(20),
Actor2KnownGroupCode            VARCHAR(20),
Actor2EthnicCode                VARCHAR(20),
Actor2Religion1Code             VARCHAR(20),
Actor2Religion2Code             VARCHAR(20),
Actor2Type1Code                 VARCHAR(20),
Actor2Type2Code                 VARCHAR(20),
Actor2Type3Code                 VARCHAR(20),

/* EVENT ACTION ATTRIBUTES */
IsRootEvent                     BOOLEAN,
EventCode                       VARCHAR(20),
EventBaseCode                   VARCHAR(20),
EventRootCode                   VARCHAR(20),
QuadClass                       INTEGER,
GoldsteinScale                  NUMERIC,
NumMentions                     INTEGER,
NumSources                      INTEGER,
NumArticles                     INTEGER,
AvgTone                         NUMERIC,

/* EVENT GEOGRAPHY */
Actor1Geo_Type                  INTEGER,           
Actor1Geo_FullName              VARCHAR(256),
Actor1Geo_CountryCode           VARCHAR(20),           
Actor1Geo_ADM1Code              VARCHAR(20),
Actor1Geo_Lat                   NUMERIC,
Actor1Geo_Long                  NUMERIC,
Actor1Geo_FeatureID             INTEGER,

Actor2Geo_Type                  INTEGER,
Actor2Geo_FullName              VARCHAR(256),
Actor2Geo_CountryCode           VARCHAR(20),
Actor2Geo_ADM1Code              VARCHAR(20),
Actor2Geo_Lat                   NUMERIC,
Actor2Geo_Long                  NUMERIC,
Actor2Geo_FeatureID             INTEGER,

ActionGeo_Type                  INTEGER,
ActionGeo_FullName              VARCHAR(256),
ActionGeo_CountryCode           VARCHAR(20),
ActionGeo_ADM1Code              VARCHAR(20),
ActionGeo_Lat                   NUMERIC,
ActionGeo_Long                  NUMERIC,
ActionGeo_FeatureID             INTEGER,

DATEADDED                       INTEGER,
SOURCEURL                       VARCHAR(1024)

);