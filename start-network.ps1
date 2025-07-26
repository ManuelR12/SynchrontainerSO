$DockerHubUser = "manuelr12"
$ImageTag = "v-final" 

$ImageName = "$DockerHubUser/synchrontainer-image:$ImageTag"
$NodeNames = "c1,c2,c3,c4"
$NetworkName = "synchro-net"

Write-Host "Limpiando contenedores antiguos (c1, c2, c3, c4)..."
docker stop c1 c2 c3 c4 2>$null
docker rm c1 c2 c3 c4 2>$null

Write-Host "Usando la imagen: $ImageName"
Write-Host "Lanzando red de contenedores..."

docker run -d --rm --name c1 --network $NetworkName -e SYNCHRO_NODES=$NodeNames -e SYNCHRO_NAME="c1" -p 5001:5000 $ImageName
docker run -d --rm --name c2 --network $NetworkName -e SYNCHRO_NODES=$NodeNames -e SYNCHRO_NAME="c2" -p 5002:5000 $ImageName
docker run -d --rm --name c3 --network $NetworkName -e SYNCHRO_NODES=$NodeNames -e SYNCHRO_NAME="c3" -p 5003:5000 $ImageName
docker run -d --rm --name c4 --network $NetworkName -e SYNCHRO_NODES=$NodeNames -e SYNCHRO_NAME="c4" -p 5004:5000 $ImageName

Start-Sleep -Seconds 3

Write-Host "¡Éxito! La red de contenedores está corriendo."
Write-Host "Para ver el estado, abre otra terminal y ejecuta 'docker ps'."