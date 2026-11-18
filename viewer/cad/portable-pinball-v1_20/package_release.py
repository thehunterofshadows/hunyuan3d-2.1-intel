"""Stage V1.20 source, full CAD pack, exact CAD asset, and two optional fit samples."""
from pathlib import Path
import json,hashlib,shutil,zipfile
R=Path(__file__).resolve().parent
REPO=R.parents[2]
A=REPO/'assets/portable-pinball-v1_20'
O=R/'exports'
A.mkdir(parents=True,exist_ok=True)
STL=A/'stl-v1_20';STL.mkdir(exist_ok=True)
for f in sorted((O/'enclosure_stl').glob('*.stl')):shutil.copy2(f,STL/f.name)
for f in (O/'fit_m8_front').glob('*.stl'):shutil.copy2(f,A/f.name)
README="""# Portable Pinball V1.20 — direct M8 front rubber feet

## What to print
Only TWO replacement parts are required for an existing V1.19 cabinet:
- `stl-v1_20/foot_receiver_left_front.stl`
- `stl-v1_20/foot_receiver_right_front.stl`

Optional fit tests: print `m8_nut_fit_coupon.stl` before a receiver, and `front_m8_center_pilot_jig.stl` to locate the exact center of the front mounting holes.

**Do not reprint** either floor panel, either upper front backing plate, or any rear parts. They are unchanged.

## Hardware and installation
- Reuse all four existing **M5 mounting bolts and captive M5 nuts per receiver** (8 front mounting bolts/nuts total). Check that the socket fits the existing 17 mm tunnels. Use verified short bolts, not M5×30.
- Install a **standard metal M8 hex nut in the TOP opening** of each new front receiver *before* sandwiching the cabinet floor; the cabinet floor retains the nut. No M6 nut clip or 55 mm M6-to-M8 front extension is needed.
- The receiver's hex pocket is **15.5 mm across corners**, about 13.42 mm across flats, nominally 8 mm deep. The centered **Ø9.0 mm through-bore** extends through the entire **20 mm** receiver. Test with your actual M8 metal nuts and M8 foot stems, not only against a nominal specification.
- **Existing original front cabinet floor and front backing plates DO NOT have an M8 hole yet.** Drill a centered **Ø9.0 mm** hole through BOTH the 4 mm front floor panel and the 6 mm inner backing plate at EACH front foot station. Center locations in original cabinet coordinates: **(X=48,Y=80) and (X=212,Y=80) mm**. The four unchanged M5 bolt centers around each station are at ±13 mm X and ±13 mm Y.
- Optional 60 mm drill jig has matching four M5 mount holes and a Ø3 mm CENTER PILOT. With receiver hardware removed, register the jig to those holes and lightly spot a 3 mm pilot. REMOVE jig and enlarge center hole to Ø9.0 mm through both existing plastic parts separately. Protect interior components, inspect both sides, deburr, and test stud travel BEFORE reassembling.
- The purchased M8 stud can now advance through the top of the receiver and the newly drilled floor/backing stack for more adjustability. Check PC, wiring and other inside clearances when the threaded shaft is raised fully.
- The rear receivers and their 45 mm + 55 mm extension stacks are **unchanged** from V1.19. Removing the 55 mm front extensions changes the slope; measure real cabinet angle with installed feet and adjust rear height if needed.
- A roughly **2.1 mm nominal minimum plastic web** separates the central nut pocket corners from the existing large M5 socket channels. PETG layer adhesion, nut friction, stud torque, bolt reach and physical load/strength are NOT VERIFIED. Print and test one front receiver with real hardware first. Do not over-tighten or use the pilot jig as a load-bearing washer.

## Validation and source
CAD assembly checks: **71 printable model pieces** (down from 81) and 20 previous small fit samples, plus 2 new standalone M8 test/jig pieces, all validated independently. No detected CAD solid interference. Original shared assemblies, both original floor panels, all four top backing plates and two rear leg stacks are preserved. Source: `viewer/cad/portable-pinball-v1_20/` in the project repository. V1.19 remains separately available. The STL files are printable placeholders pending a real nut/foot fit and cabinet load check.
"""
(A/'README-v1_20.md').write_text(README)
zip_path=A/'cad-print-pack-v1_20.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in ['build_cabinet.py','build_front_fit_samples.py','render_v1_20_preview.py','validate_meshes.py','parameters.json','requirements.txt','README.md','package_release.py']:
  z.write(R/f,'source/'+f)
 z.writestr('ASSEMBLY_INSTRUCTIONS.md',README)
 for f in sorted(STL.glob('*.stl')):z.write(f,'enclosure_stl/'+f.name)
 for f in sorted((O/'print_first_tests').glob('*.stl')):z.write(f,'print_first_tests/'+f.name)
 for f in sorted((O/'fit_m8_front').glob('*.stl')):z.write(f,'m8_front_fit_tests/'+f.name)
 for f in ['mini_vpin_assembly.step','parts_manifest.json','geometry_checks.json','stl_mesh_checks.json','v1_20_feature_checks.json','print_inventory.csv']:
  if (O/f).exists():z.write(O/f,'cad/'+f)
for src,dst in [('mini_vpin_assembly.step','cabinet-v1_20.step'),('cad_preview.png','preview-v1_20.png')]:
 shutil.copy2(O/src,A/dst)
shutil.copy2(A/'cabinet-v1_20.step',A/'cabinet.step')
shutil.copy2(A/'preview-v1_20.png',A/'preview.png')
with zipfile.ZipFile(A/'front-m8-fit-kit-v1_20.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in ['foot_receiver_left_front.stl','foot_receiver_right_front.stl']:z.write(STL/f,f)
 for f in ['m8_nut_fit_coupon.stl','front_m8_center_pilot_jig.stl']:z.write(A/f,f)
 z.writestr('ASSEMBLY_INSTRUCTIONS.md',README)
print('ASSETS',A,'STL_COUNT',len(list(STL.glob('*.stl'))),'ZIP',zip_path.stat().st_size)
