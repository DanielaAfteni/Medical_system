FROM python:3.10

# RUN python -m pip install --upgrade pip

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app
COPY . .

ENV PYTHONPATH="${PYTHONPATH}:/app"
# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt
# COPY requirements.txt .
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 4000

# Define the command to run your application
CMD ["python", "patient_service.py"]