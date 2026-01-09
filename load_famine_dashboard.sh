#!/bin/bash
set -e

# 1. Generate segment dari CSV
~/apache-pinot-1.4.0-bin/bin/pinot-admin.sh CreateSegment \
  -dataDir /home/pinot/project_root/lakehouse/gold \
  -format CSV \
  -outDir /home/pinot/segments/famine_dashboard \
  -overwrite \
  -tableConfigFile famine_dashboard_table.json \
  -schemaFile famine_dashboard_schema.json

# 2. Cari folder segment yang baru dibuat
SEGMENT_DIR=$(ls -d /home/pinot/segments/famine_dashboard/famine_dashboard_* | head -n 1)

# 3. Kompres folder jadi tar.gz
tar -czvf ${SEGMENT_DIR}.tar.gz -C /home/pinot/segments/famine_dashboard $(basename $SEGMENT_DIR)

# 4. Upload ke Controller dengan endpoint ingestion/segments
curl -X POST "http://localhost:9000/ingestion/segments" \
     -H "Content-Type: multipart/form-data" \
     -F "tableName=famine_dashboard" \
     -F "segment=@${SEGMENT_DIR}.tar.gz"

echo "✅ Segment famine_dashboard berhasil di-upload!"
