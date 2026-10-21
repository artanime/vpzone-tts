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

.PARAMETER Voz
    Identificadores de las voces a instalar (ej. en_US-amy-medium).

.PARAMETER Publicas
    Instala todas las voces con licencia de redistribucion libre (CC0, dominio
    publico, Apache-2.0, CC BY, CC BY-SA, AGPL-3.0).

.PARAMETER Todas
    Instala todo el catalogo, incluidas las voces de uso restringido.

.PARAMETER Listar
    Muestra el catalogo disponible y termina.

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

# Catalogo de voces. "Bytes" es el tamano exacto del .onnx en HuggingFace y
# sirve para verificar que la descarga no se ha corrompido.
$Catalogo = @(
    # --- Ingles (US) ---
    [pscustomobject]@{ Id = 'en_US-amy-medium';       Ruta = 'en/en_US/amy/medium';       Bytes = 63201294; Licencia = 'CC BY-SA 4.0';   Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_US-joe-medium';       Ruta = 'en/en_US/joe/medium';       Bytes = 63201294; Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-mike-medium';      Ruta = 'en/en_US/mike/medium';      Bytes = 63221984; Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-sam-medium';       Ruta = 'en/en_US/sam/medium';       Bytes = 62950044; Licencia = 'Apache-2.0';      Publica = $true;  Nota = 'No binaria' }
    [pscustomobject]@{ Id = 'en_US-kristin-medium';   Ruta = 'en/en_US/kristin/medium';   Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_US-john-medium';      Ruta = 'en/en_US/john/medium';      Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-bryce-medium';     Ruta = 'en/en_US/bryce/medium';     Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-norman-medium';    Ruta = 'en/en_US/norman/medium';    Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'en_US-ljspeech-medium';  Ruta = 'en/en_US/ljspeech/medium';  Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'LJSpeech' }

    # --- Ingles (GB) ---
    [pscustomobject]@{ Id = 'en_GB-cori-medium';      Ruta = 'en/en_GB/cori/medium';      Bytes = 63531379; Licencia = 'Dominio publico'; Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_GB-alba-medium';      Ruta = 'en/en_GB/alba/medium';      Bytes = 63201294; Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Femenina' }
    [pscustomobject]@{ Id = 'en_GB-alan-medium';      Ruta = 'en/en_GB/alan/medium';      Bytes = 63201294; Licencia = 'CC BY-SA 4.0';   Publica = $true;  Nota = 'Masculina' }

    # --- Frances ---
    [pscustomobject]@{ Id = 'fr_FR-siwis-medium';     Ruta = 'fr/fr_FR/siwis/medium';     Bytes = 63201294; Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Masculina' }
    [pscustomobject]@{ Id = 'fr_FR-upmc-medium';      Ruta = 'fr/fr_FR/upmc/medium';      Bytes = 76733615; Licencia = 'CC BY-SA 4.0';   Publica = $true;  Nota = '2 hablantes' }
    [pscustomobject]@{ Id = 'fr_FR-tom-medium';       Ruta = 'fr/fr_FR/tom/medium';       Bytes = 63511038; Licencia = 'AGPL-3.0';        Publica = $true;  Nota = 'Masculina, 44.1 kHz' }
    [pscustomobject]@{ Id = 'fr_FR-gilles-low';       Ruta = 'fr/fr_FR/gilles/low';       Bytes = 63104526; Licencia = 'CC0';             Publica = $true;  Nota = 'Masculina, calidad baja' }
    [pscustomobject]@{ Id = 'fr_FR-mls_1840-low';     Ruta = 'fr/fr_FR/mls_1840/low';     Bytes = 63104526; Licencia = 'CC BY 4.0';       Publica = $true;  Nota = 'Masculina, 1840' }
    [pscustomobject]@{ Id = 'fr_FR-mls-medium';       Ruta = 'fr/fr_FR/mls/medium';       Bytes = 76733750; Licencia = 'CC BY 4.0';       Publica = $true;  Nota = '125 hablantes' }

    # --- Uso restringido: uso personal, no redistribuir ---
    [pscustomobject]@{ Id = 'en_US-ryan-medium';      Ruta = 'en/en_US/ryan/medium';      Bytes = 63201294; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-lessac-medium';    Ruta = 'en/en_US/lessac/medium';    Bytes = 63201294; Licencia = 'Blizzard 2013';   Publica = $false; Nota = 'Solo investigacion' }
    [pscustomobject]@{ Id = 'en_US-kusal-medium';     Ruta = 'en/en_US/kusal/medium';     Bytes = 63201294; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-hfc_female-medium'; Ruta = 'en/en_US/hfc_female/medium'; Bytes = 63201294; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_US-hfc_male-medium';  Ruta = 'en/en_US/hfc_male/medium';  Bytes = 63201294; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
    [pscustomobject]@{ Id = 'en_GB-semaine-medium';   Ruta = 'en/en_GB/semaine/medium';   Bytes = 76737711; Licencia = 'CC BY-NC-SA 4.0'; Publica = $false; Nota = 'NO COMERCIAL' }
)

if (-not $Destino) {
    $Destino = Join-Path $PSScriptRoot 'piper'
}

function Format-MB {
    param([long] $Bytes)
    return ('{0,6:N1} MB' -f ($Bytes / 1MB))
}

function Mostrar-Catalogo {
    Write-Host ''
    Write-Host 'Catalogo de voces Piper' -ForegroundColor Cyan
    Write-Host ('-' * 92) -ForegroundColor DarkGray
    Write-Host ('{0,-26} {1,-9} {2,-20} {3}' -f 'VOZ', 'IDIOMA', 'LICENCIA', 'NOTA')
    Write-Host ('-' * 92) -ForegroundColor DarkGray

    foreach ($v in $Catalogo) {
        $idioma = ($v.Id -split '-')[0]
        $marca = if ($v.Publica) { 'redistribuible' } else { 'RESTRINGIDA' }
        $color = if ($v.Publica) { 'Green' } else { 'Yellow' }
        Write-Host ('{0,-26} {1,-9} ' -f $v.Id, $idioma) -NoNewline
        Write-Host ('{0,-20} ' -f $v.Licencia) -NoNewline -ForegroundColor $color
        Write-Host ('{0} [{1}]' -f $v.Nota, $marca)
    }

    Write-Host ('-' * 92) -ForegroundColor DarkGray
    Write-Host 'Las voces marcadas como RESTRINGIDA no deberian redistribuirse.' -ForegroundColor Yellow
}

function Descargar-Fichero {
    param([string] $Url, [string] $DestinoArchivo, [long] $BytesEsperados)

    $parcial = "$DestinoArchivo.part"

    try {
        $client = New-Object System.Net.WebClient
        $client.DownloadFile($Url, $parcial)
        $client.Dispose()
    }
    catch {
        if (Test-Path -LiteralPath $parcial) {
            Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue
        }
        throw
    }

    if ($BytesEsperados -gt 0) {
        $real = (Get-Item -LiteralPath $parcial).Length
        if ($real -ne $BytesEsperados) {
            Remove-Item -LiteralPath $parcial -Force -ErrorAction SilentlyContinue
            throw "descarga incompleta: se esperaban $BytesEsperados bytes y llegaron $real"
        }
    }

    Move-Item -LiteralPath $parcial -Destination $DestinoArchivo -Force
}

function Instalar-Voz {
    param($Voz)

    Write-Host ''
    Write-Host ("-> {0}  ({1}, {2})" -f $Voz.Id, $Voz.Licencia, (Format-MB $Voz.Bytes)) -ForegroundColor Cyan

    if (-not $Voz.Publica) {
        Write-Host '   licencia de uso restringido: no la redistribuyas.' -ForegroundColor Yellow
    }

    $ficheros = @(
        @{ Nombre = "$($Voz.Id).onnx";      Bytes = [long] $Voz.Bytes }
        @{ Nombre = "$($Voz.Id).onnx.json"; Bytes = 0 }
    )

    foreach ($f in $ficheros) {

        $ruta = Join-Path $Destino $f.Nombre

        if ((Test-Path -LiteralPath $ruta) -and -not $Forzar) {
            Write-Host ("   ya existe    {0}" -f $f.Nombre) -ForegroundColor DarkGray
            continue
        }

        $url = "$Base/$($Voz.Ruta)/$($f.Nombre)?download=true"

        try {
            Descargar-Fichero -Url $url -DestinoArchivo $ruta -BytesEsperados $f.Bytes
            Write-Host ("   descargado   {0}" -f $f.Nombre) -ForegroundColor Green
        }
        catch {
            Write-Host ("   ERROR        {0}: {1}" -f $f.Nombre, $_.Exception.Message) -ForegroundColor Red
            return $false
        }
    }

    return $true
}

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

    default { $seleccion = @($Catalogo | Where-Object { $_.Publica }) }
}

if ($seleccion.Count -eq 0) {
    Write-Host 'No hay voces que instalar.' -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path -LiteralPath $Destino)) {
    New-Item -ItemType Directory -Path $Destino -Force | Out-Null
}

$total = ($seleccion | Measure-Object -Property Bytes -Sum).Sum

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

if ($fallo -gt 0) { exit 1 }
exit 0
