# Urban Sensor: Sistema de Gestión de Incidencias Municipales

`Urban Sensor` es una plataforma web diseñada para centralizar y gestionar el flujo de incidencias dentro de una municipalidad. Permite a los administradores (SECPLA) configurar la estructura organizacional (Direcciones, Departamentos) y a los usuarios de terreno (Territoriales) reportar incidencias que son luego derivadas y resueltas por las Cuadrillas.

---

## 🚀 Tecnologías Utilizadas

Este proyecto está construido siguiendo las especificaciones del "Tutorial 01 - Primer Proyecto Django", utilizando:

* **Python:** `Python 3.11`
* **Framework Backend:** `Django 5.2.4`
* **Base de Datos:** `PostgreSQL`
* **Conector de Base de Datos:** `psycopg2-binary 2.9.10`
* **Frontend:** `HTML`, `CSS`, `JavaScript`
* **Librerías Frontend:** `Chart.js` (para los gráficos del dashboard)

---

## 🌟 Características Principales

El sistema se divide en varios módulos clave:

* **Gestión de Registro y Perfiles:** Control de acceso y autenticación.
* **Gestión de Estructura:**
    * Módulo de **Direcciones**
    * Módulo de **Departamentos**
* **Gestión de Incidencias:**
    * Módulo de **Tipos de Incidencia**
    * Módulo de **Encuestas** (usadas como plantillas para crear reportes)
    * Módulo de **Solicitudes de Incidencia** (los reportes reales)
* **Dashboards por Perfil:** Vistas personalizadas para cada rol.

---

## 👥 Perfiles de Usuario

El sistema maneja 5 roles de usuario, cada uno con permisos específicos:

1.  **SECPLA (Administrador):** Tiene control total. Crea usuarios, direcciones, departamentos y las plantillas de encuesta.
2.  **Dirección:** Supervisa las incidencias asignadas a los departamentos bajo su cargo.
3.  **Departamento:** Recibe incidencias, las revisa y las deriva a las Cuadrillas.
4.  **Territorial:** El usuario en terreno. Crea nuevas incidencias (Solicitudes) usando las Encuestas como plantillas.
5.  **Cuadrilla:** El personal que resuelve las incidencias y reporta su finalización.

---

## ⚙️ Instalación y Puesta en Marcha

Para ejecutar este proyecto localmente, sigue estos pasos:

### 1. Configuración del Entorno (Conda)

Se recomienda usar `conda` para gestionar el entorno, tal como se especifica en el tutorial.

```bash
# 1. Crea y activa un nuevo entorno con Python 3.11
conda create -n urban_sensor_env python=3.11

conda activate urban_sensor_env

2. Instalación de Dependencias
Instala las librerías necesarias para el proyecto:



pip install -r requirements.txt

3. Base de Datos
Asegúrate de tener PostgreSQL configurado y aplica las migraciones:


python manage.py migrate

# 1. Inicializar Perfiles
# Crea la estructura base de perfiles en la base de datos.
python manage.py create-profiles

# 2. Crear Administrador (SECPLA)
# Genera el usuario administrador principal del sistema.
python manage.py create-secpla


Crear usuarios ficticios para cada rol (Dirección, Departamento, Cuadrilla, Territorial)
ideal para probar el flujo completo de la aplicación.
python manage.py create-test

Ejecutar el Servidor
Finalmente, inicia el servidor de desarrollo:

python manage.py runserver

La contraseña de los usuarios creados por create-test es "1234"