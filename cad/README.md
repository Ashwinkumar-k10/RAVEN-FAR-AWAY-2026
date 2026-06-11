# CAD — RAVEN Drone & Payload Bay

> **RAVEN** · Rapid Autonomous Victim Emergency Network · FAR AWAY 2026  
> Theme: Agentic & Autonomous Systems

All CAD models for the RAVEN autonomous first-responder drone. Includes the full drone body, payload delivery system, and all printable hardware components. Models are available in STEP (engineering), STL (3D print), and KCL (parametric source) formats.

---

## Drone Components

```
                    [Motor Mount]   [Motor Mount]
                         │               │
              [Drone Arm]┘               └[Drone Arm]
                         \             /
                          [Drone Body ]
                         /             \
              [Drone Arm]┐               ┌[Drone Arm]
                         │               │
                    [Motor Mount]   [Motor Mount]
                              │
                       [Landing Gear]
                              │
                    [Camera Gimbal Mount]  ← front-facing
                              │
                      ┌───────▼────────┐
                      │  Payload Box   │  ← undercarriage
                      │  (first-aid)   │
                      └───── ▼ ────────┘
                      [Servo-hinged Door]
                        opens 90° on DEPLOY state
```

### Part list

| Part | File prefix | Print qty | Notes |
|---|---|---|---|
| Drone Body | `drone_body` | — | Central hub, 110 × 90 mm footprint |
| Drone Arm | `drone_arm` | 4 | 175 mm, M3 motor mount hole pattern |
| Motor Mount | `motor_mount` | 4 | Fits 2212/2216 brushless motors |
| Landing Gear | `landing_gear` | 2 | Clearance for payload bay underneath |
| Camera Gimbal Mount | `camera_gimbal_mount` | 1 | Forward-angled, fits OV5647 Pi Camera |

---

## Payload Delivery System

Mounts to the F450 frame undercarriage. Triggered autonomously by the RAVEN agent FSM on entering the `DEPLOY` state — the MG996R servo rotates 90°, the hinged door swings open, and the first-aid kit releases at the accident scene.

**Kit contents:** bandages · tourniquet · gauze pads · emergency blanket · whistle

| Part | File prefix | Print qty | Dimensions |
|---|---|---|---|
| Payload Box | `raven_payload_box` | 1 | 120 × 80 × 60 mm outer |
| Payload Door | `raven_payload_door` | 1 | 110 × 75 × 2 mm |
| Mounting Bracket | `raven_mounting_bracket` | 2 | 15 × 12 × 12 mm L-bracket |
| Payload Assembly | `raven_assembly` | — | Full combined STEP only |

### Key design features

| Feature | Detail |
|---|---|
| Wall thickness | 2.5 mm PETG throughout |
| Corner fillets | 8 mm radius, all exterior edges |
| Servo linkage slot | 6 × 20 mm on rear wall for MG996R horn rod |
| Thermal sensor slots | 3 × (2 × 15 mm) on front face for MLX90614 line-of-sight |
| Mounting hole pattern | M3, 70 mm spacing — matches F450 bottom plate |
| Hinge pin | 2 mm dia × 78 mm steel rod, press-fit |

---

## File Reference

### STEP Files
Editable B-Rep solids. Import into FreeCAD, Fusion 360, or any STEP-compatible CAD tool for measurement, modification, and assembly verification.

| File | Description |
|---|---|
| `drone_body.step` | Central hub body |
| `drone_arm.step` | Single arm (×4 in assembly) |
| `motor_mount.step` | Motor mount at arm tip |
| `landing_gear.step` | Landing leg |
| `camera_gimbal_mount.step` | Pi Camera forward mount |
| `raven_payload_box.step` | Payload enclosure |
| `raven_payload_door.step` | Servo-actuated door |
| `raven_mounting_bracket.step` | L-bracket for frame attachment |
| `raven_assembly.step` | Full payload assembly (all 4 parts) |

### STL Files
3D print-ready mesh files. Slice directly in PrusaSlicer or Cura.

| File | Description |
|---|---|
| `drone_body.stl` | Central hub |
| `drone_arm.stl` | Arm (print ×4) |
| `motor_mount.stl` | Motor mount (print ×4) |
| `landing_gear.stl` | Landing leg (print ×2) |
| `camera_gimbal_mount.stl` | Camera mount |
| `raven_payload_box.stl` | Payload box |
| `raven_payload_door.stl` | Payload door |
| `raven_mounting_bracket.stl` | L-bracket (print ×2) |

### KCL Files (`/kcl` subfolder)
Parametric source files created in Zoo Design Studio. Edit dimensions and re-export STEP/STL without regenerating from scratch.

