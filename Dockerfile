
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app
RUN rm -rf .DS_Store __pycache__ venv
# Basic dependencies
RUN apt-get update && apt-get install -y python3-pip git wget ffmpeg libsm6 libxext6 && \
    pip install --upgrade pip

# Install base dependencies
COPY requirements.txt .
COPY static/ static/
COPY templates/ templates/
RUN pip install -r requirements.txt

# Clone and patch GroundingDINO
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO/groundingdino/models/GroundingDINO/csrc/MsDeformAttn && \
    sed -i 's/value.type()/value.scalar_type()/g' ms_deform_attn_cuda.cu && \
    sed -i 's/value.scalar_type().is_cuda()/value.is_cuda()/g' ms_deform_attn_cuda.cu && \
    cd /app/GroundingDINO && pip install -e .

# Download model weights
RUN mkdir -p /app/weights && \
    wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth \
    -O /app/weights/groundingdino_swint_ogc.pth

# Copy rest of app
COPY . .

CMD ["python3", "app.py"]
