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
-- Table structure for table `discover_empresa`
--

DROP TABLE IF EXISTS `discover_empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_empresa` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `correo` varchar(254) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `nombre_empresa` varchar(255) NOT NULL,
  `foto_perfil` varchar(100) DEFAULT NULL,
  `fecha_registro` datetime(6) NOT NULL,
  `reset_token` varchar(100) DEFAULT NULL,
  `reset_token_expires` datetime(6) DEFAULT NULL,
  `blocked_at` datetime(6) DEFAULT NULL,
  `blocked_reason` longtext,
  `is_active` tinyint(1) NOT NULL,
  `is_blocked` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_empresa`
--

LOCK TABLES `discover_empresa` WRITE;
/*!40000 ALTER TABLE `discover_empresa` DISABLE KEYS */;
INSERT INTO `discover_empresa` VALUES (1,'empresa1@empres1.cl','pbkdf2_sha256$1000000$nRWRvjxMV5l1ybKAowgzXz$p4HA2WH1eIoqSiZkylHuLJEC5QIVnkZuZ3MdEpwjH1s=','Empresa 1','images/probando.jpg','2025-06-03 02:39:00.517824',NULL,NULL,NULL,NULL,1,0),(2,'empresa1@empresa1.cl','pbkdf2_sha256$1000000$es1HsQIwha2lUUxZ2n4YKT$+iDks7Pa57mLJHRQ0oanIIxUuQYtEpCh8eAoZxCvThA=','Empresa 1','images/image.jpg','2025-06-05 05:15:58.496173',NULL,NULL,NULL,NULL,1,0);
/*!40000 ALTER TABLE `discover_empresa` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 21:16:06
