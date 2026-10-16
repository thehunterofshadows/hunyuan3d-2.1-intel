"""Regression: inspect raw glTF UVs, not a trimesh roundtrip that hides flips."""
import json, struct, tempfile
from pathlib import Path
import numpy as np
from mesh_io import export_glb_pbr

def test_raw_export_preserves_top_origin_uv():
    uv=np.array([[0.1,0.2],[0.9,0.3],[0.4,0.8]])
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'test.glb'
        export_glb_pbr(np.array([[0,0,0],[1,0,0],[0,1,0]]),np.array([[0,1,2]]),uv,np.zeros((8,8,3),dtype=np.uint8),str(p))
        data=p.read_bytes();size=struct.unpack_from('<I',data,12)[0]
        doc=json.loads(data[20:20+size]);binary=data[28+size:]
        index=doc['meshes'][0]['primitives'][0]['attributes']['TEXCOORD_0']
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',8)
        raw=np.array([struct.unpack_from('<ff',binary,start+i*stride) for i in range(a['count'])])
        np.testing.assert_allclose(raw,uv,atol=1e-6)
if __name__=='__main__':
    test_raw_export_preserves_top_origin_uv()
    print('PASS: raw exported glTF UVs preserve top-origin input')
