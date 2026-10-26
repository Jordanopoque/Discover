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
-- Table structure for table `discover_aprobacionrecomendacion`
--

DROP TABLE IF EXISTS `discover_aprobacionrecomendacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_aprobacionrecomendacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha` datetime(6) NOT NULL,
  `comentario` longtext,
  `administrador_id` bigint NOT NULL,
  `estado_aprobacion_id` bigint NOT NULL,
  `recomendacion_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discover_aprobacionr_administrador_id_8cba57f2_fk_discover_` (`administrador_id`),
  KEY `discover_aprobacionr_estado_aprobacion_id_78246f12_fk_discover_` (`estado_aprobacion_id`),
  KEY `discover_aprobacionr_recomendacion_id_56e52acb_fk_discover_` (`recomendacion_id`),
  CONSTRAINT `discover_aprobacionr_administrador_id_8cba57f2_fk_discover_` FOREIGN KEY (`administrador_id`) REFERENCES `discover_administrador` (`id`),
  CONSTRAINT `discover_aprobacionr_estado_aprobacion_id_78246f12_fk_discover_` FOREIGN KEY (`estado_aprobacion_id`) REFERENCES `discover_estadoaprobacion` (`id`),
  CONSTRAINT `discover_aprobacionr_recomendacion_id_56e52acb_fk_discover_` FOREIGN KEY (`recomendacion_id`) REFERENCES `discover_recomendacion` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_aprobacionrecomendacion`
--

LOCK TABLES `discover_aprobacionrecomendacion` WRITE;
/*!40000 ALTER TABLE `discover_aprobacionrecomendacion` DISABLE KEYS */;
INSERT INTO `discover_aprobacionrecomendacion` VALUES (1,'2025-05-30 05:15:34.675152','',1,3,1),(2,'2025-05-30 05:51:22.618242','',1,3,2),(3,'2025-05-30 06:00:48.588288','Recomendación aprobada',1,1,5),(4,'2025-06-03 02:11:37.708391','Recomendación aprobada',1,1,3),(5,'2025-06-03 02:11:39.156871','Recomendación aprobada',1,1,4),(6,'2025-06-03 02:11:40.503414','Recomendación aprobada',1,1,6),(7,'2025-06-03 04:11:07.982230','Recomendación aprobada',1,1,7),(8,'2025-06-03 04:50:11.327127','Recomendación aprobada',1,1,9),(9,'2025-06-03 04:54:53.427220','',1,3,8),(10,'2025-06-04 04:30:49.073536','Recomendación aprobada',1,1,11),(11,'2025-06-05 03:06:12.700073','Recomendación aprobada',1,1,12);
/*!40000 ALTER TABLE `discover_aprobacionrecomendacion` ENABLE KEYS */;
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
