FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends blender ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /work
ENTRYPOINT ["blender", "-b"]
RUN apt-get update && apt-get install -y --no-install-recommends python3-numpy && rm -rf /var/lib/apt/lists/*
