docker build -t whisper .
docker run --gpus all -p 8888:8888 -v $(pwd)/inputs:/whisper/inputs -v $(pwd)/outputs:/whisper/outputs whisper