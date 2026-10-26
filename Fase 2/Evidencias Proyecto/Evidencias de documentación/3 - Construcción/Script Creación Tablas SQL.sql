CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    p_nombre VARCHAR(255),
    p_apellido VARCHAR(255),
    foto_perfil LONGBLOB,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    nombre_empresa VARCHAR(255) NOT NULL,
    foto_perfil LONGBLOB,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE administrador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(255) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);

CREATE TABLE tipo_recomendacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE genero (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE estado_aprobacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE recomendacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    empresa_id INT,
    tipo_id INT NOT NULL,
    genero_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    resumen TEXT,
    trivia TEXT,
    frase_destacada TEXT,
    portada LONGBLOB,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_aprobacion_id INT DEFAULT 1,
    administrador_id INT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE SET NULL,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE SET NULL,
    FOREIGN KEY (tipo_id) REFERENCES tipo_recomendacion(id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES genero(id) ON DELETE CASCADE,
    FOREIGN KEY (estado_aprobacion_id) REFERENCES estado_aprobacion(id) ON DELETE RESTRICT,
    FOREIGN KEY (administrador_id) REFERENCES administrador(id) ON DELETE SET NULL
);

CREATE TABLE recomendacion_guardada (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    recomendacion_id INT NOT NULL,
    fecha_guardado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (recomendacion_id) REFERENCES recomendacion(id) ON DELETE CASCADE
);

CREATE TABLE me_gusta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    recomendacion_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (recomendacion_id) REFERENCES recomendacion(id) ON DELETE CASCADE
);

CREATE TABLE reporte (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    recomendacion_id INT NOT NULL,
    motivo TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (recomendacion_id) REFERENCES recomendacion(id) ON DELETE CASCADE
);

CREATE TABLE gestion_usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    administrador_id INT NOT NULL,
    usuario_id INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (administrador_id) REFERENCES administrador(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE gestion_empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    administrador_id INT NOT NULL,
    empresa_id INT NOT NULL,
    accion VARCHAR(50) NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (administrador_id) REFERENCES administrador(id) ON DELETE CASCADE,
    FOREIGN KEY (empresa_id) REFERENCES empresa(id) ON DELETE CASCADE
);

CREATE TABLE aprobacion_recomendacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    administrador_id INT NOT NULL,
    recomendacion_id INT NOT NULL,
    estado_aprobacion_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    comentario TEXT,
    FOREIGN KEY (administrador_id) REFERENCES administrador(id) ON DELETE CASCADE,
    FOREIGN KEY (recomendacion_id) REFERENCES recomendacion(id) ON DELETE CASCADE,
    FOREIGN KEY (estado_aprobacion_id) REFERENCES estado_aprobacion(id) ON DELETE RESTRICT
);
