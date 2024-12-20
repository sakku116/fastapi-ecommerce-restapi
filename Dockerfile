# Stage 1: Build stage
FROM python:3.13.1-slim AS builder

# Set the working directory
WORKDIR /app

# Copy only requirements to install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.13.1-slim

# Set the working directory
WORKDIR /app

# Copy only necessary files from the build stage
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application files
COPY . .

# Run the application
CMD [ "python", "main.py", "--ensure-indexes", "--ensure-buckets", "--seed-initial-users", "--seed-initial-categories", "--seed-initial-products" ]
