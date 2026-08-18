# Parse-check startup.py before reloading pyRevit (uses pyRevit's bundled CPython; py2-only syntax
# like `print x` would false-positive, but startup.py avoids those).
$py = "$env:APPDATA\pyRevit-Master\bin\cengines\CPY3123\python.exe"
$f = Join-Path $PSScriptRoot "..\OneTake.extension\startup.py"
& $py -c "import ast,sys; src=open(sys.argv[1],encoding='utf-8').read()
try:
    ast.parse(src); print('parse OK')
except SyntaxError as e:
    print('SyntaxError line', e.lineno, e.msg); print(src.splitlines()[e.lineno-1]); sys.exit(1)" $f
