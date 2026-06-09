# Search Sessions - Поиск по сессиям
# Использование: .\search_sessions.ps1 -Pattern "термин" [-Path "sessions"]

param(
    [Parameter(Mandatory=$true)]
    [string]$Pattern,
    
    [string]$Path = "sessions",
    
    [switch]$CaseSensitive
)

Write-Host "============================================"
Write-Host "Поиск по сессиям: $Pattern"
Write-Host "============================================"
Write-Host ""

if (-not (Test-Path $Path)) {
    Write-Host "❌ Каталог не найден: $Path"
    exit 1
}

# Поиск с Select-String
$results = Select-String -Path "$Path\*.md" -Pattern $Pattern -CaseSensitive:$CaseSensitive

if ($results.Count -eq 0) {
    Write-Host "Ничего не найдено."
    exit 0
}

Write-Host "Найдено совпадений: $($results.Count)"
Write-Host ""
Write-Host "Результаты:"
Write-Host "-------------------------------------------"

foreach ($result in $results) {
    Write-Host ""
    Write-Host "Файл: $($result.Filename)"
    Write-Host "Строка: $($result.LineNumber)"
    Write-Host "Текст: $($result.Line.Trim())"
    Write-Host "-------------------------------------------"
}

Write-Host ""
Write-Host "✅ Поиск завершён."
