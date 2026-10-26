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
-- Table structure for table `discover_gestionempresa`
--

DROP TABLE IF EXISTS `discover_gestionempresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_gestionempresa` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `accion` varchar(50) NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `administrador_id` bigint NOT NULL,
  `empresa_id` bigint NOT NULL,
  `detalle` longtext NOT NULL DEFAULT (_utf8mb4'Sin detalles proporcionados'),
  PRIMARY KEY (`id`),
  KEY `discover_gestionempr_administrador_id_f4d4cc63_fk_discover_` (`administrador_id`),
  KEY `discover_gestionempr_empresa_id_5a63bca3_fk_discover_` (`empresa_id`),
  CONSTRAINT `discover_gestionempr_administrador_id_f4d4cc63_fk_discover_` FOREIGN KEY (`administrador_id`) REFERENCES `discover_administrador` (`id`),
  CONSTRAINT `discover_gestionempr_empresa_id_5a63bca3_fk_discover_` FOREIGN KEY (`empresa_id`) REFERENCES `discover_empresa` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_gestionempresa`
--

LOCK TABLES `discover_gestionempresa` WRITE;
/*!40000 ALTER TABLE `discover_gestionempresa` DISABLE KEYS */;
/*!40000 ALTER TABLE `discover_gestionempresa` ENABLE KEYS */;
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
