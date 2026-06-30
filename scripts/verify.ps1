param(
    [ValidateSet("all", "backend", "frontend")]
    [string]$Scope = "all",
    [string]$CondaEnv = "mcp"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

function Resolve-Conda {
    $command = Get-Command conda -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        return "conda"
    }

    $candidates = @(
        $env:CONDA_EXE,
        "$env:USERPROFILE\miniforge3\Scripts\conda.exe",
        "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
        "$env:USERPROFILE\anaconda3\Scripts\conda.exe",
        "D:\miniforge3\Scripts\conda.exe",
        "D:\miniconda3\Scripts\conda.exe",
        "D:\anaconda3\Scripts\conda.exe",
        "C:\ProgramData\miniforge3\Scripts\conda.exe",
        "C:\ProgramData\miniconda3\Scripts\conda.exe",
        "C:\ProgramData\anaconda3\Scripts\conda.exe"
    )

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    return $null
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Command
    Write-Host "OK: $Name" -ForegroundColor Green
}

function Invoke-Python {
    param(
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    $condaCommand = Resolve-Conda
    if ($condaCommand) {
        & $condaCommand run -n $CondaEnv python @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed with exit code $LASTEXITCODE"
        }
        return
    }

    Write-Host "WARN: conda command not found, fallback to current python." -ForegroundColor Yellow
    & python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE"
    }
}

if ($Scope -eq "all" -or $Scope -eq "backend") {
    Invoke-Step "Backend py_compile" {
        Push-Location $backend
        try {
            Invoke-Python -m py_compile `
                app/models/group/group.py `
                app/models/auth/published_service_secret.py `
                app/models/modules/mcp_template.py `
                app/repositories/__init__.py `
                app/repositories/mcp_auth_repository.py `
                app/repositories/mcp_template_group_repository.py `
                app/repositories/mcp_template_repository.py `
                app/services/auth/secret_manager.py `
                app/services/group/service.py `
                app/services/mcp_template/service.py `
                app/utils/http/pagination.py `
                run.py
        } finally {
            Pop-Location
        }
    }

    Invoke-Step "Backend import smoke" {
        Push-Location $backend
        try {
            Invoke-Python -c "from app.services.group.service import group_service; from app.services.mcp_template.service import mcp_template_service; from app.services.auth import SecretManager; from app.repositories import McpTemplateGroupRepository, McpTemplateRepository, McpAuthRepository; print(type(group_service).__name__, type(mcp_template_service).__name__, SecretManager.__name__, McpTemplateGroupRepository.__name__, McpTemplateRepository.__name__, McpAuthRepository.__name__)"
        } finally {
            Pop-Location
        }
    }
}

if ($Scope -eq "all" -or $Scope -eq "frontend") {
    Invoke-Step "Frontend build" {
        Push-Location $frontend
        try {
            node .\node_modules\vite\bin\vite.js build
            if ($LASTEXITCODE -ne 0) {
                throw "Frontend build failed with exit code $LASTEXITCODE"
            }
        } finally {
            Pop-Location
        }
    }
}
