-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: descubrimiento
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('dlgy4lbt54rkehep7kcwqb8yb6rfbd5s','eyJ1c2VyX2lkIjoxLCJ1c2VyX3R5cGUiOiJhZG1pbmlzdHJhZG9yIn0:1uMKCy:B6R7IwoOOmP_qWl2lSx5hOw7ppKdtyBY6nNVaOLJGzY','2025-06-17 05:29:08.418749'),('iyd6tmjop745yazmte7fg1vzuk4jiltr','eyJ1c2VyX2lkIjozLCJ1c2VyX3R5cGUiOiJ1c3VhcmlvIn0:1x8s64:SiT1N1W95CP9s1kDl1ZRUXkmc2LK8u4-4AJ2gaEbEVY','2026-10-06 04:27:12.991724'),('vx800gbbso5moohtlxihcnxn55e0169u','.eJxVjEsOwjAMRO_idRUlNVE_S_acIXJshxZQg_pZIMTdaUWF1N1o3pt5wzLpGHqB1hW_PL-eCu2aFxr7DAUEWuYu_D1wxy4S33XYgNxouGbDeZjHPppNMTudzCWLPs67ezjoaOrWdUL2JByxYhTPtrEuacMlM6VEliwqnqpk6-jFS0SLgkKloDYOUx3h8wWtYkTP:1uNO65:fiNqMAIqqdUpbUf9hQt7jTpscOV-hRfPU33_bcaDJnM','2025-06-20 03:50:25.160875');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 21:16:05
