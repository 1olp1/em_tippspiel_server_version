-- MySQL dump 10.13  Distrib 8.0.29, for Linux (x86_64)
--
-- Host: salatic.mysql.pythonanywhere-services.com    Database: salatic$em-tippspiel
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `matchday` int DEFAULT NULL,
  `team1_id` int NOT NULL,
  `team2_id` int NOT NULL,
  `team1_score` int DEFAULT NULL,
  `team2_score` int DEFAULT NULL,
  `matchDateTime` datetime DEFAULT NULL,
  `matchIsFinished` int DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `lastUpdateDateTime` datetime DEFAULT NULL,
  `predictions_evaluated` int DEFAULT NULL,
  `evaluation_Date` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `team1_id` (`team1_id`),
  KEY `team2_id` (`team2_id`),
  CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`team1_id`) REFERENCES `teams` (`id`),
  CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`team2_id`) REFERENCES `teams` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69392 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matches`
--

LOCK TABLES `matches` WRITE;
/*!40000 ALTER TABLE `matches` DISABLE KEYS */;
INSERT INTO `matches` VALUES (69341,1,3196,5271,5,1,'2024-06-14 21:00:00',1,'München','2024-06-23 23:29:34',1,'2024-06-29 20:12:36'),(69342,1,6167,38,1,3,'2024-06-15 15:00:00',1,'Köln','2024-06-23 23:30:16',1,'2024-06-29 20:12:36'),(69343,1,170,146,3,0,'2024-06-15 18:00:00',1,'Berlin','2024-06-16 08:08:53',1,'2024-06-29 20:12:36'),(69344,1,3203,6169,2,1,'2024-06-15 21:00:00',1,'Dortmund','2024-06-17 15:11:22',1,'2024-06-29 20:12:36'),(69345,1,1410,4353,1,2,'2024-06-16 15:00:00',1,'Hamburg','2024-06-23 23:32:11',1,'2024-06-29 20:12:36'),(69346,1,6170,758,1,1,'2024-06-16 18:00:00',1,'Stuttgart','2024-06-16 20:08:43',1,'2024-06-29 20:12:36'),(69347,1,5592,3197,0,1,'2024-06-16 21:00:00',1,'Gelsenkirchen','2024-06-18 11:44:21',1,'2024-06-29 20:12:36'),(69348,1,6171,3204,3,0,'2024-06-17 15:00:00',1,'München','2024-06-23 23:34:30',1,'2024-06-29 20:12:36'),(69349,1,5587,3201,0,1,'2024-06-17 18:00:00',1,'Frankfurt','2024-06-23 23:36:43',1,'2024-06-29 20:12:36'),(69350,1,4354,144,0,1,'2024-06-17 21:00:00',1,'Düsseldorf','2024-06-23 23:37:37',1,'2024-06-29 20:12:36'),(69351,1,3205,6239,3,1,'2024-06-18 18:00:00',1,'Dortmund','2024-06-23 23:38:17',1,'2024-06-29 20:12:36'),(69352,1,3198,141,2,1,'2024-06-18 21:00:00',1,'Leipzig','2024-06-19 00:20:55',1,'2024-06-29 20:12:36'),(69353,2,146,6169,2,2,'2024-06-19 15:00:00',1,'Hamburg','2024-06-23 11:05:07',1,'2024-06-29 20:12:36'),(69354,2,3196,6167,2,0,'2024-06-19 18:00:00',1,'Stuttgart','2024-06-20 16:44:16',1,'2024-06-29 20:12:36'),(69355,2,5271,38,1,1,'2024-06-19 21:00:00',1,'Köln','2024-06-20 16:43:54',1,'2024-06-29 20:12:36'),(69356,2,6170,5592,1,1,'2024-06-20 15:00:00',1,'München','2024-06-20 17:18:40',1,'2024-06-29 20:12:36'),(69357,2,758,3197,1,1,'2024-06-20 18:00:00',1,'Frankfurt','2024-06-23 23:25:03',1,'2024-06-29 20:12:36'),(69358,2,170,3203,1,0,'2024-06-20 21:00:00',1,'Gelsenkirchen','2024-06-21 13:19:50',1,'2024-06-29 20:12:36'),(69359,2,3201,3204,1,2,'2024-06-21 15:00:00',1,'Düsseldorf','2024-06-22 22:59:20',1,'2024-06-29 20:12:36'),(69360,2,1410,4354,1,3,'2024-06-21 18:00:00',1,'Berlin','2024-06-23 23:23:38',1,'2024-06-29 20:12:36'),(69361,2,4353,144,0,0,'2024-06-21 21:00:00',1,'Leipzig','2024-06-23 23:26:10',1,'2024-06-29 20:12:36'),(69362,2,6239,141,1,1,'2024-06-22 15:00:00',1,'Hamburg','2024-06-23 01:38:03',1,'2024-06-29 20:12:36'),(69363,2,3205,3198,0,3,'2024-06-22 18:00:00',1,'Dortmund','2024-06-23 01:33:34',1,'2024-06-29 20:12:36'),(69364,2,5587,6171,2,0,'2024-06-22 21:00:00',1,'Köln','2024-06-23 23:27:15',1,'2024-06-29 20:12:36'),(69365,3,38,3196,1,1,'2024-06-23 21:00:00',1,'Frankfurt','2024-06-24 21:02:47',1,'2024-06-29 20:12:36'),(69366,3,5271,6167,0,1,'2024-06-23 21:00:00',1,'Stuttgart','2024-06-24 21:02:53',1,'2024-06-29 20:12:36'),(69367,3,146,3203,1,1,'2024-06-24 21:00:00',1,'Leipzig','2024-06-25 00:16:13',1,'2024-06-29 20:12:36'),(69368,3,6169,170,0,1,'2024-06-24 21:00:00',1,'Düsseldorf','2024-06-25 09:17:41',1,'2024-06-29 20:12:36'),(69369,3,4353,4354,2,3,'2024-06-25 18:00:00',1,'Berlin','2024-06-25 19:57:08',1,'2024-06-29 20:12:36'),(69370,3,144,1410,1,1,'2024-06-25 18:00:00',1,'Dortmund','2024-06-26 00:13:20',1,'2024-06-29 20:12:36'),(69371,3,3197,6170,0,0,'2024-06-25 21:00:00',1,'Köln','2024-06-25 22:52:12',1,'2024-06-29 20:12:36'),(69372,3,758,5592,0,0,'2024-06-25 21:00:00',1,'München','2024-06-25 22:54:20',1,'2024-06-29 20:12:36'),(69373,3,3201,6171,1,1,'2024-06-26 18:00:00',1,'Frankfurt','2024-06-26 19:55:53',1,'2024-06-29 20:12:36'),(69374,3,3204,5587,0,0,'2024-06-26 18:00:00',1,'Stuttgart','2024-06-26 19:56:16',1,'2024-06-29 20:12:36'),(69375,3,141,3205,1,2,'2024-06-26 21:00:00',1,'Hamburg','2024-06-26 23:07:13',1,'2024-06-29 20:12:36'),(69376,3,6239,3198,2,0,'2024-06-26 21:00:00',1,'Gelsenkirchen','2024-06-26 22:55:22',1,'2024-06-29 20:12:36'),(69377,4,38,3203,2,0,'2024-06-29 18:00:00',1,'Berlin','2024-06-29 19:54:56',1,'2024-06-29 20:12:36'),(69378,4,3196,758,2,0,'2024-06-29 21:00:00',1,'Dortmund','2024-06-29 23:19:55',1,'2024-06-29 23:20:06'),(69379,4,3197,3201,2,1,'2024-06-30 18:00:00',1,'Gelsenkirchen','2024-06-30 20:37:42',1,'2024-06-30 20:38:03'),(69380,4,170,6239,4,1,'2024-06-30 21:00:00',1,'Köln','2024-06-30 23:02:39',1,'2024-06-30 23:06:39'),(69381,4,144,5587,NULL,NULL,'2024-07-01 18:00:00',0,'Düsseldorf','2024-06-26 19:54:47',0,NULL),(69382,4,3198,6170,NULL,NULL,'2024-07-01 21:00:00',0,'Frankfurt','2024-06-26 22:19:51',0,NULL),(69383,4,6171,4353,NULL,NULL,'2024-07-02 18:00:00',0,'München','2024-06-26 22:19:59',0,NULL),(69384,4,4354,3205,NULL,NULL,'2024-07-02 21:00:00',0,'Leipzig','2024-06-26 22:20:21',0,NULL),(69385,5,170,3196,NULL,NULL,'2024-07-05 18:00:00',0,'Stuttgart','2024-06-30 22:48:28',0,NULL),(69386,5,5251,5251,NULL,NULL,'2024-07-05 21:00:00',0,'Hamburg','2024-02-03 00:29:37',0,NULL),(69387,5,3197,38,NULL,NULL,'2024-07-06 18:00:00',0,'Düsseldorf','2024-06-30 20:40:47',0,NULL),(69388,5,5251,5251,NULL,NULL,'2024-07-06 21:00:00',0,'Berlin','2024-02-03 00:30:38',0,NULL),(69389,6,5251,5251,NULL,NULL,'2024-07-09 21:00:00',0,'München','2024-02-03 00:31:31',0,NULL),(69390,6,5251,5251,NULL,NULL,'2024-07-10 21:00:00',0,'Dortmund','2024-02-03 00:31:54',0,NULL),(69391,7,5251,5251,NULL,NULL,'2024-07-14 21:00:00',0,'Berlin','2024-02-03 00:32:23',0,NULL);
/*!40000 ALTER TABLE `matches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `predictions`
--

