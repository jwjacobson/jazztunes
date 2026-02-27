#!/bin/bash
# copy_vendor.sh - Copy vendor JS/CSS from node_modules to static
set -e

JS_DIR="./static/js/vendor"
CSS_DIR="./static/css/vendor"

mkdir -p "$JS_DIR" "$CSS_DIR"

cp node_modules/jquery/dist/jquery.min.js "$JS_DIR/"
cp node_modules/htmx.org/dist/htmx.min.js "$JS_DIR/"
cp node_modules/datatables.net/js/dataTables.min.js "$JS_DIR/"
cp node_modules/datatables.net-dt/css/dataTables.dataTables.min.css "$CSS_DIR/"

echo "Vendor files copied successfully"