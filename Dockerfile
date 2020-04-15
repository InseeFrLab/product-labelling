FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
ADD requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
RUN chmod +x /app/entrypoint.sh
EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python","/app/manage.py","runserver","0.0.0.0:8000"]
