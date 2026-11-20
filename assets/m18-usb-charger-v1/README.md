# Milwaukee M18 USB Charger Adapter — V1

## Prototype status
**Mechanical fit-test prototype only.** This download contains the NEW printable upper shell, NOT an electrically completed or verified phone charger. Do not connect a battery to unprotected contacts.

## Components / files
- `stl/M18_USB_Socket_Housing_v1.stl`: new printable upper housing. Print upside-down with roof on bed; prefer heat-resistant filament such as ASA or suitable PETG. Initial trial: 0.2 mm layers, 4+ walls, 30–40% infill. Actual thermal and fit suitability is untested.
- `m18-usb-socket-housing-v1.step`: editable housing CAD.
- `m18-usb-charger-v1.glb`: interactive preview **of the new shell only**.
- `README.md`: build and source notes.

To complete the mechanical assembly, separately obtain the original *Battery Connector for Milwaukee M18* by Wiseone (3 STL pieces; Printables model 219711) and *Accessory Power Outlet* by EWJ (socket STL; Printables model 1603552). These original components have NOT been included in this website pack.

## Key geometry
- Existing M18 slide plate is nominally 69 x 77 mm. Upper shell bounding size about 68.2 x 76.1 x 48.8 mm.
- Shell uses four underside M3 heat-set pilot pockets matching original slide plate locations; verify actual insert size and screw engagement.
- Socket roof hole diameter 29.1 mm with two M4 clearance holes on 34.5 mm centers for EWJ's socket.
- Unallocated forward space for a future protection board; **not fitted** to any particular low-voltage cutoff.

## Electrical warnings
- **No low-voltage cutoff or fuse has been installed, sized or tested in this printable file.** An independent fused low-voltage disconnect is needed before powering the charger.
- Do not assume the printed EWJ socket's hose-clamp contact can safely carry 67.5 W continuously. The source author warns of increased contact resistance and heating. Use rated metal contacts and test under load.
- Verify the actual AINOPE charger's marked input rating accepts the 21 V maximum of a freshly charged 5S M18 pack.
- Test insulation, polarity, current capacity, fuse, cutoff and case temperature with a current-limited supply before battery use.
- Not weatherproof.

## Attribution and licenses
- M18 battery adapter source: Wiseone, *Battery Connector for Milwaukee M18 (Updated: 08/11/2023)*, Printables model 219711, **CC BY-NC 4.0**. Original source NOT bundled here.
- Socket source: EWJ (@EWJ_2138826), *Accessory Power Outlet (cigarette lighter socket)*, Printables model 1603552, **CC BY-SA 4.0**. Original source NOT bundled here.
- New upper shell is a noncommercial mechanical prototype based on mounting dimensions for those adapters. Respect upstream attribution and licenses before sharing any combined derivative.
