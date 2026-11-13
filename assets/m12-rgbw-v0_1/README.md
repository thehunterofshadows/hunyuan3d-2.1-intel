# M12 RGBW lantern v0.1 — printable accessory concept
Original lantern by ksuszka, Printables #96307: https://www.printables.com/model/96307-milwaukee-m12-lanterntorch
This v0.1 viewer previews ONLY the newly designed parts, in an exploded layout; original battery housing, LED spiral holder, and diffuser are NOT included as files in this public deployment. The original donor geometry is not altered. The new insert nominally uses the original 21x15 mm rocker cutout to provide MODE and BRIGHTNESS tactile switches. This replaces the rocker; the eventual build still needs a physical power cutoff, real tact PCB mounting dimensions, and electronics-board fitting. The LED carrier is an 84mm universal cable-tie accessory that fits only if the donor inner tube measures >=30.4 mm. Print the 3mm diameter-fit ring first, then bezel fit coupon, then only print the full spine after physical trial assembly.
## Electronics requirements
M12 -> inline fuse -> independent, correctly configured 3S low-voltage disconnect with hysteresis -> regulated 5V DC/DC -> ESP32 and SK6812 RGBW LEDs. WLED mode and brightness mapping requires actual firmware configuration, not included in this mechanical CAD release. Battery voltage sensing, logic level shifter, capacitor, insulation, low battery cutoff, thermal control and master battery disconnect must be validated on the bench. Don't charge via this lantern. Actual LED strip and controller choice might require redesign.
## Current files
- stl/rocker-slot_two-button_bezel.stl
- stl/mode_and_brightness_button_cap.stl (print TWO)
- stl/esp32_cutoff_electronics_spine.stl
- stl/electronics_spine_diameter_fit_gauge.stl
- m12-accessories-v0_1.step
## Safety/status
Mechanical geometry passes watertight mesh checks only. NO print fit checks, electrical tests, thermal validation, or battery-pack cutoff testing have occurred. Keep original battery contacts and slide geometry unchanged. Confirm the original author's redistribution license before publishing their source models.