DROP TABLE IF EXISTS `predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `predictions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `matchday` int NOT NULL,
  `match_id` int NOT NULL,
  `team1_score` int NOT NULL,
  `team2_score` int NOT NULL,
  `goal_diff` int NOT NULL,
  `winner` int NOT NULL,
  `prediction_date` datetime DEFAULT NULL,
  `points` int DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `predictions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=84 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `predictions`
--

LOCK TABLES `predictions` WRITE;
/*!40000 ALTER TABLE `predictions` DISABLE KEYS */;
INSERT INTO `predictions` VALUES (6,4,4,69377,2,1,1,1,'2024-06-25 23:54:06',2),(7,4,4,69378,5,0,5,1,'2024-06-25 23:54:06',2),(14,6,4,69377,2,1,1,1,'2024-06-29 11:54:27',2),(16,5,4,69381,1,0,1,1,'2024-06-30 20:40:49',0),(17,5,4,69378,2,0,2,1,'2024-06-29 15:31:45',4),(18,4,4,69379,0,1,-1,2,'2024-06-27 16:53:35',0),(19,4,4,69380,3,0,3,1,'2024-06-27 16:53:35',3),(20,4,4,69381,2,0,2,1,'2024-06-27 16:53:35',0),(21,4,4,69382,1,2,-1,2,'2024-06-27 16:53:35',0),(22,4,4,69383,0,1,-1,2,'2024-06-27 16:53:35',0),(23,4,4,69384,3,1,2,1,'2024-06-27 16:53:35',0),(24,5,4,69377,0,1,-1,2,'2024-06-29 16:44:46',0),(25,5,4,69379,2,0,2,1,'2024-06-28 07:21:01',2),(42,8,4,69377,0,1,-1,2,'2024-06-28 22:22:40',0),(43,8,4,69378,2,0,2,1,'2024-06-28 22:22:40',4),(44,8,4,69379,1,0,1,1,'2024-06-28 22:22:40',3),(45,8,4,69380,2,0,2,1,'2024-06-28 22:22:40',2),(46,8,4,69381,2,1,1,1,'2024-06-30 20:41:14',0),(47,9,4,69377,6,7,-1,2,'2024-06-29 17:19:49',0),(48,9,4,69378,3,1,2,1,'2024-06-29 20:58:10',3),(49,11,4,69377,1,1,0,0,'2024-06-29 11:39:42',0),(50,11,4,69378,2,0,2,1,'2024-06-29 11:39:42',4),(51,6,4,69378,2,0,2,1,'2024-06-29 11:54:12',4),(52,6,4,69379,3,1,2,1,'2024-06-29 11:56:27',2),(53,6,4,69380,2,0,2,1,'2024-06-29 11:56:27',2),(54,6,4,69381,6,7,-1,2,'2024-07-01 01:31:46',0),(55,6,4,69382,2,1,1,1,'2024-06-29 11:56:27',0),(56,6,4,69383,0,1,-1,2,'2024-06-29 11:56:27',0),(57,6,4,69384,2,1,1,1,'2024-06-29 11:56:27',0),(58,12,4,69377,3,1,2,1,'2024-06-29 15:19:05',3),(59,12,4,69378,3,1,2,1,'2024-06-29 15:19:05',3),(60,13,4,69378,3,1,2,1,'2024-06-29 18:15:36',3),(61,7,4,69378,3,1,2,1,'2024-06-29 20:36:50',3),(62,5,4,69380,2,1,1,1,'2024-06-30 20:40:30',2),(63,7,4,69379,2,0,2,1,'2024-06-30 08:25:59',2),(64,7,4,69380,3,0,3,1,'2024-06-30 08:25:59',3),(65,7,4,69381,3,1,2,1,'2024-06-30 08:25:59',0),(66,7,4,69382,2,1,1,1,'2024-06-30 08:25:59',0),(67,7,4,69383,0,2,-2,2,'2024-06-30 08:25:59',0),(68,7,4,69384,2,0,2,1,'2024-06-30 08:25:59',0),(69,9,4,69379,2,1,1,1,'2024-06-30 11:27:36',4),(70,9,4,69380,1,0,1,1,'2024-06-30 20:49:21',2),(71,9,4,69381,1,2,-1,2,'2024-06-30 11:27:36',0),(72,9,4,69382,1,0,1,1,'2024-06-30 11:27:36',0),(73,9,4,69383,2,1,1,1,'2024-06-30 11:27:36',0),(74,9,4,69384,2,0,2,1,'2024-06-30 11:35:53',0),(75,12,4,69379,2,1,1,1,'2024-06-30 11:39:57',4),(76,12,4,69380,4,0,4,1,'2024-06-30 11:39:57',2),(77,11,4,69380,3,1,2,1,'2024-06-30 18:27:06',2),(78,11,4,69381,2,3,-1,2,'2024-06-30 18:27:06',0),(79,11,4,69382,1,0,1,1,'2024-06-30 18:27:06',0),(80,11,4,69383,0,2,-2,2,'2024-06-30 18:27:06',0),(81,11,4,69384,3,1,2,1,'2024-06-30 18:27:06',0),(82,5,4,69382,1,0,1,1,'2024-06-30 20:40:49',0),(83,8,4,69382,1,0,1,1,'2024-06-30 20:41:14',0);
/*!40000 ALTER TABLE `predictions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams` (
  `id` int NOT NULL,
  `teamName` text,
  `shortName` text,
  `teamIconUrl` text,
  `teamIconPath` text,
  `teamGroupName` text,
  `points` int DEFAULT '0',
  `opponentGoals` int DEFAULT '0',
  `goals` int DEFAULT '0',
  `matches` int DEFAULT '0',
  `won` int DEFAULT '0',
  `lost` int DEFAULT '0',
  `draw` int DEFAULT '0',
  `goalDiff` int DEFAULT '0',
  `teamRank` int DEFAULT NULL,
  `lastUpdateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teams`
--

LOCK TABLES `teams` WRITE;
/*!40000 ALTER TABLE `teams` DISABLE KEYS */;
INSERT INTO `teams` VALUES (38,'Schweiz','CHE','https://img.uefa.com/imgml/flags/140x140/SUI.png','./static/em/2024/team-logos/CHE.png','Gruppe A',8,3,7,4,2,0,2,4,3,'2024-06-30 20:27:17'),(141,'Tschechien','CZE','https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Flag_of_the_Czech_Republic.svg/200px-Flag_of_the_Czech_Republic.svg.png','./static/em/2024/team-logos/CZE.png','Gruppe F',1,5,3,3,0,2,1,-2,22,'2024-06-30 20:27:17'),(144,'Frankreich','FRA','http://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Flag_of_France.svg/20px-Flag_of_France.svg.png','./static/em/2024/team-logos/FRA.png','Gruppe D',5,1,2,3,1,0,2,1,8,'2024-06-30 20:27:17'),(146,'Kroatien','HRV','https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Flag_of_Croatia.svg/20px-Flag_of_Croatia.svg.png','./static/em/2024/team-logos/HRV.png','Gruppe B',2,6,3,3,0,1,2,-3,20,'2024-06-30 20:27:17'),(170,'Spanien','ESP','https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Flag_of_Spain.svg/20px-Flag_of_Spain.svg.png','./static/em/2024/team-logos/ESP.png','Gruppe B',9,0,5,3,3,0,0,5,2,'2024-06-30 20:27:17'),(758,'Dänemark','DNK','https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Denmark.svg/20px-Flag_of_Denmark.svg.png','./static/em/2024/team-logos/DNK.png','Gruppe C',3,4,2,4,0,1,3,-2,17,'2024-06-30 20:27:17'),(1410,'Polen','POL','https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Flag_of_Poland.svg/23px-Flag_of_Poland.svg.png','./static/em/2024/team-logos/POL.png','Gruppe D',1,6,3,3,0,2,1,-3,23,'2024-06-30 20:27:17'),(3196,'Deutschland','DEU','https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Flag_of_Germany.svg/150px-Flag_of_Germany.svg.png','./static/em/2024/team-logos/DEU.png','Gruppe A',10,2,10,4,3,0,1,8,1,'2024-06-30 20:27:17'),(3197,'England','ENG','https://upload.wikimedia.org/wikipedia/en/thumb/b/be/Flag_of_England.svg/1280px-Flag_of_England.svg.png','./static/em/2024/team-logos/ENG.png','Gruppe C',6,2,3,4,1,0,3,1,6,'2024-06-30 20:27:17'),(3198,'Portugal','PRT','https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Flag_of_Portugal.svg/2000px-Flag_of_Portugal.svg.png','./static/em/2024/team-logos/PRT.png','Gruppe F',6,3,5,3,2,1,0,2,5,'2024-06-30 20:27:17'),(3201,'Slowakei','SVK','https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Flag_of_Slovakia.svg/1280px-Flag_of_Slovakia.svg.png','./static/em/2024/team-logos/SVK.png','Gruppe E',5,4,4,4,1,1,2,0,9,'2024-06-30 20:27:17'),(3203,'Italien','ITA','https://upload.wikimedia.org/wikipedia/en/0/03/Flag_of_Italy.svg','./static/em/2024/team-logos/ITA.svg','Gruppe B',4,5,3,4,1,2,1,-2,14,'2024-06-30 20:27:17'),(3204,'Ukraine','UKR','https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Flag_of_Ukraine.svg/2000px-Flag_of_Ukraine.svg.png','./static/em/2024/team-logos/UKR.png','Gruppe E',4,4,2,3,1,1,1,-2,15,'2024-06-30 20:27:17'),(3205,'Türkei','TUR','https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Flag_of_Turkey.svg/2000px-Flag_of_Turkey.svg.png','./static/em/2024/team-logos/TUR.png','Gruppe F',6,5,5,3,2,1,0,0,7,'2024-06-30 20:27:17'),(4353,'Niederlande','NLD','https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/20px-Flag_of_the_Netherlands.svg.png','./static/em/2024/team-logos/NLD.png','Gruppe D',4,4,4,3,1,1,1,0,13,'2024-06-30 20:27:17'),(4354,'Österreich','AUT','https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_Austria.svg/20px-Flag_of_Austria.svg.png','./static/em/2024/team-logos/AUT.png','Gruppe D',6,4,6,3,2,1,0,2,4,'2024-06-30 20:27:17'),(5251,'-','-',NULL,'./static/em/2024/team-logos/dummy-teamlogo.png','None',0,0,0,0,0,0,0,0,25,'2024-06-30 20:27:17'),(5271,'Schottland','SCT','https://img.uefa.com/imgml/flags/140x140/SCO.png','./static/em/2024/team-logos/SCT.png','Gruppe A',1,7,2,3,0,2,1,-5,24,'2024-06-30 20:27:17'),(5587,'Belgien','BEL','https://cdn.pixabay.com/photo/2013/07/13/14/14/belgium-162240_960_720.png','./static/em/2024/team-logos/BEL.png','Gruppe E',4,1,2,3,1,1,1,1,11,'2024-06-30 20:27:17'),(5592,'Serbien','SRB','https://cdn.pixabay.com/photo/2013/07/13/14/17/serbia-162415_960_720.png','./static/em/2024/team-logos/SRB.png','Gruppe C',2,2,1,3,0,1,2,-1,19,'2024-06-30 20:27:17'),(6167,'Ungarn','HUN','https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Flag_of_Hungary.svg/320px-Flag_of_Hungary.svg.png','./static/em/2024/team-logos/HUN.png','Gruppe A',3,5,2,3,1,2,0,-3,18,'2024-06-30 20:27:17'),(6169,'Albanien','ALB','https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/320px-Flag_of_Albania.svg.png','./static/em/2024/team-logos/ALB.png','Gruppe B',1,5,3,3,0,2,1,-2,21,'2024-06-30 20:27:17'),(6170,'Slowenien','SVN','https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Flag_of_Slovenia.svg/320px-Flag_of_Slovenia.svg.png','./static/em/2024/team-logos/SVN.png','Gruppe C',3,2,2,3,0,0,3,0,16,'2024-06-30 20:27:17'),(6171,'Rumänien','ROU','https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Flag_of_Romania.svg/320px-Flag_of_Romania.svg.png','./static/em/2024/team-logos/ROU.png','Gruppe E',4,3,4,3,1,1,1,1,10,'2024-06-30 20:27:17'),(6239,'Georgien','GEO','https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_Georgia.svg/20px-Flag_of_Georgia.svg.png','./static/em/2024/team-logos/GEO.png','Gruppe F',4,4,4,3,1,1,1,0,12,'2024-06-30 20:27:17');
/*!40000 ALTER TABLE `teams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `hash` text NOT NULL,
  `total_points` int DEFAULT '0',
  `correct_result` int DEFAULT '0',
  `correct_goal_diff` int DEFAULT '0',
  `correct_tendency` int DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (4,'J0dd3l','scrypt:32768:8:1$rvkYnEwY2qt6laBL$d16af625f1c43d3a23b93eb53a4c978edaea0cb42f842db6b9c283f4106739dcacab13dc2347b76099c1c8a29d29e66d04bca166da8c231ff75a32275789f54a',7,0,1,2),(5,'olp','scrypt:32768:8:1$Wse1bdapyOLi17f7$6d15439b19754b8f7b5d6193fd6dc801e66d19d9cac464c0d147919bca932cb84c5618a011bb2776e20757d32715f238c340532a3bd4b9d2b5ec5e9f640e250b',8,1,0,2),(6,'Tuktuk_20','scrypt:32768:8:1$2Itk3kpu1WXzPoJT$1d1c95c7ef7c505e6fb3b27fe688f6efea6de69bc33fd172c3636e1a77cf867c923321e31348e6e1e97d1096421f0bb2dd2528b862c5aff7b846fe7322cc4e66',10,1,0,3),(7,'Depp','scrypt:32768:8:1$3opA2WtpyToBBT07$62b34b82888f41e69aacc6a55d5ffd62ca42c65d68c23a718a5d5af70d789b7921b204809afccfcdae21f24f10ad650dd743ccd52384779fc294e659a8ac41dc',8,0,2,1),(8,'CH7','scrypt:32768:8:1$ex28xhNZcMMp3638$cc803fbfb444b23b086e3cce2f140652a1206ae6068ec5cf1b22b6ed293521ebf4bf6de69d3fac7d9b2cb0c7e5ef21cd6bd1abf93a67b848c1bad4d525fc41e1',9,1,1,1),(9,'Nebroid','scrypt:32768:8:1$BH08mP5vW5VtyUZZ$9ba700bc4295283ca91c1f64a3ccee8414770cfca8949dea488bae5c2ba11b6a19963d9f5f1af7963ba2478b100ad4749bf10c58f5a07ab82efd9f16b8f8a059',9,1,1,1),(11,'Zebasti ','scrypt:32768:8:1$gABoBbQtc1JGOoAm$c00c26e8f220041e2ef493f2c5d68d19aa8d3b7c6f0f657a971b5bdcb89b187b9bfbc92e056447c0a6c22d829fd6249cd251970cb3916895c805495048a43647',6,1,0,1),(12,'Rebberlein1','scrypt:32768:8:1$ruOYlL3SlQ7QefZN$39c048ad217fe063375e766ddb190006e779cf71aec2d8eb666805f0409eb97ff9a2754abac4c12671d6e3932da7234ebdd20b61f92f5c6756476ed919ce84fb',12,1,2,1),(13,'John','scrypt:32768:8:1$N5zXAiij7HHYrlIM$0ef4ed5119bdfcb93a6b9d4684b58e6a0163b174d379f3a72860b706ac079e1dad3592a0288998a3886adb8a82daee432c6fad7587e6d7a4c310e8a8a6f42275',3,0,1,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-01  2:43:15
