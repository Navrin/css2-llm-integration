#!/bin/bash

for filename in ../database_schema/*.sql; do
  [ -e "$filename" ] || continue;
  [[ "$filename" =~ '99-copy-all' ]]  && continue; # skip the copy all
  psql -p5432 $DB_NAME -U $DB_USER -a -q -f $filename
done

for filename in ../example_data/*.csv; do
  [ -e "$filename" ] || continue;
  set -e
  table=$(echo "$filename" | cut -d '/' -f 3 | cut -d '-' -f 2 | cut -d '.' -f 1);
  echo "$table"

  psql -v ON_ERROR_STOP=1 -p5432 $DB_NAME -U $DB_USER  -c "\copy $table FROM '$filename' WITH (FORMAT csv, DELIMITER ',', HEADER MATCH, DEFAULT '<>');";

done