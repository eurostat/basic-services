REM For clean processing uncomment next line. All cached data will be cleaned, geocoding will be done anew.
REM del .\cache\*.*
python ./src/process.py .\samples\2020-all-no-capacity.txt "|"
python ./src/process.py .\samples\2020-primary-secondary.csv ","
python ./src/process.py .\samples\2020-pre-school.csv ","
