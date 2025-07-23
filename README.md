我现在就是用3.10python创建了虚拟环境,然后pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

RUN git clone https://github.com/IDEA-Research/GroundingDINO.git && \
    cd GroundingDINO/groundingdino/models/GroundingDINO/csrc/MsDeformAttn && \
    sed -i 's/value.type()/value.scalar_type()/g' ms_deform_attn_cuda.cu && \
    sed -i 's/value.scalar_type().is_cuda()/value.is_cuda()/g' ms_deform_attn_cuda.cu && \


装了torch,然后在vs 2019(确保有c++的情况下)(venv310) C:\Users\Administrator\Desktop\groundingDINO-webapp\GroundingDINO>cl 
Microsoft (R) C/C++ Optimizing Compiler Version 19.21.27702.2 for x64
Copyright (C) Microsoft Corporation.  All rights reserved.

usage: cl [ option... ] filename... [ /link linkoption... ]

在这里面set DISTUTILS_USE_SDK=1
set MSSdk=1
然后cd 到groundingdino里面groundingDINO-webapp\GroundingDINO>pip install -e . --no-build-isolation

然后pip install -r requirements.txt
然后RUN mkdir -p /app/weights && \
    wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth \
    -O /app/weights/groundingdino_swint_ogc.pth

这样才安装成功,请问我怎么docker到gcp上去?保证这些配置和环境一样?gcp的cuda什么的能和我一样吗
