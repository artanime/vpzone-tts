<#
.SYNOPSIS
    Descarga modelos de voz de Piper (TTS offline) a voices/piper.

.DESCRIPTION
    Los modelos de Piper son un par de ficheros por voz: <nombre>.onnx (el modelo)
    y <nombre>.onnx.json (su configuracion). Ambos se publican en
    https://huggingface.co/rhasspy/piper-voices.

    Este script los descarga sin necesidad de Python ni de la app instalada.
    Los deja en voices/piper/ y aparecen automaticamente en el desplegable de
    voces de la app (proveedor Piper), sin tocar la configuracion.

    Cada voz tiene su propia licencia de dataset. Consulta la columna "Licencia"
    de voices/README.md antes de redistribuir los modelos: las marcadas como
    uso restringido (no comercial o investigacion) no deberias publicarlas.

    SEGURIDAD
    ---------
    - Solo se descarga por HTTPS desde hosts de HuggingFace; si la descarga
      acaba en otro host, se aborta.
    - Cada fichero se comprueba contra su tamano exacto y su SHA-256 oficial
      (el .onnx es el hash LFS que publica HuggingFace; el .onnx.json se fijo
      a partir del fichero publicado). Si no coincide, se borra y se aborta:
      nunca se deja un modelo sin verificar en la carpeta.
    - La descarga va a un fichero temporal .part y solo se mueve a su sitio
      cuando la verificacion ha pasado.
    - Los nombres de fichero se validan y no pueden salir de la carpeta de
      destino (sin path traversal).
    - Los modelos se tratan como datos: nunca se ejecutan.

.PARAMETER Voz
    Identificadores de las voces a instalar (ej. en_US-amy-medium).

.PARAMETER Publicas
    Instala todas las voces con licencia de redistribucion libre (CC0, dominio
    publico, Apache-2.0, CC BY, CC BY-SA, AGPL-3.0).

.PARAMETER Todas
    Instala todo el catalogo, incluidas las voces de uso restringido.

.PARAMETER Listar
    Muestra el catalogo disponible y termina.

.PARAMETER Verificar
    Comprueba los ficheros ya instalados contra sus hashes oficiales y no
    descarga nada.

.PARAMETER Destino
    Carpeta donde se guardan los modelos. Por defecto voices/piper.

.PARAMETER Forzar
    Vuelve a descargar las voces que ya estan instaladas.

.EXAMPLE
    .\voices\instalar_voces.ps1 -Listar

.EXAMPLE
    .\voices\instalar_voces.ps1 -Voz en_US-amy-medium, fr_FR-siwis-medium

.EXAMPLE
    .\voices\instalar_voces.ps1 -Publicas

.EXAMPLE
    .\voices\instalar_voces.ps1 -Verificar

.EXAMPLE
    .\voices\instalar_voces.ps1 -Voz en_US-joe-medium -Forzar
#>

[CmdletBinding(DefaultParameterSetName = 'Publicas')]
param(
    [Parameter(ParameterSetName = 'Voz')]
    [string[]] $Voz,

    [Parameter(ParameterSetName = 'Publicas')]
    [switch] $Publicas,

    [Parameter(ParameterSetName = 'Todas')]
    [switch] $Todas,

    [Parameter(ParameterSetName = 'Listar')]
    [switch] $Listar,

    [Parameter(ParameterSetName = 'Verificar')]
    [switch] $Verificar,

    [string] $Destino,

    [switch] $Forzar
)

$ErrorActionPreference = 'Stop'

# PS 5.1 renderiza la barra de progreso en cada bloque y ralentiza mucho la
# descarga de binarios de 60 MB. Se desactiva para la sesion.
$ProgressPreference = 'SilentlyContinue'

# HuggingFace exige TLS 1.2; PS 5.1 puede venir con SSL3/TLS1.0 por defecto.
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$Base = 'https://huggingface.co/rhasspy/piper-voices/resolve/main'

