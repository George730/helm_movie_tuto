LAST_WEEK_FILE=$../csv/(date -d '7 days ago' "+%Y-%m-%d")*.csv
echo "delete files 7 days ago:" $LAST_WEEK_FILE
find . -name "$LAST_WEEK_FILE" -type f -delete
