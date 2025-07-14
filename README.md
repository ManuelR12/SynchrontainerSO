
# 1. Configuración Inicial
Clonar el Repositorio:

git clone https://github.com/ManuelR12/SynchrontainerSO.git

Descargar la Imagen Docker Base:
docker pull manuelr12/synchrontainer-image:v1.2

(Si necesitan modificar requirements o Dockerfile tienen que avisarme para modificar la imagen).

# 2. Ejecutar la Aplicación (Modo Desarrollo)
Para que tus cambios en el código local se reflejen al instante en el contenedor:

Windows (CMD/PowerShell):

docker run -it --rm -p 5000:5000 -v "C:\Users\juanr\OneDrive\Escritorio\so-course-2023\myapp:/usr/src/app" --name synchro-dev-container manuelr12/synchrontainer-image:v1.2 python3 ./app.py 

(CAMBIAS MI RUTA POR LA TUYA)

Mac/Linux (o Git Bash en Windows):

docker run -it --rm -p 5000:5000 -v "$(pwd)/myapp:/usr/src/app" --name synchro-dev-container manuelr12/synchrontainer-image:v1.2 python3 ./app.py

(NO VAYA A CERRAR LA TERMINAL)

# 3. Probar Endpoints
Con el contenedor ejecutándose, abre el navegador y visita:

http://localhost:5000/

http://localhost:5000/despedirse

http://localhost:5000/public/

http://localhost:5000/storage/current

Para probar subida y descarga, usa el upload_test.html (lo añado para que puedas copiar el html y ponerlo en donde quieras en tu PC).

# 4. Flujo de Trabajo para Cambios (AUNQUE QUIZAS SOLO HAGAMOS CAMBIOS EN app.py)
A. Cambios en el Código (app.py, etc. dentro de myapp/)
Edita los archivos de código localmente.

Los cambios se reflejan automáticamente en el contenedor (puede que necesites reiniciar el contenedor si no se recarga solo).

Sube tus cambios a Git (git add, git commit, git push).


B. Cambios en la Configuración Base (Dockerfile, requirements.txt)

Modifica Dockerfile o requirements.txt.

Reconstruye la imagen con una nueva versión:

docker build -t manuelr12/synchrontainer-image:v1.3 . # Para este punto estamos en la version 1.2

Sube la nueva imagen a Docker Hub:

docker push manuelr12/synchrontainer-image:v1.3

Comunica al equipo la nueva etiqueta de versión.

Sube también los cambios del Dockerfile/requirements.txt a Git.

