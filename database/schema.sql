create database msgVerificationBot;

use msgVerificationBot;

create table messages(
  msg_id int NOT NULL AUTO_INCREMENT,
  sentence text,
  truthValue int NOT NULL,
  PRIMARY KEY (msg_id)
);

create table unlabelled_messages(
  msg_id int NOT NULL AUTO_INCREMENT,
  sentence text,
  PRIMARY KEY (msg_id)
);
