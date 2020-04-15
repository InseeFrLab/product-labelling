FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
ADD . /app
RUN chmod +x /app/entrypoint.sh
RUN pip install -r /app/requirements.txt
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python","/app/manage.py","runserver","0.0.0.0:8000"]
