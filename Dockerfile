# imagen base
FROM python:3

# establece el directorio de trabajo
WORKDIR /usr/src/app

# Copiar la carpeta myapp a /usr/src/app
COPY ./myapp/ .

# instalacion de requerimientos y dependencias
RUN pip3 install -r requirements.txt

# *************************************************************************
# MODIFICACIÓN CLAVE: Crear las carpetas sync_files, public y private
# *************************************************************************

# Crea la carpeta principal 'sync_files' en la raíz del contenedor
# (o puedes especificar /usr/src/app/sync_files si prefieres que esté dentro de tu WORKDIR)
RUN mkdir -p /sync_files

# Crea las subcarpetas 'public' y 'private' dentro de 'sync_files'
RUN mkdir -p /sync_files/public
RUN mkdir -p /sync_files/private

# Opcional pero recomendado: Establece permisos de escritura para que la aplicación
# pueda crear y modificar archivos dentro de estas carpetas.
# Esto asume que tu aplicación Python se ejecuta con un usuario que necesita estos permisos.
RUN chmod -R 777 /sync_files

# *************************************************************************
# Fin de la MODIFICACIÓN CLAVE
# *************************************************************************

# Aperturo el puerto 5000 del contenedor
EXPOSE 5000

# Establece el entrypoint
CMD ["python3", "./app.py"]
