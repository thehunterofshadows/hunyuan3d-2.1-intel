# Portable Pinball V1.19 — M5 cabinet leg mounting sandwiches

**Source:** `viewer/cad/portable-pinball-v1_19/`. This is a separate version; V1.18 and earlier remain unchanged.

## Changes and hardware

- Replace the four **inside** 50 mm `foot_backing_*` plates and four **outside/below-floor** `foot_receiver_*` discs, plus BOTH floor panels (or carefully enlarge only their existing four corner bolt holes).
- Same four hole centers per mount, at ±13 mm in both X and Y about each leg axis; all 16 through-holes enlarge from 4.5 mm for M4 to **5.5 mm for M5**.
- The **16 metal M5 hex nuts** fit in top-open hexagonal pockets in the inside backing plates: 9.7 mm across vertices (8.40 mm across flats), 4.25 mm pocket depth, intended for typical 8.0 mm-across-flats, 4.0 mm-thick M5 nuts. Actual hardware tolerances must be trial-fitted.
- Inside top backing plates are **6 mm thick**, with 1.75 mm material under each M5 nut pocket; this stays out of the flipper's modeled body/wiring reserve (the 7 mm prototype DID interfere). Mounting receiver flanges remain 8 mm deep; a **10.8 mm diameter by 6.2 mm deep** M5 head recess and **11.3 mm access bore** through each 12 mm-deep boss let common socket-head M5 screws reach their captive nuts from below.
- **16 metal M5 machine screws** (4 per leg); best initial fit candidate is **M5×12 mm socket-head** with a small M5 washer of roughly 10 mm outside diameter, verifying all dimensions. Check actual washer/head thickness, driving access, nut engagement, and clamp force on the test coupon before buying or printing everything. M5×14 may fit without a washer depending on your hardware. The model does not represent individual bolts or washers and does NOT verify bolt head/washer fit.
- **M5×30 is NOT recommended** for the complete cabinet: with the nominal bolt-head seat at Z≈−1.8 mm and shaft length 30 mm the threads reach Z≈28.2, protruding **about 18 mm above the backing plate**. Rear screws can intrude into the Dell PC tray / cable area. Do not rely on length being irrelevant. Use shorter screws or cut/deburr correctly rather than forcing protruding bolts into the cabinet.
- Foot support structure is otherwise the same: **6 × M6×30 external-hex-head bolts**, **6 M6 metal nuts**, **4 M8 metal nuts**, **4 purchased M8 swivel rubber feet**, M6/M8 nut retaining clips and sleeves as V1.18.

## Assembly / fit check

1. Print `foot_backing_left_rear.stl`, `foot_receiver_left_rear.stl`, and the small `m5_floor_mount_coupon.stl` from the **M5 floor mount test ZIP**. The coupon is a 50×50×4 mm patch matching the floor thickness and four M5 hole offsets.
2. Place all four M5 nuts in the *upper* printed backing plate pockets; the nuts remain accessible from above until you assemble the cabinet. Align the floor coupon between the inner backing and outer receiver with M5×12 test bolts inserted from below. A small washer under each head is optional ONLY if it actually fits the counterbore and still allows adequate thread engagement.
3. Verify smooth bolt pass-through, nut anti-rotation, screwdriver clearance through the lower boss, screw length/engagement and no cracking or excessive crushing when tightened modestly. **Do not over-torque PETG.** Check this setup with the exact bolts/nuts you own, before mounting all four feet.
4. Reprint the V1.19 full `bottom_front`/`bottom_rear` panels or drill the old 4.5 mm holes out to 5.5 mm while securely supporting the part; never try forcing an M5 through an old M4 hole. All four receiver/backing plates must be V1.19; the old V1.18 mounting pieces do not fit M5.
5. Assemble M6-to-M8 foot modules per V1.18. Keep front/rear lengths balanced left/right. Recheck PC, USB encoder, flipper bodies and wire bundles for bolt-tip and plate clearance.

**Prototype warning:** CAD valid solids, modeled keepouts and STL mesh closure do not prove real hardware fit, PETG strength, screw clamp force, shock/nudge resistance or safe load capacity. The removable floor-to-wall load path has not been physically load-tested. Test under modest load before using the populated cabinet.
