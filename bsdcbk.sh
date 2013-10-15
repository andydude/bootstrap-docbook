#!/bin/bash
FILE="$1"
BASE=$(basename "$FILE" .dbk)
APP_DIR=$(dirname $0)
HTML_DIR="$APP_DIR/templates"
TEMP_DIR=$(mktemp -dt bootstrap-docbook)
DOCBOOK_XSLT=/opt/local/share/xsl/docbook-xsl/html/docbook.xsl

echo "-- Using $TEMP_DIR for temporary files"

# step 1: check filename extension
EXT=$(echo "$FILE" | cut -d'.' -f2)
if [ x"$EXT" != x"dbk" ]; then
    echo "$0: ERROR: filename must end in .dbk, but it doesn't"
    exit 1
fi

# scribble produces ${BASE}.html
xsltproc "${DOCBOOK_XSLT}" "${BASE}.dbk" > "${TEMP_DIR}/${BASE}.1.html"
if [ $? -ne 0 ]; then
    echo "$0: ERROR: xsltproc didn't like the input"
    exit $?
fi
iconv -f ISO-8859-1 -t UTF-8 "${TEMP_DIR}/${BASE}.1.html" > "${TEMP_DIR}/${BASE}.2.html"

xmllint --html "${TEMP_DIR}/${BASE}.2.html" --xmlout --dropdtd > "${TEMP_DIR}/${BASE}.3.html"
#tidy -asxhtml "${TEMP_DIR}/${BASE}.2.html" > "${TEMP_DIR}/${BASE}.3.html"
if [ $? -ne 0 ]; then
    echo "$0: ERROR: xmllint didn't like the input"
    exit $?
fi
tail -n +2 "${TEMP_DIR}/${BASE}.3.html" > "${TEMP_DIR}/${BASE}.4.html"

python "${APP_DIR}/bsdcbk.py" "${TEMP_DIR}/${BASE}.4.html" > "${TEMP_DIR}/${BASE}.5.html"
if [ $? -ne 0 ]; then
    echo "$0: ERROR: python's ElementTree didn't like the input"
    exit $?
fi

cat "${HTML_DIR}/header-sample.html" "${TEMP_DIR}/${BASE}.5.html" "${HTML_DIR}/footer-sample.html" > "${TEMP_DIR}/${BASE}.6.html"

xmllint --html --htmlout --pretty 2 "${TEMP_DIR}/${BASE}.6.html" > "${TEMP_DIR}/${BASE}.7.html"
#echo "${TEMP_DIR}/${BASE}.5.html"

# Produce a sample page of what it would look like
cp "${TEMP_DIR}/${BASE}.6.html" "${BASE}-sample.html"
cp "${HTML_DIR}/bootstrap-docbook.css" "$(dirname $FILE)/bootstrap-docbook.css"

# Produce a body
cp "${TEMP_DIR}/${BASE}.3.html" "${BASE}.html"

exit 0
