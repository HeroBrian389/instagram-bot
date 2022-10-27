create table images_new (id int not null auto_increment, username VARCHAR(255), taken_at int(11), photo_id VARCHAR(255), device_timestamp int, filename VARCHAR(255), status VARCHAR(255), alt_caption VARCHAR(1000), url VARCHAR(1000) not null UNIQUE, time_entered VARCHAR(255), date_entered VARCHAR(255));


create table images_new (
   id INT NOT NULL AUTO_INCREMENT,
   username VARCHAR(255) NOT NULL,
   taken_at int(11),
   photo_id VARCHAR(255),
   device_timestamp int(11),
   filename VARCHAR(255),
   status VARCHAR(255),
   alt_caption TEXT,
   url TEXT,
   time_entered VARCHAR(255),
   date_entered VARCHAR(255),
   PRIMARY KEY ( id )
);