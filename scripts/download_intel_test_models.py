import urllib.request,json,hashlib,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
repo="tencent/Hunyuan3D-2.1"
rev='0b94677654c57bb9a6b6845cd7b704ccf551d327'
files=json.load(urllib.request.urlopen(f"https://huggingface.co/api/models/{repo}/tree/{rev}?recursive=true&limit=1000"))
root=Path("/runtime/models/Hunyuan3D-2.1"); root.mkdir(parents=True,exist_ok=True)
selected=[x for x in files if x["type"]=="file" and (x["path"].startswith(("hunyuan3d-dit-v2-1/","hunyuan3d-vae-v2-1/","hunyuan3d-paintpbr-v2-1/")) or x["path"] in ("README.md","LICENSE","Notice.txt"))]
print("Revision",rev,"bytes",sum(x["size"] for x in selected),flush=True)
def get(x):
 p=root/x["path"];p.parent.mkdir(parents=True,exist_ok=True)
 expected=x.get("lfs",{}).get("oid")
 def checksum(path):
  h=hashlib.sha256()
  with path.open("rb") as f:
   for chunk in iter(lambda:f.read(8<<20),b""):h.update(chunk)
  return h.hexdigest()
 if p.exists() and p.stat().st_size==x["size"] and (not expected or checksum(p)==expected):return
 for attempt in range(3):
  try:
   temp=p.with_name(p.name+".partial")
   with urllib.request.urlopen(f"https://huggingface.co/{repo}/resolve/{rev}/{x['path']}?download=true",timeout=90) as src,temp.open("wb") as dest:
    while chunk:=src.read(8<<20):dest.write(chunk)
   assert temp.stat().st_size==x["size"]
   if expected:assert checksum(temp)==expected
   temp.replace(p);print("Downloaded",x["path"],flush=True);return
  except Exception as exc:
   print("Retry",x["path"],type(exc).__name__,flush=True)
   if attempt==2:raise
with ThreadPoolExecutor(max_workers=4) as ex:list(ex.map(get,selected))
(root/"download-manifest.json").write_text(json.dumps({"repo":repo,"revision":rev,"files":selected},indent=2))
print("ALL MODEL FILES VERIFIED",flush=True)

# Upstream paint also requires RealESRGAN. Keep partial files out of its loader.
p=Path("/work/Hunyuan3D-2.1/hy3dpaint/ckpt/RealESRGAN_x4plus.pth")
p.parent.mkdir(parents=True,exist_ok=True)
if not p.exists() or p.stat().st_size < 60_000_000:
 temp=p.with_suffix(".partial")
 with urllib.request.urlopen("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",timeout=90) as src,temp.open("wb") as dest:
  while chunk:=src.read(8<<20):dest.write(chunk)
 assert temp.stat().st_size>60_000_000
 temp.replace(p)
print("RealESRGAN ready",flush=True)
