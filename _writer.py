import pathlib, os, base64
BASE = pathlib.Path('validation/gauquelin')
BASE.mkdir(parents=True, exist_ok=True)
print('writer ready, BASE =', BASE.resolve())
