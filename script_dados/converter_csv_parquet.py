"""Converte os CSVs de focos de calor (MODIS e VIIRS) para Parquet.

Uso (a partir da raiz do repositório):
    python scripts/converter_csv_parquet.py            # converte modis e viirs
    python scripts/converter_csv_parquet.py modis      # converte só o modis

Requisitos:
    pip install pandas pyarrow
"""
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

BASE = Path(r'C:\Users\arthu\OneDrive\Documentos\modis_2025_south_america')

TIPOS = {
    'modis': {
        'entrada': BASE / 'modis',
        'saida': Path('dados/parquet/modis'),
        'dtypes': {
            'latitude': 'float32', 'longitude': 'float32', 'brightness': 'float32',
            'scan': 'float32', 'track': 'float32', 'acq_time': 'int16',
            'satellite': 'category', 'instrument': 'category', 'confidence': 'int16',
            'version': 'category', 'bright_t31': 'float32', 'frp': 'float32',
            'daynight': 'category', 'type': 'int8',
        },
        'datas': ['acq_date'],
    },
    'viirs': {
        'entrada': BASE / 'viirs',
        'saida': Path('dados/parquet/viirs'),
        'dtypes': {
            'latitude': 'float32', 'longitude': 'float32', 'bright_ti4': 'float32',
            'scan': 'float32', 'track': 'float32', 'acq_time': 'int16',
            'satellite': 'category', 'instrument': 'category', 'confidence': 'category',
            'version': 'category', 'bright_ti5': 'float32', 'frp': 'float32',
            'daynight': 'category', 'type': 'int8',
        },
        'datas': ['acq_date'],
    },
}


def converter(nome, cfg):
    entrada, saida = cfg['entrada'], cfg['saida']
    saida.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(entrada.rglob('*.csv'))
    if not arquivos:
        print(f'[{nome}] nenhum CSV encontrado em {entrada}')
        return

    for csv in arquivos:
        df = pd.read_csv(csv, dtype=cfg['dtypes'], parse_dates=cfg['datas'])

        # guarda o nome do arquivo de origem (útil se ele indicar país/região)
        df['origem'] = csv.stem
        df['origem'] = df['origem'].astype('category')

        # dados ordenados comprimem melhor
        df = df.sort_values(['acq_date', 'acq_time']).reset_index(drop=True)

        destino = saida / f'{csv.stem}.parquet'
        df.to_parquet(destino, compression='zstd', index=False)

        # conferência: o Parquet precisa ter o mesmo número de linhas do DataFrame
        linhas_parquet = pq.ParquetFile(destino).metadata.num_rows
        status = 'OK' if linhas_parquet == len(df) else 'ERRO: número de linhas diferente'

        print(f'[{nome}] {csv.name}: {len(df):,} linhas | '
              f'{csv.stat().st_size / 1e6:.1f} MB -> {destino.stat().st_size / 1e6:.1f} MB | {status}')

        if destino.stat().st_size > 100 * 1024 * 1024:
            print(f'  ATENÇÃO: {destino.name} passa de 100 MB e o GitHub vai recusar o push')


if __name__ == '__main__':
    escolhidos = sys.argv[1:] or list(TIPOS)
    for nome in escolhidos:
        if nome not in TIPOS:
            sys.exit(f'Tipo desconhecido: {nome}. Opções: {", ".join(TIPOS)}')
        converter(nome, TIPOS[nome])