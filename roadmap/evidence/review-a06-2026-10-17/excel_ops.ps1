param(
  [Parameter(Mandatory)][ValidateSet('hold','edit','read')][string]$Mode,
  [Parameter(Mandatory)][string]$Path,
  [int]$Sheet = 1,
  [string]$Ready = '',
  [string]$Release = '',
  [string]$Text = 'Excel edit'
)
$ErrorActionPreference = 'Stop'
$x = New-Object -ComObject Excel.Application
$x.Visible = $false
$x.DisplayAlerts = $false
try {
  $wb = $x.Workbooks.Open($Path)
  $ws = $wb.Worksheets.Item($Sheet)
  switch ($Mode) {
    'hold' {
      New-Item -ItemType File -Force $Ready | Out-Null
      $deadline = (Get-Date).AddSeconds(60)
      while (-not (Test-Path $Release) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 200 }
      $wb.Close($false)
    }
    'edit' {
      $ws.Cells.Item(5, 9).Value2 = $Text      # a user typing in the title cell of row 5, then saving
      $wb.Save()
      $wb.Close($true)
    }
    'read' {
      "A5=" + $ws.Cells.Item(5, 1).Value2 + ";I5=" + $ws.Cells.Item(5, 9).Value2 + ";P5=" + $ws.Cells.Item(5, 16).Value2
      $wb.Close($false)
    }
  }
} finally {
  $x.Quit()
  [void][Runtime.InteropServices.Marshal]::ReleaseComObject($x)
}
