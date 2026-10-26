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
-- Table structure for table `discover_usuario`
--

DROP TABLE IF EXISTS `discover_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_usuario` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `correo` varchar(254) NOT NULL,
  `contrasena` varchar(255) NOT NULL,
  `p_nombre` varchar(255) DEFAULT NULL,
  `p_apellido` varchar(255) DEFAULT NULL,
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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_usuario`
--

LOCK TABLES `discover_usuario` WRITE;
/*!40000 ALTER TABLE `discover_usuario` DISABLE KEYS */;
INSERT INTO `discover_usuario` VALUES (1,'jordan.o.poque@gmail.com','pbkdf2_sha256$1000000$LjFeFJNa2OkWFDtxboJH7E$1+binktkbfex/skRm5+wnedRFCSd4fYBYG7IonttCpM=','Jordan Antonio','Ordenes','images/IMG_0660.jpeg','2025-05-30 04:34:42.473657','6aHU6vRJba8m2H_RoL_FhU9JBNeYAaBJRt9LNVcipMw','2025-06-04 07:14:40.229924',NULL,NULL,1,0),(2,'usuario1@usuario1.cl','pbkdf2_sha256$1000000$k9W69bpC1bbdwMlkRTd3Z7$NA9PobeG5M9f87zRtnwhOcw9Al4zxCQ0EwLu0jEu0W8=','Usuario','1','images/gatoooooo_C1dhn1K.jpg','2025-06-05 05:14:12.356491',NULL,NULL,NULL,NULL,1,0),(3,'intento50@intento50.cl','pbkdf2_sha256$1000000$Gik1grIKqi5F2bi1Rsc34m$87O0sIdWKjed7vrh71AwrKK6VbeW7h6VNXp7sHcHOkQ=','intento','cincuenta','images/MV5BMjU4Mzc0YmQtYzlkNy00ZjJkLWE2NDktZmM1OWZmOTAyOTBlXkEyXkFqcGc_F7oT78g._V1_FMjpg_UX1000_.jpg','2026-09-22 04:21:21.755951',NULL,NULL,NULL,NULL,1,0);
/*!40000 ALTER TABLE `discover_usuario` ENABLE KEYS */;
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
