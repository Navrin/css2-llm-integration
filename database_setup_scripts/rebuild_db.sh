#!/bin/bash

for filename in ../database_schema/*.sql; do
  [ -e "$filename" ] || continue
  psql -p5432 "css2_llm" -U postgres -a -q -f $filename
done