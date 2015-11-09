#!/bin/sh

if [ -z "$2" ]
then
  echo "Usage: $0 <site.params> <panorama.tif>"
  echo "Import a panorama into the Django database."
  exit
fi

param_file="$1"
pano_file="$2"

for file in "$param_file" "$pano_file"
do
  if [ ! -f "$file" ]
  then
    echo "Error: file '$file' not found"
    exit
  fi
done

DIRNAME="$(dirname $0)"

php "$DIRNAME"/export_single_pano.php "$param_file" | "$DIRNAME"/../manage.py import_single_pano "$pano_file"
