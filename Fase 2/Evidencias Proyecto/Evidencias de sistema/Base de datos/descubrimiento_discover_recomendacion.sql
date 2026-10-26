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
-- Table structure for table `discover_recomendacion`
--

DROP TABLE IF EXISTS `discover_recomendacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `discover_recomendacion` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(255) NOT NULL,
  `resumen` longtext,
  `trivia` longtext,
  `frase_destacada` longtext,
  `portada` varchar(100) DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `administrador_id` bigint DEFAULT NULL,
  `empresa_id` bigint DEFAULT NULL,
  `estado_aprobacion_id` bigint NOT NULL,
  `genero_id` bigint NOT NULL,
  `tipo_id` bigint NOT NULL,
  `usuario_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `discover_recomendaci_administrador_id_cdc1e1b0_fk_discover_` (`administrador_id`),
  KEY `discover_recomendaci_empresa_id_e2e49bf3_fk_discover_` (`empresa_id`),
  KEY `discover_recomendaci_estado_aprobacion_id_a41f34b3_fk_discover_` (`estado_aprobacion_id`),
  KEY `discover_recomendacion_genero_id_5db256b8_fk_discover_genero_id` (`genero_id`),
  KEY `discover_recomendaci_tipo_id_47340d80_fk_discover_` (`tipo_id`),
  KEY `discover_recomendaci_usuario_id_5af1cb05_fk_discover_` (`usuario_id`),
  CONSTRAINT `discover_recomendaci_administrador_id_cdc1e1b0_fk_discover_` FOREIGN KEY (`administrador_id`) REFERENCES `discover_administrador` (`id`),
  CONSTRAINT `discover_recomendaci_empresa_id_e2e49bf3_fk_discover_` FOREIGN KEY (`empresa_id`) REFERENCES `discover_empresa` (`id`),
  CONSTRAINT `discover_recomendaci_estado_aprobacion_id_a41f34b3_fk_discover_` FOREIGN KEY (`estado_aprobacion_id`) REFERENCES `discover_estadoaprobacion` (`id`),
  CONSTRAINT `discover_recomendaci_tipo_id_47340d80_fk_discover_` FOREIGN KEY (`tipo_id`) REFERENCES `discover_tiporecomendacion` (`id`),
  CONSTRAINT `discover_recomendaci_usuario_id_5af1cb05_fk_discover_` FOREIGN KEY (`usuario_id`) REFERENCES `discover_usuario` (`id`),
  CONSTRAINT `discover_recomendacion_genero_id_5db256b8_fk_discover_genero_id` FOREIGN KEY (`genero_id`) REFERENCES `discover_genero` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discover_recomendacion`
--

LOCK TABLES `discover_recomendacion` WRITE;
/*!40000 ALTER TABLE `discover_recomendacion` DISABLE KEYS */;
INSERT INTO `discover_recomendacion` VALUES (1,'Resident Evil','probando si se puede rechazar','probando si se puede rechazar','probando si se puede rechazar','images/portadas_recomendaciones/xl_120804_9e6cdea8_ncweLUb.jpg','2025-05-30 05:10:30.637832',1,NULL,3,1,1,1),(2,'resident village','jskjslkjslkjlksasa','nssakmsalksamlnsaklanlksa','dasjisajjsalksajlkas','images/portadas_recomendaciones/Resident_evil_village_gXgMrAm.jpeg','2025-05-30 05:50:34.517429',1,NULL,3,1,1,1),(3,'probando algo','sksaklsajksajlksajksaljsa','snlknsalksanlksanlksanlksa','slksamklsanlksansalknsalksa','images/portadas_recomendaciones/Bad_Bunny_titi_BNDJuBe.png','2025-05-30 05:54:27.492548',1,NULL,1,1,1,1),(4,'snalksnlksanlksanlksa','sanklsanlksanklsanlksa','sklsa skalsa lksa lksa','msamsalkmsalkmsalk','images/portadas_recomendaciones/Bad_Bunny_titi_XgRmtRX.png','2025-05-30 05:55:50.195096',1,NULL,1,1,1,1),(5,'nsksnlknsalksansalk','snaklnsalksanlksanklsanlksa','nalknslknsalknsalknlsak','smaklsalksanksanksanlksanlsa','images/portadas_recomendaciones/call_of_duty_modern_warface_gdZKCcx.jpg','2025-05-30 05:59:49.332730',1,NULL,1,1,1,1),(6,'probndo recomendaciones','snksnsklnsklsnks','nsjksanjsakjsanjksanj','nsaksanjsankjsanjsaknska','images/portadas_recomendaciones/berserk-miura-1024x576-1_ooBJMUq.jpg','2025-06-03 02:11:10.037991',1,NULL,1,1,1,1),(7,'sjsksjksjksljsks','sjklsjsklajksajksajlsakjksaljsakl','sjkajksaljlksajslkjlksajsalkjlksa','snkaklsjalksjaklsjlksa','images/portadas_recomendaciones/probando_virH9zi.jpg','2025-06-03 03:35:20.194774',1,1,1,1,1,1),(8,'sjksaljalkjalkjalksjkals','sjlksajlksajlksajlksajlksa','slksajlksajklsajlksajksa','slksajksajklsajklsajklsa','images/portadas_recomendaciones/Bad_Bunny_titi_c6YtJAm.png','2025-06-03 04:39:19.332844',1,1,3,1,1,NULL),(9,'sjksjkajlkajlksajsalkjslkasa','sjlksjaklsajlkjsaklsjaksaj','saklajslkjsakljsalkjsak','salkjsalkjsalkjsalkjsaklsa','images/portadas_recomendaciones/1540561083517_YnOaTnL.jpeg','2025-06-03 04:46:10.293126',1,NULL,1,1,1,1),(10,'probando si se ven las recomendaciones pendientes','verificandooooo','probandooo','sjksjklsajksajlksajlksa','images/portadas_recomendaciones/gatomeme.jpg','2025-06-03 04:51:49.431722',NULL,1,2,1,1,NULL),(11,'probando si funciona aun xD','shshhshshshhs','ssjjsksjksjks','sjsjsjjsjsjsjjs','images/portadas_recomendaciones/Arctic_monkeys_do_i_wanna_know_Tyeo8d3.jpg','2025-06-04 04:30:07.847301',1,NULL,1,1,1,1),(12,'probando desde el celular','probandooo','probandooo','probandooo','images/portadas_recomendaciones/ea287a98-8f4b-41b8-bed8-c7f30b1c9e8c.jpeg','2025-06-05 03:04:57.818857',1,NULL,1,1,1,1);
/*!40000 ALTER TABLE `discover_recomendacion` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-25 21:16:04
