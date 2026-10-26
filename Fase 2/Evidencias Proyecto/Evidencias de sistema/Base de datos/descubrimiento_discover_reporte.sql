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
-- Table structure for table `discover_reporte`
--

DROP TABLE IF EXISTS `discover_reporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_reporte` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `motivo` longtext NOT NULL,
  `fecha` datetime(6) NOT NULL,
  `recomendacion_id` bigint NOT NULL,
  `usuario_id` bigint NOT NULL,
  `estado` varchar(20) NOT NULL,
  `administrador_id` bigint DEFAULT NULL,
  `comentario_admin` longtext,
  `fecha_resolucion` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `discover_reporte_recomendacion_id_a5ee79da_fk_discover_` (`recomendacion_id`),
  KEY `discover_reporte_usuario_id_72ab65e5_fk_discover_usuario_id` (`usuario_id`),
  KEY `discover_reporte_administrador_id_41c080c8_fk_discover_` (`administrador_id`),
  CONSTRAINT `discover_reporte_administrador_id_41c080c8_fk_discover_` FOREIGN KEY (`administrador_id`) REFERENCES `discover_administrador` (`id`),
  CONSTRAINT `discover_reporte_recomendacion_id_a5ee79da_fk_discover_` FOREIGN KEY (`recomendacion_id`) REFERENCES `discover_recomendacion` (`id`),
  CONSTRAINT `discover_reporte_usuario_id_72ab65e5_fk_discover_usuario_id` FOREIGN KEY (`usuario_id`) REFERENCES `discover_usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_reporte`
--

LOCK TABLES `discover_reporte` WRITE;
/*!40000 ALTER TABLE `discover_reporte` DISABLE KEYS */;
INSERT INTO `discover_reporte` VALUES (1,'no me gusta','2025-06-03 05:28:47.931043',9,1,'resuelto',1,'','2025-06-03 05:30:21.414364'),(2,'esta tampoco me gusta','2025-06-03 05:36:53.714723',7,1,'pendiente',NULL,NULL,NULL);
/*!40000 ALTER TABLE `discover_reporte` ENABLE KEYS */;
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
