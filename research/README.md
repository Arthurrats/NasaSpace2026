# Pesquisa Python

Use `notebooks/` para análises exploratórias e `src/fire_research/` para código reutilizável. Instale as dependências dos experimentos neste ambiente. O Flask tem seu próprio ambiente e pode rodar independentemente.

```powershell
cd research
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
```

Para usar o JupyterLab:

```powershell
.\.venv\Scripts\python.exe -m pip install -e '.[notebooks]'
.\.venv\Scripts\python.exe -m jupyter lab
```
