FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file first to leverage Docker caching
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the serialized model and Flask application code
COPY superkart_model.joblib ./backend_files/superkart_model.joblib
COPY Flask_App.py ./app.py

# Expose port 7860 for Flask API
EXPOSE 7860

# Run the web application
CMD ["python", "app.py"]