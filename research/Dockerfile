FROM python:3.13-slim-bookworm
ENV PYTHONUNBUFFERED=1
WORKDIR /workspace

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir ".[notebooks]" \
    && useradd --create-home --uid 1000 researcher \
    && install -d -o researcher -g researcher /workspace/notebooks

USER researcher
EXPOSE 8888
CMD ["jupyter", "lab", "--no-browser", "--ip=0.0.0.0", "--port=8888", "--ServerApp.port_retries=0", "--ServerApp.root_dir=/workspace/notebooks"]
