FROM python:3.12 AS builder
WORKDIR /forgery-finder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /forgery-finder/

RUN mkdir __pypackages__ && pdm sync --prod --no-editable

FROM python:3.12
WORKDIR /forgery-finder

ENV PYTHONPATH=/forgery-finder/__pdm__

COPY app.py /forgery-finder/
COPY --from=builder /forgery-finder/__pypackages__/3.12/lib /forgery-finder/__pdm__
COPY --from=builder /forgery-finder/__pypackages__/3.12/bin/* /bin/

EXPOSE 5000
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000", "-w", "4"]