| File | Description |
|---|---|
| `kcl/drone_body.kcl` | Hub parametric source |
| `kcl/drone_arm.kcl` | Arm parametric source |
| `kcl/motor_mount.kcl` | Motor mount source |
| `kcl/landing_gear.kcl` | Landing gear source |
| `kcl/camera_gimbal_mount.kcl` | Camera mount source |
| `kcl/raven_payload_box.kcl` | Payload box source |
| `kcl/raven_payload_door.kcl` | Door source |
| `kcl/raven_mounting_bracket.kcl` | Bracket source |

---

## Print Settings

| Setting | Value |
|---|---|
| Material | PETG |
| Layer height | 0.2 mm |
| Infill | 30% gyroid |
| Wall perimeters | 4 |
| Bed temperature | 70 °C |
| Nozzle temperature | 235 °C |
| Supports | Hinge barrels only |
| Estimated filament | ~150 g (payload parts only) |
| Estimated print time | ~4–5 hours (payload parts) |

**Slicer:** PrusaSlicer 2.7+ or Cura 5.x

### Print order
1. `raven_payload_box.stl`
2. `raven_payload_door.stl`
3. `raven_mounting_bracket.stl` × 2
4. `landing_gear.stl` × 2
5. `motor_mount.stl` × 4
6. `drone_arm.stl` × 4
7. `drone_body.stl`
8. `camera_gimbal_mount.stl`

---

## Payload Assembly Instructions

**Tools needed:** M3 × 10 mm bolts (×4), 2 mm steel rod 78 mm, servo horn linkage rod 1.5 mm × 30 mm.

1. Print all payload parts in PETG at settings above.
2. Thread the 2 mm steel hinge pin through both door hinge barrels.
3. Seat the door onto the front-bottom edge of the box — pin fits into the 2.1 mm holes.
4. Pass the servo linkage rod through the rear wall slot, connect to MG996R horn.
5. Bolt both L-brackets onto the box top rim flanges using M3 × 10 mm bolts.
6. Bolt the assembled payload bay to the F450 bottom plate via the bracket top holes.
7. Load first-aid contents, close door (servo at 0°).
8. On `DEPLOY` state — RPi GPIO sends 90° PWM → door opens → kit releases.

---

## Tools Used

| Tool | Version | Licence | Role |
|---|---|---|---|
| Zoo Design Studio | 2025 | Free tier | KCL parametric modelling + STEP export |
| KCL (KittyCAD Language) | — | Apache 2.0 | Parametric source format |
| FreeCAD | 0.21 | LGPL v2+ | Assembly verification and screenshots |
| pythonocc-core | 7.9.0 | LGPL v2.1 | Python assembly of STEP files |
| PrusaSlicer | 2.7+ | AGPL v3 | STL slicing |

All tools are fully open-source and FAR AWAY 2026 compliant. No Fusion 360, Altium, or proprietary tools used.

---

## Reproducing All Files

```bash
# Install dependencies
pip install kittycad
conda install -c conda-forge pythonocc-core=7.9.0

# Set Zoo API token
export ZOO_API_TOKEN=your_token_here   # get from zoo.dev/account

# Generate all 3 payload parts via Zoo API (~5 min)
python generate_raven_cad.py

# Assemble payload parts into single STEP
python assemble_raven.py
```

Drone body, arm, motor mount, landing gear, and camera gimbal KCL files can be edited and re-exported directly from [app.zoo.dev](https://app.zoo.dev) — open the `.kcl` file, modify parameters, export STEP/STL.

---

## Purpose

These CAD models directly support RAVEN's mission:

- **Search and rescue** — drone frame optimised for stability over highway corridors
- **Payload delivery** — autonomous servo release of first-aid kit at accident scene
- **Emergency response** — payload bay sized for tourniquet, bandages, emergency blanket
- **Autonomous deployment** — servo trigger integrated with RAVEN FSM `DEPLOY` state, no human input required

---

## FAR AWAY 2026 Compliance

| Requirement | Status |
|---|---|
| CAD files in `/cad` GitHub folder | ✅ STEP + STL + KCL all committed |
| Open-source CAD tools only | ✅ Zoo Design Studio + FreeCAD + pythonocc |
| Hardware design documented | ✅ Dimensions, print settings, assembly steps |
| Reproducible from source | ✅ KCL source + generation scripts committed |
| No proprietary tools (Fusion 360 etc.) | ✅ Fully compliant |

---

*RAVEN · FAR AWAY 2026 · Agentic & Autonomous Systems · Built with Zoo Design Studio + FreeCAD*