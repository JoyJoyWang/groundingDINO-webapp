FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

WORKDIR /app
RUN rm -rf .DS_Store __pycache__ venv
# Basic dependencies
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip git wget build-essential cmake ninja-build \
    && rm -rf /var/lib/apt/lists/*

RUN python3.10 -m pip install --upgrade pip

# Install base dependencies
COPY requirements.txt .
COPY static/ static/
COPY templates/ templates/

RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Clone and patch GroundingDINO
RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO/groundingdino/models/GroundingDINO/csrc/MsDeformAttn && \
    sed -i 's/value.type()/value.scalar_type()/g' ms_deform_attn_cuda.cu && \
    sed -i 's/value.scalar_type().is_cuda()/value.is_cuda()/g' ms_deform_attn_cuda.cu && \
    cd /app/GroundingDINO && pip install -e . --no-build-isolation

WORKDIR /app
RUN pip install -r requirements.txt

# Download model weights
RUN mkdir -p /app/weights && \
    wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth \
    -O /app/weights/groundingdino_swint_ogc.pth

# Copy rest of app
COPY . .

CMD ["python3.10", "app.py"]
