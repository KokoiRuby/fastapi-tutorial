# Build stage - dep
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
# disable cache to save docker image size
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# security practice using non-root user
RUN useradd -m app

# Copy only the installed packages from builder stage
COPY --from=builder /usr/local /usr/local
# Copy the rest of the application code to container
COPY --chown=app:app . .

# Make sure scripts in /usr/local/bin are usable
ENV PATH=/usr/local/bin:$PATH

# Change to non-root user
USER app

# Command to run the application
CMD ["python", "-m", "app.entrypoint.fastapi"]
