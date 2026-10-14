# # 
# FROM --platform=linux/amd64 python:3.14-slim
# RUN apt-get update
# RUN apt-get install -y gcc
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
# ENV PYTHONBUFFERED 1

# # 
# WORKDIR /code

# # 
# COPY ./requirements.txt /code/requirements.txt

# # 
# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# # 
# COPY ./ /code

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
