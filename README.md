# Synchrontainer - Proyecto Final
Este proyecto implementa un sistema de archivos distribuido utilizando una red de contenedores Docker. Permite la publicación, réplica y recuperación de archivos entre los nodos de la red, demostrando conceptos de sistemas operativos, redes y contenerización.

# Tecnologías Principales:
- Contenerización: Docker
- Backend: Python con Flask
- Comunicación en Red: HTTP (Librería requests)
- Scripting de Despliegue: PowerShell

# Clonar el Repositorio:
git clone https://github.com/ManuelR12/SynchrontainerSO.git
cd SynchrontainerSO

# Construir la Imagen Docker:
docker build -t manuelr12/synchrontainer-image:v-2.2 .

# Crear la Red Virtual:
docker network create synchro-net

# Ejecutar el Script de Despliegue:
powershell.exe -ExecutionPolicy Bypass -File .\start-network.ps1

# Para verificar
docker ps

# Abrir la Herramienta de Carga:
Abre el archivo upload_test.html en el navegador.

# Caso de Prueba #1: Subir archivos a diferentes nodos y carpetas
Acción 1: Subir un archivo al contenedor c1 en la carpeta public.
Acción 2: Subir un archivo al contenedor c1 en la carpeta private.
Acción 3: Subir un archivo al contenedor c2 en la carpeta public.
Acción 4: Subir un archivo al contenedor c3 en la carpeta private.


# Caso de Prueba #2: Listar el contenido de un contenedor específico (/storage)
Abrir el siguiente link.
http://localhost:5001/storage/c1
Este endpoint muestra tanto los archivos públicos como los privados del contenedor c1.

# Caso de Prueba #3: Listar TODOS los archivos de la Red (/public)
Abrir este link.
http://localhost:5002/public/
Se le estamos pide a c2 que muestre todos los archivos públicos. c2 se comunica con el resto de la red (c1 y c3), recopila la información y la presenta.

# Caso de Prueba #4: Descarga en Red
Intentar descargar un archivo que solo existe en c2, pero pidiéndoselo a c3.
http://localhost:5003/download/(nombreDelArchivoEnc2)
Se demuestra la descarga en red. El contenedor c3 no tiene este archivo, pero es lo busca en la red creada, lo encuentra en c2, lo obtiene y lo presenta. Esto completa el ciclo de replicación y recuperación de archivos.

# Detener la Red
docker stop c1 c2 c3