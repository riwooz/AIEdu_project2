# Project2

1. SQL 생성

CREATE TABLE 'user' (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `nickname` varchar(20) UNIQ NOT NULL,
    `name` varchar(20) NOT NULL,
    `profile` varchar(256) NOT NULL
    `birthdate` datetime NOT NULL,
    `password` varchar(256) NOT NULL,
    PRIMARY KEY (`id`)
)
