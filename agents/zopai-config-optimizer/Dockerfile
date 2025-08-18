# Step 1: Use official Python image
FROM python:3.10-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy project files
COPY . /app

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose port
EXPOSE 8000

# Step 6: Run FastAPI app with uvicorn
CMD ["uvicorn", "zopai_api:app", "--host", "0.0.0.0", "--port", "8000"]
