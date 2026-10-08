# 🎬 Discover

> Plataforma inteligente de recomendaciones de entretenimiento desarrollada con Django, Django REST Framework, MySQL e inteligencia artificial.

**Discover** es una plataforma web orientada al descubrimiento de contenido de entretenimiento. Permite a los usuarios explorar y descubrir **películas,
videojuegos, libros y música** mediante recomendaciones organizadas por categorías y géneros.

El sistema incorpora funcionalidades basadas en **inteligencia artificial mediante la API de Google Gemini**, utilizadas para asistir en la generación y 
elaboración del contenido de las recomendaciones.

La arquitectura del proyecto utiliza **Django como framework principal**, junto con **Django REST Framework (DRF)** para la implementación de servicios y 
endpoints mediante una **API REST**, permitiendo la comunicación estructurada entre las distintas funcionalidades de la aplicación.

## 📌 Características principales

* 🎬 Recomendaciones de **películas**
* 🎮 Recomendaciones de **videojuegos**
* 📚 Recomendaciones de **libros**
* 🎵 Recomendaciones de **música**
* 🔎 Exploración por tipo y género
* 🤖 Generación de contenido mediante **Google Gemini**
* 🌐 API REST desarrollada con **Django REST Framework**
* 👤 Sistema de usuarios
* 🏢 Gestión de recomendaciones para empresas
* 🛠️ Panel de administración
* 🔐 Gestión de acceso según tipo de usuario
* 🗄️ Persistencia de información mediante **MySQL**
* 🔊 Generación de contenido de audio mediante inteligencia artificial
* 🃏 Interfaz interactiva para visualizar información adicional de cada recomendación

---

## 🧠 Inteligencia Artificial

Discover integra la **API de Google Gemini** para asistir en la generación de contenido asociado a las recomendaciones.

La inteligencia artificial puede utilizarse para generar o sugerir información como:

* Títulos
* Descripciones
* Resúmenes
* Trivia
* Frases destacadas
* Contenido complementario para las recomendaciones

Además, el proyecto incorpora funcionalidades de **síntesis de voz (TTS)** para permitir la reproducción mediante audio del contenido generado.

---

## 🌐 API REST

Uno de los componentes principales de Discover es su **API REST**, desarrollada utilizando **Django REST Framework**.

La API permite gestionar y exponer información de la plataforma mediante endpoints HTTP, facilitando la comunicación entre el backend y las diferentes
funcionalidades del sistema.

### Componentes utilizados

* **Django REST Framework**
* Serializers
* Views / API Views
* Endpoints HTTP
* Métodos `GET`, `POST`, `PUT` y `DELETE` según la funcionalidad
* Manejo de respuestas en formato JSON
* Integración con los modelos de Django
* Comunicación con la base de datos MySQL

De esta manera, Django cumple tanto el rol de framework principal de la aplicación como de backend para los servicios REST.

---

## 👥 Tipos de usuario

### 👤 Usuario

Puede:

* Explorar recomendaciones.
* Filtrar contenido.
* Visualizar información detallada.
* Consultar diferentes categorías.
* Escuchar el contenido mediante audio cuando esté disponible.

### 🏢 Empresa

Puede:

* Gestionar recomendaciones.
* Crear contenido promocional.
* Administrar sus propias publicaciones.
* Utilizar inteligencia artificial para asistir en la creación del contenido.

### ⚙️ Administrador

Cuenta con funcionalidades de administración y gestión general de la plataforma.

---

## 🛠️ Tecnologías utilizadas

### Backend

* **Python**
* **Django**
* **Django REST Framework**
* **MySQL**

### Frontend

* HTML5
* CSS3
* JavaScript
* Django Templates

### API

* **REST API**
* **Django REST Framework**
* JSON
* HTTP

### Inteligencia Artificial

* **Google Gemini API**
* Modelos generativos de texto
* Tecnología Text-to-Speech (TTS)

### Herramientas

* Git
* GitHub
* Visual Studio

---

## 🏗️ Arquitectura general

```text
                         ┌─────────────────────┐
                         │       Usuario       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Interfaz Web     │
                         │   HTML / CSS / JS   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Django        │
                         │      Backend        │
                         └──────┬────────┬─────┘
                                │        │
                   ┌────────────┘        └─────────────┐
                   ▼                                   ▼
          ┌──────────────────┐                 ┌─────────────────┐
          │ Django REST      │                 │   Django Views  │
          │ Framework        │                 │ / Templates     │
          │                  │                 │                 │
          │     REST API     │                 │   Aplicación    │
          └────────┬─────────┘                 │      Web        │
                   │                           └─────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │      MySQL       │
          │   Base de datos  │
          └──────────────────┘

                         ┌──────────────────┐
                         │    Gemini API    │
                         │ Inteligencia     │
                         │    Artificial    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │       TTS        │
                         │      Audio       │
                         └──────────────────┘
```

---

## 📂 Estructura del proyecto

El repositorio se encuentra organizado por las diferentes fases de desarrollo del proyecto:

```text
Discover/
│
├── Fase 1/
│
├── Fase 2/
│
├── Fase 3/
│
└── README.md
```

Las diferentes fases contienen los avances y entregables correspondientes al desarrollo de Discover.

---

# 👨‍💻 Autores

**Jordán Órdenes**

**Lino Barrera**

**Analista Programador**
**Ingeniería en Informática**

Proyecto desarrollado como parte del proceso académico de **Ingeniería en Informática — DUOC UC**.

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos y de aprendizaje.
