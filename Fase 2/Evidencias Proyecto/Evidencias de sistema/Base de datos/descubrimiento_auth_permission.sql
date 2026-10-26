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
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=77 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add administrador',7,'add_administrador'),(26,'Can change administrador',7,'change_administrador'),(27,'Can delete administrador',7,'delete_administrador'),(28,'Can view administrador',7,'view_administrador'),(29,'Can add empresa',8,'add_empresa'),(30,'Can change empresa',8,'change_empresa'),(31,'Can delete empresa',8,'delete_empresa'),(32,'Can view empresa',8,'view_empresa'),(33,'Can add estado aprobacion',9,'add_estadoaprobacion'),(34,'Can change estado aprobacion',9,'change_estadoaprobacion'),(35,'Can delete estado aprobacion',9,'delete_estadoaprobacion'),(36,'Can view estado aprobacion',9,'view_estadoaprobacion'),(37,'Can add genero',10,'add_genero'),(38,'Can change genero',10,'change_genero'),(39,'Can delete genero',10,'delete_genero'),(40,'Can view genero',10,'view_genero'),(41,'Can add tipo recomendacion',11,'add_tiporecomendacion'),(42,'Can change tipo recomendacion',11,'change_tiporecomendacion'),(43,'Can delete tipo recomendacion',11,'delete_tiporecomendacion'),(44,'Can view tipo recomendacion',11,'view_tiporecomendacion'),(45,'Can add usuario',12,'add_usuario'),(46,'Can change usuario',12,'change_usuario'),(47,'Can delete usuario',12,'delete_usuario'),(48,'Can view usuario',12,'view_usuario'),(49,'Can add gestion empresa',13,'add_gestionempresa'),(50,'Can change gestion empresa',13,'change_gestionempresa'),(51,'Can delete gestion empresa',13,'delete_gestionempresa'),(52,'Can view gestion empresa',13,'view_gestionempresa'),(53,'Can add recomendacion',14,'add_recomendacion'),(54,'Can change recomendacion',14,'change_recomendacion'),(55,'Can delete recomendacion',14,'delete_recomendacion'),(56,'Can view recomendacion',14,'view_recomendacion'),(57,'Can add aprobacion recomendacion',15,'add_aprobacionrecomendacion'),(58,'Can change aprobacion recomendacion',15,'change_aprobacionrecomendacion'),(59,'Can delete aprobacion recomendacion',15,'delete_aprobacionrecomendacion'),(60,'Can view aprobacion recomendacion',15,'view_aprobacionrecomendacion'),(61,'Can add reporte',16,'add_reporte'),(62,'Can change reporte',16,'change_reporte'),(63,'Can delete reporte',16,'delete_reporte'),(64,'Can view reporte',16,'view_reporte'),(65,'Can add recomendacion guardada',17,'add_recomendacionguardada'),(66,'Can change recomendacion guardada',17,'change_recomendacionguardada'),(67,'Can delete recomendacion guardada',17,'delete_recomendacionguardada'),(68,'Can view recomendacion guardada',17,'view_recomendacionguardada'),(69,'Can add me gusta',18,'add_megusta'),(70,'Can change me gusta',18,'change_megusta'),(71,'Can delete me gusta',18,'delete_megusta'),(72,'Can view me gusta',18,'view_megusta'),(73,'Can add gestion usuario',19,'add_gestionusuario'),(74,'Can change gestion usuario',19,'change_gestionusuario'),(75,'Can delete gestion usuario',19,'delete_gestionusuario'),(76,'Can view gestion usuario',19,'view_gestionusuario');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
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
