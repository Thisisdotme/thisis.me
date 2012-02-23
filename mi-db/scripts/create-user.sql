/* user creation and privileges setting */

/* mi user */

DROP USER 'mi';
DROP USER 'mi'@'localhost';
DROP USER 'mi'@'%';

CREATE USER 'mi'@'localhost' IDENTIFIED BY 'mi';
CREATE USER 'mi'@'%' IDENTIFIED BY 'mi';

GRANT ALL PRIVILEGES ON `mi%`.* TO 'mi'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `mi%`.* TO 'mi'@'%' WITH GRANT OPTION;

/* mi author */

DROP USER 'miauthor';
DROP USER 'miauthor'@'localhost';
DROP USER 'miauthor'@'%';

CREATE USER 'miauthor'@'localhost' IDENTIFIED BY 'miauthor';
CREATE USER 'miauthor'@'%' IDENTIFIED BY 'miauthor';

GRANT ALL PRIVILEGES ON `mi%`.* TO 'miauthor'@'localhost' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON `mi%`.* TO 'miauthor'@'%' WITH GRANT OPTION;