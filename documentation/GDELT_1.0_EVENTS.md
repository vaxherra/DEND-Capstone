# GDELT 1.0 Event Database

## Notice

Full information about the project could be found at [https://www.gdeltproject.org/](https://www.gdeltproject.org/). In this document GDELT 1.0. Event Database is described only to the extent it is used in the project and in a brief manner. 


## Basic information

From the source:
> The GDELT 1.0 Event Database contains over a quarter-billion records organized into a set of tab-delimited files by date. Through March 31, 2013 records are stored in monthly and yearly files by the date the event took place. Beginning with April 1, 2013, files are **created daily** and records are stored by the date the event was found in the world's news media rather than the date it occurred (97%+ of events are reported within 24 hours of happening, but a small number of events each day are past events being mentioned for the first time - if an event has been seen before it will not be included again). Files are ZIP compressed in tab delimited format, but named with a ".CSV" extension to address some software packages that will not accept .TXT or .TSV files.
> **Each morning, seven days a week**, the latest daily update is posted by 6AM EST. This file is named with the previous day's date in the format "YYYYMMDD.export.CSV.zip" (ie the morning of May 24, 2013 a new file called "20130523.export.CSV.zip" is added). UNIX or Linux users can easily set up a cronjob or other automatic scheduling processes to automatically download the latest daily update each morning and process it for watchboarding, forecasting, early warning, alert services, and other applications.
>(...)

## Event 

The GDELT database describes events. An event consists of basic fields like unique ID (`GlobalEventID`), date (`Day`), but also describes entities called **actors** and **actions**.

Usually, an event is describing an action ivoked by Actor 1 on Actor 2. Each actor has unique code, name, and many other parameters described below. Generally an event consists of two actors, but in complex or single-actor situations some of the actors might be blank of had very generic statements, like "Unidentified gunmen".

Events generally describe what Actor1 did to Actor2, and offer several mechanisms for assessing the “importance” or immediate-term “impact” of an event.

For events GDELT currently uses the CAMEO version 1.1b3 taxonomy. The details can be found in [CAMEO documentation](docs/CAMEO.Manual.1.1b3.pdf) ([link](https://www.gdeltproject.org/data/documentation/CAMEO.Manual.1.1b3.pdf)).




### Event structure
For full document structure see the official documentation in provided [PDF source in this repository](docs/GDELT-Data_Format_Codebook.pdf), or visit [GDELT documentaiton website](https://www.gdeltproject.org/data.html#documentation)

Only some headers relevant to the project at hand are documented:

#### Event ID and date attributes (some omitted for brevity)
- `GlobalEventID`. (integer): Globally unique identifier assigned to each event record that uniquely identifies it in the master dataset. GDELT specifies that **there might be some small amount of error duplicates in events**

- `SQLDATE` . (integer) date the event took place in `YYYYMMDD` format.

 

#### Actor 1 attributes (some omitted for brevity)

- `Actor1Code`. (character or factor) The complete raw CAMEO code for Actor1 (includes geographic, class, ethnic, religious, and type classes). May be blank if the system was unable to identify an Actor1

- `Actor1Name`. (character) The actual name of the Actor 1. In the case of a political leader or organization, this will be the leader’s formal name (GEORGE W BUSH, UNITED NATIONS), for a geographic match it will be either the country or capital/major city name (UNITED STATES / PARIS), and for ethnic, religious, and type matches it will reflect the root match class (KURD,CATHOLIC, POLICE OFFICER, etc). May be blank if the system was unable to identify an Actor1.

- `Actor1CountryCode`. (character or factor) The 3-character CAMEO code for the country affiliation of Actor1. May be blank if the system was unable to identify an Actor1 or determine its country affiliation (such as “UNIDENTIFIED GUNMEN”). 

- `Actor1KnownGroupCode`. (character or factor) If Actor1 is a known IGO/NGO/rebel organization (United Nations, World Bank, al-Qaeda, etc) with its own CAMEO code, this field will contain that code (i.e. might be empty).

- `Actor1EthnicCode`. (character or factor) If the source document specifies the ethnic affiliation of Actor1 and that ethnic group has a CAMEO entry, the CAMEO code is entered here.  

- `Actor1Religion1Code`. (character or factor) If the source document specifies the religious affiliation of Actor1 and that religious group has a CAMEO entry, the CAMEO code is entered here. 

- `Actor1Religion2Code`. (character or factor) If multiple religious codes are specified for Actor1 this contains the **secondary code**. Some religion entries automatically use two codes, such as Catholic, which invokes Christianity as Code1 and Catholicism as Code2

- `Actor1Type1Code`. (character or factor) The 3-character CAMEO code of the CAMEO “type” or “role” of Actor1, **if specified**. This can be a specific role such as Police Forces, Government, Military, Political Opposition, Rebels, etc, a broad role class such as Education, Elites, Media, Refugees, or organizational classes like Non-Governmental Movement. Special codes such as Moderate and Radical may refer to the operational strategy of a group.

- `Actor1Type2Code`. (character or factor) If multiple type/role codes are specified for Actor1, this returns the second code.

- `Actor1Type3Code`. (character or factor) If multiple type/role codes are specified for Actor1, this returns the third code.

#### Actor 2 attributes (some omitted for brevity)

> The fields above are repeated for Actor2. The set of fields above are repeated, but each is prefaced with “Actor2” instead of “Actor1”. The definitions and values of each field are the same as above.

#### Event action attributes
- `IsRootEvent`. (logical or binary or byte) The system codes every event found in an entire document, using an array of techniques to deference and link information together. A number of previous projects such as the ICEWS initiative have found that events occurring in the lead paragraph of a document tend to be the most “important.” This flag can therefore be used as a **proxy for the rough importance of an event** to create subsets of the event stream.

- `EventCode`. (character or factor) This is the raw CAMEO action code describing the action that Actor1 performed upon Actor2.

- `EventBaseCode`. (character or factor) CAMEO event codes are defined in a three-level taxonomy. For events at level three in the taxonomy, this yields its level two leaf root node. For example, code “0251” (“Appeal for easing of administrative sanctions”) would yield an EventBaseCode of “025” (“Appeal to yield”). This makes it possible to aggregate events at various resolutions of specificity. For events at levels two or one, this field will be set to EventCode.

- `EventRootCode`. (character or factor) Similar to EventBaseCode, this defines the root-level category the event code falls under. 

- `QuadClass`. (integer) The entire CAMEO event taxonomy is ultimately organized under four primary classifications: 
    1. Verbal Cooperation, 
    2. Material Cooperation, 
    3. Verbal Conflict, 
    4. Material Conflict. 
    
    This field specifies this primary classification for the event type, allowing analysis at the highest level of aggregation. The numeric codes in this field map to the Quad Classes as follows:
    
    `1`=Verbal Cooperation, `2`=Material Cooperation, `3`=Verbal Conflict, `4`=Material Conflict


- `GoldsteinScale`. (numeric) Each CAMEO event code is assigned a numeric score from -10 to +10, capturing the **theoretical potential impact that type of event will have on the stability of a country**. This is known as the Goldstein Scale. This field specifies the Goldstein score for each event type. NOTE: this score is **based on the type of event**, not the specifics of the actual event record being recorded – thus two riots, one with 10 people and one with 10,000, will both
receive the same Goldstein score. This can be aggregated to various levels of time resolution to yield an approximation of the stability of a location over time.

- `NumMentions`. (integer) This is the total number of mentions of this event across all source documents. Multiple references to an event within a single document also contribute to this count. This can be used as a method of assessing the **“importance” of an event**: the more discussion of that event, the more likely it is to be significant. 

    The total universe of source documents and the density of events within them vary over time, so it is recommended that this field be normalized by the average or other measure of the universe of events during the time period of interest. 

    NOTE: this **field is updated over time** if news articles published later discuss this event (for example, in the weeks after a major bombing there will likely be numerous news articles published mentioning the original bombing as context to new developments, while on the one-year anniversary there will likely be further coverage). 
    
    At this time the daily event stream only includes new event records found each day and does not include these updates; a special “updates” stream will be released in Fall 2013 that will include these.


- `NumSources`. (integer) This is the total number of information sources containing one or more mentions of this event. This can be used as a method of assessing the **“importance” of an event**: the more discussion of that event, the more likely it is to be significant. The total universe of sources varies over time, so it is recommended that this field be normalized by the average or
other measure of the universe of events during the time period of interest. NOTE: same as with `NumMentions`, this field is updated over time to reflect subsequent coverage of the event. Similarly, these updates are not included in the daily event stream, but will be incorporated into a new “updates” stream to be released in Fall 2013.

- `NumArticles` (integer) This is the total number of source documents containing one or more mentions of this event. This can be used as a method of assessing the **“importance” of an event**: the more discussion of that event, the more likely it is to be significant. The total universe of source documents varies over time, so it is recommended that this field be normalized by the average or other measure of the universe of events during the time period of interest. NOTE:
same as with `NumMentions`, this field is updated over time to reflect subsequent coverage of the event, but these updates are not currently part of the daily event stream.

- `AvgTone`. (numeric) This is the average “tone” of all documents containing one or more mentions of this event. The score ranges from -100 (extremely negative) to +100 (extremely positive). Common values range between -10 and +10, with 0 indicating neutral. This can be used as a method of **filtering the “context” of events** as a subtle measure of the importance of an event and as **a proxy for the “impact” of that event**. For example, a riot event with a slightly
negative average tone is likely to have been a minor occurrence, whereas if it had an extremely negative average tone, it suggests a far more serious occurrence. A riot with a positive score likely suggests a very minor occurrence described in the context of a more positive narrative (such as a report of an attack occurring in a discussion of improving conditions on the ground in a country and how the number of attacks per day has been greatly reduced).



#### Event geography

The georeferenced location for an actor may not always match the Actor1_CountryCode or Actor2_CountryCode field, such as in a case where the President of Russia is visiting Washington, DC in the United States, in which case the Actor1_CountryCode would contain the code for Russia, while the georeferencing fields below would contain a match for Washington, DC. 

It may not always be possible for the system to locate a match for each actor or location, in which case one or more of the fields **may be blank**.

To find all events located in or relating to a specific city or geographic landmark, the `Geo_FeatureID` column should be used, rather than the `Geo_Fullname column`.

**Headers**:

- `Actor1Geo_Type`. (integer) This field specifies the geographic resolution of the match type and holds one of the following values: 
    `1`=COUNTRY (match was at the country level), 
    `2`=USSTATE (match was to a US state), 
    `3`=USCITY (match was to a US city or landmark),
    `4`=WORLDCITY (match was to a city or landmark outside the US), 
    `5`=WORLDSTATE (match was to an Administrative Division 1 outside the US – roughly equivalent to a US state). 
    
    This can be used to filter events by geographic specificity, for example, extracting only those events with a landmark-level geographic resolution for mapping. Note that matches with codes 1 (COUNTRY), 2 (USSTATE), and 5 (WORLDSTATE) will still provide a latitude/longitude pair, which will be the centroid of that country or state, but the FeatureID field below will be blank.

- `Actor1Geo_Fullname`. (character) This is the full human-readable name of the matched location. In the case of a country it is simply the country name. For US and World states it is in the format of “State, Country Name”, while for all other matches it is in the format of “City/Landmark, State, Country”. This can be used to label locations when placing events on a map. NOTE: this field reflects the precise name used to refer to the location in the text itself, meaning it may contain multiple spellings of the same location – use the `FeatureID` column to
determine whether two location names refer to the same place.

- `Actor1Geo_CountryCode`. (character) This is the 2-character FIPS10-4 country code for the location.

- `Actor1Geo_ADM1Code`. (character) This is the 2-character FIPS10-4 country code followed by the 2-character FIPS10-4 administrative division 1 (ADM1) code for the administrative division housing the landmark. In the case of the United States, this is the 2-character shortform of the state’s name (such as “TX” for Texas).

- `Actor1Geo_Lat`. (numeric) This is the centroid latitude of the landmark for mapping.

- `Actor1Geo_Long`. (numeric) This is the centroid longitude of the landmark for mapping.

- `Actor1Geo_FeatureID`. (~~signed integer~~ **character**: upon manual inspection it turned out that this column contains sometimes string, and the official documentation is invalid for this field) This is the GNS or GNIS FeatureID for this location. More information on these values can be found in [Leetaru 2012](http://www.dlib.org/dlib/september12/leetaru/09leetaru.html).NOTE: This field will be blank except when Actor1Geo_Type has a value of 3 or 4. A small percentage of small cities and towns may have a blank value in this field even for Actor1Geo_Type values of 3 or 4: this will be corrected in the 2.0 release of GDELT. NOTE: This field can contain both positive and negative numbers, see [Leetaru 2012](http://www.dlib.org/dlib/september12/leetaru/09leetaru.html) for more information on this.

     
> **These codes are repeated for Actor2 and Action, using those prefixes.**

#### Data management tools

- `DATEADDED`. (integer) This field stores the date the event was added to the master database.

- `SOURCEURL`. (character) This field is only present in the daily event stream files beginning April 1, 2013 and lists the URL of the news article the event was found in. If the event was found in an article from the BBC Monitoring service, this field will contain “BBC Monitoring.” If an event was mentioned in multiple articles, only one of the URLs is provided. This field is not present in
event files prior to April 1, 2013.
