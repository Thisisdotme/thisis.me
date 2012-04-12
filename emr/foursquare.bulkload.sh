#!/usr/bin/env bash

# remove everything from the database first
echo "Truncating foursquare tmp tables"
/usr/local/mysql/bin/mysql --user=mi --password=mi -e "use mi; truncate tmp_foursquare_summary; truncate tmp_foursquare_venue;"

for file in foursquare-author-venue.part-*.txt; do

	echo Bulking loading $file
	/usr/local/mysql/bin/mysql --user=mi --password=mi -e "use mi; load data local infile '$file' into table tmp_foursquare_venue;"
	
done

for file in foursquare-summary.part-*.txt; do

	echo Build loadking $file
	/usr/local/mysql/bin/mysql --user=mi --password=mi -e "use mi; load data local infile '$file' into table tmp_foursquare_summary;"
	
done