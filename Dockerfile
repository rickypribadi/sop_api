# 
FROM --platform=linux/amd64 python:3.12.2-slim
RUN apt-get update
RUN apt-get install -y gcc
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
ENV PYTHONBUFFERED 1

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./ /code

# 

# CMD ["sh", "-c", "gunicorn main:app --max-requests-jitter 10 --max-requests 40 --timeout 300 --bind :8401 --workers 3 --threads 4 -k uvicorn.workers.UvicornWorker"]
CMD ["sh", "-c", "gunicorn main:app --bind :8401 -k uvicorn.workers.UvicornWorker"]

# CMD ["fastapi", "run", "main.py", "--port", "8401"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8401"]