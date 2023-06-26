import os
import subprocess

# Código para instalar as bibliotecas necessarias em outros computadores

libraries = [
    "requests",
    "pandas",
    "python-dateutil",
    "time",
    "openpyxl",
    "tqdm"
]

for library in libraries:
    try:
        # Verifica se a biblioteca já está instalada
        __import__(library)
        print(f"{library} já está instalada")
    except ImportError:
        print(f"Instalando {library}...")
        subprocess.check_call(['pip', 'install', library])
        print(f"{library} instalada com sucesso")

print("\nTodas as bibliotecas foram instaladas.")
