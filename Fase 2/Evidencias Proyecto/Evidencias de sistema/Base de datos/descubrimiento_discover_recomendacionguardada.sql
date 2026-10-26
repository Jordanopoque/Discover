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
-- Table structure for table `discover_recomendacionguardada`
--

DROP TABLE IF EXISTS `discover_recomendacionguardada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_recomendacionguardada` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_guardado` datetime(6) NOT NULL,
  `recomendacion_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discover_recomendaci_recomendacion_id_5c62317c_fk_discover_` (`recomendacion_id`),
  KEY `discover_recomendaci_usuario_id_4214907b_fk_discover_` (`usuario_id`),
  CONSTRAINT `discover_recomendaci_recomendacion_id_5c62317c_fk_discover_` FOREIGN KEY (`recomendacion_id`) REFERENCES `discover_recomendacion` (`id`),
  CONSTRAINT `discover_recomendaci_usuario_id_4214907b_fk_discover_` FOREIGN KEY (`usuario_id`) REFERENCES `discover_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_recomendacionguardada`
--

LOCK TABLES `discover_recomendacionguardada` WRITE;
/*!40000 ALTER TABLE `discover_recomendacionguardada` DISABLE KEYS */;
INSERT INTO `discover_recomendacionguardada` VALUES (2,'2025-06-05 06:42:04.967018',11,1),(4,'2025-06-05 07:11:31.566019',9,1);
/*!40000 ALTER TABLE `discover_recomendacionguardada` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 21:16:07
