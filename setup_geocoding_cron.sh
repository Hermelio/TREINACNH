#!/bin/bash
# Setup automatic geocoding via cron job
# This script will run every hour to geocode new cities

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Cron job command (runs every hour)
CRON_COMMAND="0 * * * * cd $PROJECT_DIR && source venv/bin/activate && python manage.py geocode_pending >> logs/geocode_cron.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "geocode_pending"; then
    echo "✓ Cron job for geocoding already exists"
    echo ""
    echo "Current cron jobs:"
    crontab -l | grep geocode_pending
else
    # Add cron job
    (crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -
    echo "✓ Cron job added successfully!"
    echo ""
    echo "Geocoding will run automatically every hour to process new cities."
fi

echo ""
echo "To view cron logs:"
echo "  tail -f $PROJECT_DIR/logs/geocode_cron.log"
echo ""
echo "To remove cron job:"
echo "  crontab -e  (then delete the geocode_pending line)"
