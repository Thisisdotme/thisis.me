use mi

INSERT INTO access_group (group_name) VALUES
	('group:admins'), 
	('group:authors');

INSERT INTO highlight_type (label) VALUES
	('foursquare_30d'),
	('linkedin_30d'),
	('twitter_retweet_30d');

INSERT INTO service_object_type (label) VALUES
	('highlight'),
	('photo-album'),
	('photo'),
	('checkin'),
	('status'),
	('follow'),
	('video'),
	('video-album');