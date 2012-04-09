USE mi;

DROP TABLE IF EXISTS `tmp_foursquare_venue`;
CREATE TABLE `tmp_foursquare_venue` (
  `author_id` int,
  `venue_id` varchar(32) DEFAULT NULL,
  `feature_event_id` int
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

load data local infile '/Users/howard/dev/emr/foursquare/foursquare-author-venue.part-00000.txt' into table tmp_foursquare_venue;

DROP TABLE IF EXISTS `tmp_foursquare_summary`;
CREATE TABLE `tmp_foursquare_summary` (
  `author_id` int,
  `venue_id` varchar(32) DEFAULT NULL,
  `time` int,
  `feature_event_id` int,
  `count` int
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

load data local infile '/Users/howard/dev/emr/foursquare/foursquare-summary.part-00000.txt' into table tmp_foursquare_summary;