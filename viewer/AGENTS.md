# Viewer
Production-only deployment is explicitly authorized by the owner. Do not add a Dev hostname or inference endpoint. Keep static viewer changes under viewer/; reuse assets/ without modifying generated outputs. Build/test through Docker. See README.md for commands.
No source bind mounts in production. No credentials in source or images. Preserve the Intel inference work on Skynet. Publishing the viewer does not authorize running AI inference, scheduling agents or exposing Gradio.
