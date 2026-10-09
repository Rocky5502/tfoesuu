FROM python@sha256:e191a71397fd61fbddb6712cd43ef9a2c17df0b5e7ba67607128554cd6bff267

COPY requirements-lock.txt /tmp/requirements-lock.txt
RUN python -m pip install --no-cache-dir --disable-pip-version-check \
    -r /tmp/requirements-lock.txt

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=0

WORKDIR /workspace
