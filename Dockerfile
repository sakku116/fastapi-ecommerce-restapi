# Use a base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Create a directory for logs
RUN mkdir logs

# Install dependencies
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN apt-get update && apt-get install -y iputils-ping

# Copy the requirements file
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# Copy the workspace files to the container
COPY . .

# Run the command to start your application
CMD [ "python", "main.py", "--ensure-indexes", "--ensure-buckets", "--seed-initial-users", "--seed-initial-categories", "--seed-initial-products"]