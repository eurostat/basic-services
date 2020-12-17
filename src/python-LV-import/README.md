Latvian education data comes from Latvian State Education Information System
(Valsts izglītības informācijas sistēma).
It consists of detailed data (incl. school capacities) on pre-scholl, primary, secondary, tertiary
and post-(secondary/tertiary) education which is updated daily.

# Sources
## Source 1
The public search page https://viis.lv/Pages/Institutions/Search.aspx provides all types of education but lacks of capacities.
## Sources 2 and 3
Latvian Ministry of Education publishes yearly the pre-school and primary/secondary extracts
(most probably from the same information system) with capacities
(adjust school year, at the moment of writing it was 20202021)
https://www.izm.gov.lv/lv/20202021mg

# Download instructions
## Source 1
https://viis.lv/Pages/Institutions/Search.aspx
1) select "Nē" in the listbox "Likvidēta" - excludes expired institutions
2) select all items in the listbox Pakļautība (Ownership/Subordination)
3) click on "Meklēt un eksportēt uz CSV" in right bottom corner (search and export to CSV)
4) save as 2020-all-no-capacity.txt (vertical-bar-separated)
Size: ~ 2700 records.

## Sources 2 and 3
https://www.izm.gov.lv/lv/20202021mg
Direct download links for school year 2020/2021
- pre-school: https://www.izm.gov.lv/lv/media/4957/download
1) download and open
2) extract manually the table with headers starting on row 4
3) save as CSV with name 2020-primary-secondary.csv
Size: ~ 700 records.
- primary/secondary: https://www.izm.gov.lv/lv/media/4954/download
1) download and open
2) extract manually the table with headers starting on row 4
3) save as CSV with name 2020-pre-school.csv
Size: ~ 650 records.

# Run
The processing can be run with one command ```process.bat``` provided input files are downloaded (instructions above) and mapping between input and output files has been properly configured (see below).

# Run preparation
Data extraction from the sources is based on mapping configuration files <source-name>.json. Each field in the final LV.csv file is represented in the configuration file as (example for field "id")
```json
"id": {
  "mapping-name": "Reģistrācijas numurs"
}
```
Things supported by mapping configuration:
- copy field content from different input field: ```"mapping-name": "<different-name>"```
- find corresponding value for list of input values: ```"private": ["Komercsabiedrība","Nodibinājums"]```
- fill with a constant ```"default": "LV"```
- fill with the current date ```"default": "current-date"```
- declare field as temporary ```"temporary": true```; such field will exist during the processing and will be kept in the cache between consecutive runs, but will not go to final file. It is a good way to keep geocoding results between consecutive runs so not wasting geocoder capacity.

# Cache
Processing builds a cache in the subdirectory ./cache. Each record from the sources becomes a separate file <id>.json. If the same id is found in > 1 source, information in the file is updated with the most complete and latest values.

Geocoding is done only once, saved to the cache and reused on subsequent updates.

---
# References
* General rules: https://webgate.ec.europa.eu/CITnet/confluence/pages/viewpage.action?spaceKey=GISCO&title=Basic+services+mapping
* Processing instructions: https://webgate.ec.europa.eu/fpfis/wikis/pages/viewpage.action?spaceKey=GISCO&title=Education+services+in+Europe
* Validation instructions: https://webgate.ec.europa.eu/CITnet/confluence/display/GISCO/How+to+use+the+Java+validation+procedure
https://priv-bx-myremote.tech.ec.europa.eu/CITnet/confluence/display/GISCO/,DanaInfo=.awfdjeykGmlJp6424qQwB,SSL+Basic+services+mapping
* Validation Java package: https://github.com/eurostat/basic-services/tree/master/src/gisco_java/src/main/java/eu/europa/ec/eurostat/basicservices/education
