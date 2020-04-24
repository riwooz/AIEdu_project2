


CREATE TABLE `user` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `nickname` varchar(20) NOT NULL,
    `password` varchar(256) NOT NULL,
    `name` varchar(20) NOT NULL,
    `profile` varchar(256) NOT NULL,
    `birthdate` datetime NOT NULL,
    UNIQUE INDEX uniq_nickname (nickname),
    PRIMARY KEY (`id`)
);

CREATE TABLE `topic` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `title` varchar(20) NOT NULL,
    `description` text,
    PRIMARY KEY (`id`) 
);

CREATE TABLE 'baseball' (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `nickname` varchar(20) NOT NULL,
    `count` int(5) NOT NULL
)


INSERT INTO `topic` VALUES (1,'Profile','개인정보');
INSERT INTO `topic` VALUES (2,'News','뉴스');
INSERT INTO `topic` VALUES (3,'Photos','사진');
INSERT INTO `topic` VALUES (4,'Baseball','야구게임');



INSERT INTO `topic` VALUES (1,'MySQL','MySQL is...','2018-01-01 12:10:11',1);
