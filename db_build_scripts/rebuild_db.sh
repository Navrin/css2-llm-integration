#!/bin/bash

for filename in ../database_schema/*.sql; do
  [ -e "$filename" ] || continue
  psql -p5432 $DB_NAME -U $DB_USER -a -q -f $filename
done