# Hosts a los que puede acabar redirigida la descarga (HuggingFace y su CDN).
$HostsPermitidos = @('huggingface.co', 'hf.co')

# Catalogo de voces. Los datos de integridad viven en $Huellas, unas lineas mas
# abajo: Bytes/Sha256 son los que publica HuggingFace para el .onnx (LFS) y
# JsonBytes/JsonSha se calcularon del .onnx.json publicado. El script comprueba
# que cada voz del catalogo tenga su huella antes de descargar nada.
$Catalogo = @(
    # --- Espanol (ES) ---
    [pscustomobject]@{ Id = 'es_ES-davefx-medium';    Ruta = 'es/es_ES/davefx/medium';    Licencia = 'CC0';             Publica = $true;  Nota = 'Voz por defecto' }
    [pscustomobject]@{ Id = 'es_ES-sharvard-medium';  Ruta = 'es/es_ES/sharvard/medium';  Licencia = 'CC BY 3.0';       Publica = $true;  Nota = 'Espanol (ES)' }

    # --- Ingles (US) ---
    [pscustomobject]@{ Id = 'en_US-amy-medium';       Ruta = 'en/en_US/amy/medium';       Licencia = 'CC BY-SA 4.0';    Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_US-joe-medium';       Ruta = 'en/en_US/joe/medium';       Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-mike-medium';      Ruta = 'en/en_US/mike/medium';      Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-sam-medium';       Ruta = 'en/en_US/sam/medium';       Licencia = 'Apache-2.0';      Publica = $true;  Nota = 'No binaria' }
    [pscustomobject]@{ Id = 'en_US-kristin-medium';   Ruta = 'en/en_US/kristin/medium';   Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_US-john-medium';      Ruta = 'en/en_US/john/medium';      Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-bryce-medium';     Ruta = 'en/en_US/bryce/medium';     Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-norman-medium';    Ruta = 'en/en_US/norman/medium';    Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-ljspeech-medium';  Ruta = 'en/en_US/ljspeech/medium';  Licencia = 'Dominio publico'; Publica = $true;  Nota = 'LJSpeech' }

    # --- Ingles (GB) ---
    [pscustomobject]@{ Id = 'en_GB-cori-medium';      Ruta = 'en/en_GB/cori/medium';      Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_GB-alba-medium';      Ruta = 'en/en_GB/alba/medium';      Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_GB-alan-medium';      Ruta = 'en/en_GB/alan/medium';      Licencia = 'CC BY-SA 4.0';    Publica = $true;  Nota = 'Masculina' }

    # --- Frances ---
    [pscustomobject]@{ Id = 'fr_FR-siwis-medium';     Ruta = 'fr/fr_FR/siwis/medium';     Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'fr_FR-upmc-medium';      Ruta = 'fr/fr_FR/upmc/medium';      Licencia = 'CC BY-SA 4.0';    Publica = $true;  Nota = '2 hablantes' }
    [pscustomobject]@{ Id = 'fr_FR-tom-medium';       Ruta = 'fr/fr_FR/tom/medium';       Licencia = 'AGPL-3.0';        Publica = $true;  Nota = 'Masculina, 44.1 kHz' }
    [pscustomobject]@{ Id = 'fr_FR-gilles-low';       Ruta = 'fr/fr_FR/gilles/low';       Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina, calidad baja' }
    [pscustomobject]@{ Id = 'fr_FR-mls_1840-low';     Ruta = 'fr/fr_FR/mls_1840/low';     Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Masculina, 1840' }
    [pscustomobject]@{ Id = 'fr_FR-mls-medium';       Ruta = 'fr/fr_FR/mls/medium';       Licencia = 'CC BY 4.0';       Publica = $true;  Nota = '125 hablantes' }

    # --- Uso restringido: uso personal, no redistribuir ---
    [pscustomobject]@{ Id = 'en_US-ryan-medium';      Ruta = 'en/en_US/ryan/medium';      Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-lessac-medium';    Ruta = 'en/en_US/lessac/medium';    Licencia = 'Blizzard 2013';   Publica = $false; Nota = 'Solo investigacion' }
    [pscustomobject]@{ Id = 'en_US-kusal-medium';     Ruta = 'en/en_US/kusal/medium';     Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-hfc_female-medium'; Ruta = 'en/en_US/hfc_female/medium'; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-hfc_male-medium';  Ruta = 'en/en_US/hfc_male/medium';  Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_GB-semaine-medium';   Ruta = 'en/en_GB/semaine/medium';   Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
)

# Huellas de integridad por voz. Bytes/Sha256 = .onnx (hash LFS de HuggingFace).
# JsonBytes/JsonSha = .onnx.json. Si HuggingFace actualiza un modelo, la descarga
# fallara a proposito hasta que se actualice esta tabla en el repositorio.
$Huellas = @{
    'es_ES-davefx-medium'    = @{ Bytes = 63201294; Sha256 = '6658b03b1a6c316ee4c265a9896abc1393353c2d9e1bca7d66c2c442e222a917'; JsonBytes = 4817; JsonSha = '0e0dda87c732f6f38771ff274a6380d9252f327dca77aa2963d5fbdf9ec54842' }
    'es_ES-sharvard-medium'  = @{ Bytes = 76733615; Sha256 = '40febfb1679c69a4505ff311dc136e121e3419a13a290ef264fdf43ddedd0fb1'; JsonBytes = 4903; JsonSha = '7438c9b699c72b0c3388dae1b68d3f364dc66a2150fe554a1c11f03372957b2c' }
    'en_US-amy-medium'       = @{ Bytes = 63201294; Sha256 = 'b3a6e47b57b8c7fbe6a0ce2518161a50f59a9cdd8a50835c02cb02bdd6206c18'; JsonBytes = 4882; JsonSha = '95a23eb4d42909d38df73bb9ac7f45f597dbfcde2d1bf9526fdeaf5466977d77' }
    'en_US-joe-medium'       = @{ Bytes = 63201294; Sha256 = '58afce0321b8d9c46d7cdf9c16500cc55a793b4220212dba6b70fb788b3baf06'; JsonBytes = 4794; JsonSha = '3d6d5410b3795cb1950595247ef8f06190719e6fdbfa3a2356d8ec368e1aad33' }
    'en_US-mike-medium'      = @{ Bytes = 63221984; Sha256 = '3157e69e2c580cab297483f4b301ee975a4590c17d35a9757e33347d0e90fae2'; JsonBytes = 5439; JsonSha = '0a2538c0b1e06a6cab7c46b97c79abd5e6a34a6c05b74b9376874c7099d81dad' }
    'en_US-sam-medium'       = @{ Bytes = 62950044; Sha256 = '56417b3b4afe8ec6bb4cabf06e17d67261fdd5bf334592abcfc80052fba11163'; JsonBytes = 5040; JsonSha = '8c7fb47f19683b0b81037c5564f9a5ad4699a9da685e0e5da0a72fd3c3f5c1c4' }
    'en_US-kristin-medium'   = @{ Bytes = 63531379; Sha256 = '5849957f929cbf720c258f8458692d6103fff2f0e3d3b19c8259474bb06a18d4'; JsonBytes = 4968; JsonSha = '5681426d4aead22195de70531eeeeddb46493cfaffc5764b2ea3db73428b651c' }
    'en_US-john-medium'      = @{ Bytes = 63531379; Sha256 = '789c6c875726e627ddee93d51d8727859abe9c091c3d141591f4b83c2072e988'; JsonBytes = 4965; JsonSha = 'af60f177b6b550f3d7a302720c0fb89e7f94a82b5dca464775ef63b1c69ba09a' }
    'en_US-bryce-medium'     = @{ Bytes = 63531379; Sha256 = 'dc9caa6c313199ffb5ac698b6e542fa6cba388aeaf2731e25262e33b9810aef1'; JsonBytes = 4966; JsonSha = '7ceb1bc4af6d4e41b6d1edbb86c67e91e01eaa71f66db4cd0ae92ac704d415be' }
    'en_US-norman-medium'    = @{ Bytes = 63531379; Sha256 = 'b9739443232a80a59c7d18810dd856899bf16a7964725f5ab81ea49b1351cb71'; JsonBytes = 4968; JsonSha = '6c2db7f558a4a8deb9fe822583c1c5105f6c4e834dd0f9de8ad17a888ee9fe1d' }
    'en_US-ljspeech-medium'  = @{ Bytes = 63531379; Sha256 = '6f52a751e2349abe7a76735eb09dc1875298c77ea2342ffd2fef79ff81b87f22'; JsonBytes = 4972; JsonSha = '141d612cc0a95ed7efc1ca936b845c2364967f2e9217c5dbfcf69fc4d6c65860' }
    'en_GB-cori-medium'      = @{ Bytes = 63531379; Sha256 = '1899f98e5fb8310154f3c2973f4b8a929ba7245e722b3d3a85680b833d95f10d'; JsonBytes = 4966; JsonSha = 'e262c16d7f192f69d4edd6b4ef8a5915379e67495fcc402f1ab15eeb33da3d36' }
    'en_GB-alba-medium'      = @{ Bytes = 63201294; Sha256 = '401369c4a81d09fdd86c32c5c864440811dbdcc66466cde2d64f7133a66ad03b'; JsonBytes = 4888; JsonSha = 'aa965a2f02ecced632c2694e1fc72bbff6d65f265fab567ca945918c73dd89f4' }
    'en_GB-alan-medium'      = @{ Bytes = 63201294; Sha256 = '0a309668932205e762801f1efc2736cd4b0120329622adf62be09e56339d3330'; JsonBytes = 4888; JsonSha = 'c0f0d124e5895c00e7c03b35dcc8287f319a6998a365b182deb5c8e752ee8c1e' }
    'fr_FR-siwis-medium'     = @{ Bytes = 63201294; Sha256 = '641d1ab097da2b81128c076810edb052b385decc8be3381814802a64a73baf99'; JsonBytes = 4875; JsonSha = '39479916c2db192b5ac9764daddd0c744d83e023ad890c6976c0633ae4df8959' }
    'fr_FR-upmc-medium'      = @{ Bytes = 76733615; Sha256 = '9abb3800c199148897a9ed64e100d224f3de83579f100044174ad19418f1786f'; JsonBytes = 4996; JsonSha = 'e8636ec15dfd5d72db37a02cb5320a20f2b8d339f2a0e4337da64c58a33a5868' }
    'fr_FR-tom-medium'       = @{ Bytes = 63511038; Sha256 = 'bf65074ccdeeeeaa832e75edb1c0a513c01c9a972bdf085ff8a6e71ea234fd41'; JsonBytes = 4959; JsonSha = '2f7f885ad5a0aad802e3cc24e4f57239febdcb142b4876de5d238094674361cc' }
    'fr_FR-gilles-low'       = @{ Bytes = 63104526; Sha256 = '5cd711846720e261c2a176f6924c198a7424d0a75dd4b0a5357a5fb9cb739285'; JsonBytes = 4158; JsonSha = '5a47cc0789e91267d17666bbec842dd92950669271a09023eb6970ee364cf88a' }
    'fr_FR-mls_1840-low'     = @{ Bytes = 63104526; Sha256 = 'dcea3d495b760f168179b6bd27c7daefa1d8304ce6ec48867e42bae7cb2e507a'; JsonBytes = 4160; JsonSha = '294a643de0ae6a4a885d841d9b74470263efe35c81e7cf37dd43e2d663fbd8b3' }
    'fr_FR-mls-medium'       = @{ Bytes = 76733750; Sha256 = '0ed223f78466917f2bae05ee90096ce69ab1fdeb251f55590d0e7422d234e162'; JsonBytes = 7036; JsonSha = '252b0b0a6e4cc4949e23eccb956f9c779986c32f934f2f7e2191e5fdc2edca61' }
    'en_US-ryan-medium'      = @{ Bytes = 63201294; Sha256 = 'abf4c274862564ed647ba0d2c47f8ee7c9b717d27bdad9219100eb310db4047a'; JsonBytes = 4883; JsonSha = '44034c056cb15681b2ad494307c7f3f2e4499d1253c700c711fa0a4607ffe78d' }
    'en_US-lessac-medium'    = @{ Bytes = 63201294; Sha256 = '5efe09e69902187827af646e1a6e9d269dee769f9877d17b16b1b46eeaaf019f'; JsonBytes = 4885; JsonSha = 'efe19c417bed055f2d69908248c6ba650fa135bc868b0e6abb3da181dab690a0' }
    'en_US-kusal-medium'     = @{ Bytes = 63201294; Sha256 = '438ae25bb305b2a7f6d632327d6102df25011f793e8222fa9db876e7321df8f3'; JsonBytes = 4884; JsonSha = 'ddd3c4dfd8b4f568150c934fb94912dd788d44db87f4f0a328c469d7a6761f41' }
    'en_US-hfc_female-medium' = @{ Bytes = 63201294; Sha256 = '914c473788fc1fa8b63ace1cdcdb44588f4ae523d3ab37df1536616835a140b7'; JsonBytes = 5033; JsonSha = '03f1fa0622b80463283592d97aca9f6e89aec345a5c56b7257723e0093c58b6c' }
    'en_US-hfc_male-medium'  = @{ Bytes = 63201294; Sha256 = 'd11e403a02bdf5a670c877b3dc56e0e1c8cece6fb30289586314dffdc0a78cb0'; JsonBytes = 5033; JsonSha = 'f66847424aed0bf99ecbb5d7cfde47c0a906f426a0daf7c46f305e7d21afd886' }
    'en_GB-semaine-medium'   = @{ Bytes = 76737711; Sha256 = 'd6dab6f3b92db43ea3f78c7f20dc8eadb47a1f15d8a1c9d451cf3ccd201a2f66'; JsonBytes = 5076; JsonSha = '6425dcb878684043b77d772b173ae006d86a583b110303edda48b8438ecee5ee' }
}

if (-not $Destino) {
    $Destino = Join-Path $PSScriptRoot 'piper'
}

function Format-MB {
    param([long] $Bytes)
    return ('{0,6:N1} MB' -f ($Bytes / 1MB))
}

function Get-Sha256 {
    param([string] $RutaArchivo)
    return (Get-FileHash -LiteralPath $RutaArchivo -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-HostPermitido {
    param([string] $HostName)

    if (-not $HostName) { return $false }

    $h = $HostName.ToLowerInvariant()

    foreach ($permitido in $HostsPermitidos) {
        if ($h -eq $permitido) { return $true }
        if ($h.EndsWith('.' + $permitido)) { return $true }
    }

    return $false
}

function Assert-RutaSegura {
    param([string] $RutaArchivo)

    $nombre = Split-Path -Leaf $RutaArchivo
    if ($nombre -notmatch '^[A-Za-z0-9._-]+$') {
        throw "nombre de fichero no permitido: $nombre"
    }

    $destinoCompleto = [System.IO.Path]::GetFullPath($Destino).TrimEnd([char[]]@('\', '/'))
    $archivoCompleto = [System.IO.Path]::GetFullPath($RutaArchivo)
    $prefijo = $destinoCompleto + [System.IO.Path]::DirectorySeparatorChar

    if (-not $archivoCompleto.StartsWith($prefijo, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "la ruta se sale de la carpeta de destino: $RutaArchivo"
    }
}

function Get-EstadoFichero {
    param([string] $RutaArchivo, [long] $BytesEsperados, [string] $ShaEsperado)

    if (-not (Test-Path -LiteralPath $RutaArchivo)) { return 'falta' }

    $item = Get-Item -LiteralPath $RutaArchivo
    if (-not $item.PSIsContainer) {
        if ($BytesEsperados -gt 0 -and $item.Length -ne $BytesEsperados) { return 'alterado' }
        if ($ShaEsperado) {
            if ((Get-Sha256 $RutaArchivo) -ne $ShaEsperado) { return 'alterado' }
        }
        return 'ok'
    }

    return 'alterado'
}

function Mostrar-Catalogo {
    Write-Host ''
    Write-Host 'Catalogo de voces Piper' -ForegroundColor Cyan
    Write-Host ('-' * 96) -ForegroundColor DarkGray
    Write-Host ('{0,-28} {1,-9} {2,-22} {3}' -f 'VOZ', 'IDIOMA', 'LICENCIA', 'NOTA')
    Write-Host ('-' * 96) -ForegroundColor DarkGray

    foreach ($v in $Catalogo) {
        $idioma = ($v.Id -split '-')[0]
        if ($v.Publica) { $marca = 'redistribuible' } else { $marca = 'RESTRINGIDA' }
        if ($v.Publica) { $color = 'Green' } else { $color = 'Yellow' }
        Write-Host ('{0,-28} {1,-9} ' -f $v.Id, $idioma) -NoNewline
        Write-Host ('{0,-22} ' -f $v.Licencia) -NoNewline -ForegroundColor $color
        Write-Host ('{0} [{1}]' -f $v.Nota, $marca)
    }

    Write-Host ('-' * 96) -ForegroundColor DarkGray
    Write-Host 'Las voces marcadas como RESTRINGIDA no deberian redistribuirse.' -ForegroundColor Yellow
    Write-Host 'Todas las descargas se verifican con SHA-256 antes de instalarse.' -ForegroundColor DarkGray
}

function Descargar-Fichero {
    param(
        [string] $Url,
        [string] $DestinoArchivo,
        [long] $BytesEsperados,
        [string] $Sha256Esperado
    )

    if ($Url -notmatch '^https://') {
        throw "solo se permiten descargas HTTPS: $Url"
    }

    Assert-RutaSegura $DestinoArchivo

    $parcial = "$DestinoArchivo.part"
    Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue

    try {
        $resp = Invoke-WebRequest -Uri $Url -OutFile $parcial -UseBasicParsing -MaximumRedirection 5 -TimeoutSec 600 -PassThru

        $hostFinal = $resp.BaseResponse.ResponseUri.Host
        if (-not (Test-HostPermitido $hostFinal)) {
            throw "la descarga acabo en un host no permitido: $hostFinal"
        }
    }
    catch {
        Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue
        throw
    }

    if ($BytesEsperados -gt 0) {
        $real = (Get-Item -LiteralPath $parcial).Length
        if ($real -ne $BytesEsperados) {
            Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue
            throw "descarga incompleta: se esperaban $BytesEsperados bytes y llegaron $real"
        }
    }

    if ($Sha256Esperado) {
        $shaReal = Get-Sha256 $parcial
        if ($shaReal -ne $Sha256Esperado) {
            Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue
            throw "SHA-256 no coincide (posible manipulacion): esperado $Sha256Esperado, obtenido $shaReal"
        }
    }

    Move-Item -LiteralPath $parcial -Destination $DestinoArchivo -Force
}

function Instalar-Voz {
    param($Voz)

    $huella = $Huellas[$Voz.Id]

    Write-Host ''
    Write-Host ("-> {0}  ({1}, {2})" -f $Voz.Id, $Voz.Licencia, (Format-MB $huella.Bytes)) -ForegroundColor Cyan

    if (-not $Voz.Publica) {
        Write-Host '   licencia de uso restringido: no la redistribuyas.' -ForegroundColor Yellow
    }

    $ficheros = @(
        @{ Nombre = "$($Voz.Id).onnx";      Bytes = [long] $huella.Bytes;     Sha = $huella.Sha256 }
        @{ Nombre = "$($Voz.Id).onnx.json"; Bytes = [long] $huella.JsonBytes; Sha = $huella.JsonSha }
    )

    foreach ($f in $ficheros) {

        $ruta = Join-Path $Destino $f.Nombre
        Assert-RutaSegura $ruta

        $estado = Get-EstadoFichero -RutaArchivo $ruta -BytesEsperados $f.Bytes -ShaEsperado $f.Sha

        if ($estado -eq 'ok' -and -not $Forzar) {
            Write-Host ("   ya existe    {0}  (SHA-256 verificado)" -f $f.Nombre) -ForegroundColor DarkGray
            continue
        }

        if ($estado -eq 'alterado') {
            Write-Host ("   alterado     {0} no coincide con el hash oficial; se vuelve a descargar" -f $f.Nombre) -ForegroundColor Yellow
        }

        $url = "$Base/$($Voz.Ruta)/$($f.Nombre)?download=true"

        try {
            Descargar-Fichero -Url $url -DestinoArchivo $ruta -BytesEsperados $f.Bytes -Sha256Esperado $f.Sha
            Write-Host ("   descargado   {0}  sha256={1}..." -f $f.Nombre, $f.Sha.Substring(0, 12)) -ForegroundColor Green
        }
        catch {
            Write-Host ("   ERROR        {0}: {1}" -f $f.Nombre, $_.Exception.Message) -ForegroundColor Red
            return $false
        }
    }

    return $true
}

function Verificar-Voz {
    param($Voz)

    $huella = $Huellas[$Voz.Id]

    Write-Host ''
    Write-Host ("-> {0}" -f $Voz.Id) -ForegroundColor Cyan

    $todoOk = $true

    $ficheros = @(
        @{ Nombre = "$($Voz.Id).onnx";      Bytes = [long] $huella.Bytes;     Sha = $huella.Sha256 }
        @{ Nombre = "$($Voz.Id).onnx.json"; Bytes = [long] $huella.JsonBytes; Sha = $huella.JsonSha }
    )

    foreach ($f in $ficheros) {
        $ruta = Join-Path $Destino $f.Nombre
        $estado = Get-EstadoFichero -RutaArchivo $ruta -BytesEsperados $f.Bytes -ShaEsperado $f.Sha

        switch ($estado) {
            'ok'       { Write-Host ("   OK          {0}" -f $f.Nombre) -ForegroundColor Green }
            'falta'    { Write-Host ("   FALTA       {0}" -f $f.Nombre) -ForegroundColor Yellow; $todoOk = $false }
            default    { Write-Host ("   ALTERADO    {0}  <-- no coincide con el hash oficial" -f $f.Nombre) -ForegroundColor Red; $todoOk = $false }
        }
    }

    return $todoOk
}

# --- Integridad del propio catalogo ---
foreach ($v in $Catalogo) {
    if (-not $Huellas.ContainsKey($v.Id)) {
        throw "el catalogo no tiene huella SHA-256 para $($v.Id); revisa el script."
    }
}

function Assert-SinDuplicados {
    $vistos = @{}
    foreach ($v in $Catalogo) {
        if ($vistos.ContainsKey($v.Id)) { throw "voz duplicada en el catalogo: $($v.Id)" }
        $vistos[$v.Id] = $true
    }
}

Assert-SinDuplicados

# --- Seleccion de voces ---

if ($Listar) {
    Mostrar-Catalogo
    exit 0
}

$seleccion = @()

switch ($PSCmdlet.ParameterSetName) {

    'Todas' { $seleccion = @($Catalogo) }

    'Voz' {
        foreach ($pedido in $Voz) {
            $coincidencia = @($Catalogo | Where-Object { $_.Id -eq $pedido.Trim() })
            if ($coincidencia.Count -eq 0) {
                Write-Host "Voz desconocida: $pedido" -ForegroundColor Red
                Write-Host 'Usa -Listar para ver el catalogo.' -ForegroundColor Red
                exit 1
            }
            $seleccion += $coincidencia[0]
        }
    }

    'Verificar' { $seleccion = @($Catalogo) }

    default { $seleccion = @($Catalogo | Where-Object { $_.Publica }) }
}

if ($seleccion.Count -eq 0) {
    Write-Host 'No hay voces que instalar.' -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path -LiteralPath $Destino)) {
    New-Item -ItemType Directory -Path $Destino -Force | Out-Null
}

# --- Modo verificar ---

if ($PSCmdlet.ParameterSetName -eq 'Verificar') {

    Write-Host ''
    Write-Host ("Verificando voces instaladas en {0}" -f $Destino) -ForegroundColor White

    $revisadas = 0
    $correctas = 0
    $fallos = 0

    foreach ($v in $seleccion) {
        $modelo = Join-Path $Destino "$($v.Id).onnx"
        $config = Join-Path $Destino "$($v.Id).onnx.json"
        if (-not (Test-Path -LiteralPath $modelo) -and -not (Test-Path -LiteralPath $config)) { continue }

        $revisadas++
        if (Verificar-Voz -Voz $v) { $correctas++ } else { $fallos++ }
    }

    # Ficheros .onnx que no estan en el catalogo (no se pueden verificar).
    $conocidos = @{}
    foreach ($v in $Catalogo) { $conocidos["$($v.Id).onnx"] = $true }
    $sueltos = @(Get-ChildItem -LiteralPath $Destino -File -Filter *.onnx -ErrorAction SilentlyContinue |
        Where-Object { -not $conocidos.ContainsKey($_.Name) })

    if ($sueltos.Count -gt 0) {
        Write-Host ''
        Write-Host 'Modelos no catalogados (sin hash conocido):' -ForegroundColor Yellow
        foreach ($s in $sueltos) { Write-Host ("   {0}" -f $s.Name) -ForegroundColor Yellow }
    }

    Write-Host ''
    Write-Host ("Revisadas: {0} | correctas: {1} | con fallos: {2}" -f $revisadas, $correctas, $fallos) -ForegroundColor White

    if ($revisadas -eq 0) {
        Write-Host 'No hay voces instaladas que verificar.' -ForegroundColor Yellow
        exit 0
    }

    if ($fallos -gt 0) { exit 1 }
    exit 0
}

# --- Modo instalar ---

$total = 0
foreach ($v in $seleccion) { $total += [long] $Huellas[$v.Id].Bytes + [long] $Huellas[$v.Id].JsonBytes }

Write-Host ''
Write-Host ("Instalando {0} voz(es) en {1}  ({2} en total)" -f $seleccion.Count, $Destino, (Format-MB $total)) -ForegroundColor White

$ok = 0
$fallo = 0

foreach ($v in $seleccion) {
    if (Instalar-Voz -Voz $v) { $ok++ } else { $fallo++ }
}

Write-Host ''
Write-Host ("Listo: {0} instalada(s), {1} con error." -f $ok, $fallo) -ForegroundColor Green
Write-Host 'Abre la app, elige el proveedor Piper y selecciona la voz en el desplegable.' -ForegroundColor White
Write-Host 'Para comprobar la integridad cuando quieras: .\voices\instalar_voces.ps1 -Verificar' -ForegroundColor DarkGray

if ($fallo -gt 0) { exit 1 }
exit 0
