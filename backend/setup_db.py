# -*- coding: utf-8 -*-
"""
Database initialization and sample data seeder for RIG Query Agent.
Run: python setup_db.py
"""
import os
import sys
from datetime import datetime, timedelta
from database import create_tables, SessionLocal, WorkPack, Procedure, Operation, Shift, Checklist, ChecklistItem, EquipmentKB
from dotenv import load_dotenv

load_dotenv()

def seed_work_packs(db):
    work_packs_data = [
        ("WP001", "Pump Maintenance", "Active", "High", "2024-01-15", "Routine maintenance of primary mud pump system including seal replacement and bearing inspection."),
        ("WP002", "BOP Pressure Test", "In Progress", "High", "2024-01-16", "Full pressure test of blowout preventer stack per API 16A specifications."),
        ("WP003", "Drill Pipe Inspection", "Completed", "Medium", "2024-01-10", "Visual and dimensional inspection of all drill pipe in current BHA."),
        ("WP004", "Valve Inspection", "Active", "High", "2024-01-17", "Comprehensive inspection of all choke and kill line valves."),
        ("WP005", "Top Drive Service", "In Progress", "High", "2024-01-18", "500-hour service interval for top drive unit including gear oil change."),
        ("WP006", "Mud System Calibration", "Pending", "Medium", "2024-01-19", "Calibration of all mud weight and flow sensors in the circulating system."),
        ("WP007", "Drill Pipe Replacement", "Active", "High", "2024-01-20", "Replace worn drill pipe sections identified during WP003 inspection."),
        ("WP008", "Draw Works Inspection", "Completed", "Medium", "2024-01-08", "Annual inspection of draw works braking system and drum bearings."),
        ("WP009", "Rotary Table Service", "In Progress", "Medium", "2024-01-21", "Lubrication and alignment check for rotary table and master bushing."),
        ("WP010", "Choke Manifold Test", "Active", "High", "2024-01-22", "Functional test of all choke manifold valves and pressure gauges."),
        ("WP011", "Shaker Screen Replacement", "Completed", "Low", "2024-01-05", "Replacement of worn shaker screens on primary and secondary shakers."),
        ("WP012", "Pump 2 Overhaul", "Pending", "High", "2024-01-23", "Complete overhaul of secondary mud pump including liner and piston replacement."),
        ("WP013", "Derrick Inspection", "Active", "Medium", "2024-01-24", "Monthly structural inspection of derrick legs and crown block assembly."),
        ("WP014", "Chemical Injection Test", "In Progress", "Low", "2024-01-25", "Test and calibrate chemical injection pumps for corrosion inhibitor dosing."),
        ("WP015", "Emergency Shutdown Test", "Pending", "High", "2024-01-26", "Full functional test of emergency shutdown system per safety protocols."),
    ]
    created = []
    for code, name, status, priority, date, desc in work_packs_data:
        wp = WorkPack(code=code, name=name, status=status, priority=priority, created_date=date, description=desc)
        db.add(wp)
        created.append(wp)
    db.commit()
    return created

def seed_procedures(db, work_packs):
    # Map work pack code to object
    wp_map = {wp.code: wp for wp in work_packs}
    
    procedures_data = [
        # WP001 - Pump Maintenance
        ("P001", "Pump Inspection", "Completed", "J. Peterson", "WP001"),
        ("P002", "Seal Replacement", "In Progress", "M. Rodriguez", "WP001"),
        ("P003", "Bearing Check", "Pending", "J. Peterson", "WP001"),
        # WP002 - BOP Pressure Test
        ("P004", "BOP Ram Test", "In Progress", "K. Williams", "WP002"),
        ("P005", "Annular Preventer Test", "Pending", "K. Williams", "WP002"),
        ("P006", "Choke Line Pressure Test", "Pending", "D. Chen", "WP002"),
        # WP003 - Drill Pipe Inspection
        ("P007", "Visual Inspection DP-1", "Completed", "T. Brooks", "WP003"),
        ("P008", "Dimensional Check DP-2", "Completed", "T. Brooks", "WP003"),
        ("P009", "Thread Condition Check", "Completed", "M. Rodriguez", "WP003"),
        # WP004 - Valve Inspection
        ("P010", "Choke Valve Inspection", "In Progress", "D. Chen", "WP004"),
        ("P011", "Kill Line Valve Test", "Pending", "K. Williams", "WP004"),
        ("P012", "Hydraulic Line Check", "Pending", "J. Peterson", "WP004"),
        # WP005 - Top Drive Service
        ("P013", "Gear Oil Change", "Completed", "R. Alvarez", "WP005"),
        ("P014", "Swivel Inspection", "In Progress", "R. Alvarez", "WP005"),
        ("P015", "Motor Brush Check", "Pending", "T. Brooks", "WP005"),
        # WP006 - Mud System Calibration
        ("P016", "Flow Sensor Calibration", "Pending", "D. Chen", "WP006"),
        ("P017", "Density Sensor Check", "Pending", "M. Rodriguez", "WP006"),
        # WP007 - Drill Pipe Replacement
        ("P018", "Remove Worn Sections", "In Progress", "T. Brooks", "WP007"),
        ("P019", "Install New Pipe Sections", "Pending", "T. Brooks", "WP007"),
        ("P020", "Thread Inspection Post-Install", "Pending", "J. Peterson", "WP007"),
        # WP008 - Draw Works Inspection
        ("P021", "Brake System Check", "Completed", "R. Alvarez", "WP008"),
        ("P022", "Drum Bearing Inspection", "Completed", "R. Alvarez", "WP008"),
        ("P023", "Cable Wear Assessment", "Completed", "K. Williams", "WP008"),
        # WP009 - Rotary Table Service
        ("P024", "Master Bushing Lubrication", "Completed", "D. Chen", "WP009"),
        ("P025", "Alignment Verification", "In Progress", "J. Peterson", "WP009"),
        # WP010 - Choke Manifold Test
        ("P026", "Manual Choke Valve Test", "In Progress", "K. Williams", "WP010"),
        ("P027", "Remote Choke Valve Test", "Pending", "D. Chen", "WP010"),
        ("P028", "Pressure Gauge Calibration", "Pending", "M. Rodriguez", "WP010"),
        # WP011 - Shaker Screen
        ("P029", "Remove Old Screens", "Completed", "T. Brooks", "WP011"),
        ("P030", "Install New Screens", "Completed", "T. Brooks", "WP011"),
        # WP012 - Pump 2 Overhaul
        ("P031", "Pump Shutdown Procedure", "Pending", "M. Rodriguez", "WP012"),
        ("P032", "Liner Replacement", "Pending", "J. Peterson", "WP012"),
        ("P033", "Piston Rod Inspection", "Pending", "R. Alvarez", "WP012"),
        # WP013 - Derrick Inspection
        ("P034", "Crown Block Inspection", "In Progress", "K. Williams", "WP013"),
        ("P035", "Derrick Leg Structural Check", "Pending", "T. Brooks", "WP013"),
        # WP014 - Chemical Injection
        ("P036", "Injection Pump Calibration", "In Progress", "D. Chen", "WP014"),
        ("P037", "Chemical Line Integrity Test", "Pending", "M. Rodriguez", "WP014"),
        # WP015 - Emergency Shutdown
        ("P038", "ESD Logic Test", "Pending", "K. Williams", "WP015"),
        ("P039", "Panel Indicator Verification", "Pending", "J. Peterson", "WP015"),
        ("P040", "Emergency Valve Actuation Test", "Pending", "R. Alvarez", "WP015"),
    ]
    
    created = []
    for code, name, status, assigned, wp_code in procedures_data:
        wp = wp_map.get(wp_code)
        proc = Procedure(
            code=code, name=name, status=status,
            assigned_to=assigned, work_pack_id=wp.id if wp else None
        )
        db.add(proc)
        created.append(proc)
    db.commit()
    return created

def seed_operations(db, procedures):
    # Generic operation templates for each procedure
    op_templates = {
        "Pump Inspection": ["Shutdown pump safely", "Check pressure gauges", "Inspect pump bearings", "Check for leaks", "Document findings", "Restart pump", "Verify normal operation", "Log results"],
        "Seal Replacement": ["Isolate pump from system", "Drain pump casing", "Remove old seals", "Clean seal grooves", "Install new seals", "Reassemble casing", "Pressure test", "Return to service"],
        "default": ["Prepare work area", "Isolate equipment", "Perform inspection/work", "Test functionality", "Document results", "Return to service"],
    }
    
    ops_created = 0
    for proc in procedures:
        template = op_templates.get(proc.name, op_templates["default"])
        # Add some variation - 3 to 8 operations per procedure
        num_ops = min(len(template), max(3, len(template)))
        for i, op_name in enumerate(template[:num_ops]):
            status_choices = ["Completed", "In Progress", "Pending"]
            # Make status consistent with procedure status
            if proc.status == "Completed":
                op_status = "Completed"
            elif proc.status == "Pending":
                op_status = "Pending"
            else:
                op_status = status_choices[i % 3]
            
            op = Operation(
                name=op_name,
                step_order=i + 1,
                status=op_status,
                procedure_id=proc.id
            )
            db.add(op)
            ops_created += 1
    db.commit()
    print(f"Created {ops_created} operations")

def seed_shifts(db):
    operators = [
        "J. Peterson", "M. Rodriguez", "K. Williams", "D. Chen",
        "T. Brooks", "R. Alvarez", "S. Mitchell", "A. Johnson",
        "B. Harris", "C. Martinez"
    ]
    shift_types = ["Morning", "Afternoon", "Night"]
    
    shifts = []
    base_date = datetime(2024, 1, 20)
    
    for i in range(20):
        operator = operators[i % len(operators)]
        shift_type = shift_types[i % 3]
        date = base_date - timedelta(days=i // 3)
        
        if shift_type == "Morning":
            login = date.replace(hour=6, minute=0)
            logout = date.replace(hour=14, minute=0) if i > 0 else None
        elif shift_type == "Afternoon":
            login = date.replace(hour=14, minute=0)
            logout = date.replace(hour=22, minute=0) if i > 0 else None
        else:
            login = date.replace(hour=22, minute=0)
            logout = (date + timedelta(days=1)).replace(hour=6, minute=0) if i > 1 else None
        
        # Most recent shift is Active
        status = "Active" if i == 0 else "Completed"
        
        shift = Shift(
            operator_name=operator,
            shift_type=shift_type,
            login_time=login.strftime("%Y-%m-%d %H:%M"),
            logout_time=logout.strftime("%Y-%m-%d %H:%M") if logout else None,
            status=status,
            date=date.strftime("%Y-%m-%d")
        )
        db.add(shift)
        shifts.append(shift)
    
    db.commit()
    print(f"Created {len(shifts)} shifts")
    return shifts

def seed_checklists(db, work_packs):
    checklists_data = [
        ("Pump Inspection Checklist", "Mud Pump", "WP001"),
        ("BOP Ram Inspection Checklist", "Blowout Preventer", "WP002"),
        ("Drill Pipe Inspection Checklist", "Drill Pipe", "WP003"),
        ("Valve Maintenance Checklist", "Choke Manifold", "WP004"),
        ("Top Drive Service Checklist", "Top Drive", "WP005"),
        ("Mud System Calibration Checklist", "Mud System", "WP006"),
        ("Draw Works Inspection Checklist", "Draw Works", "WP008"),
        ("Rotary Table Service Checklist", "Rotary Table", "WP009"),
        ("Choke Manifold Test Checklist", "Choke Manifold", "WP010"),
        ("Shaker Screen Replacement Checklist", "Shale Shaker", "WP011"),
        ("Pump Overhaul Checklist", "Mud Pump", "WP012"),
        ("Derrick Inspection Checklist", "Derrick Structure", "WP013"),
        ("Chemical Injection Checklist", "Chemical System", "WP014"),
        ("Emergency Shutdown Checklist", "ESD System", "WP015"),
        ("Mud Motor Inspection Checklist", "Mud Motor", None),
        ("Hook and Swivel Inspection Checklist", "Hook", None),
        ("Kelly Drive Maintenance Checklist", "Kelly", None),
        ("Accumulator Unit Inspection Checklist", "BOP Accumulator", None),
        ("Degasser Maintenance Checklist", "Degasser", None),
        ("Crown Block Inspection Checklist", "Crown Block", None),
    ]
    
    wp_map = {wp.code: wp for wp in work_packs}
    created = []
    
    for name, equip, wp_code in checklists_data:
        wp = wp_map.get(wp_code) if wp_code else None
        cl = Checklist(
            name=name,
            equipment=equip,
            created_date="2024-01-20",
            work_pack_id=wp.id if wp else None
        )
        db.add(cl)
        created.append(cl)
    
    db.commit()
    
    # Now add checklist items
    items_templates = {
        "Mud Pump": [
            ("Verify pump is safely isolated and locked out", True, 1),
            ("Check suction and discharge valve positions", True, 2),
            ("Inspect pump liner for wear (max 0.015\" oversize)", True, 3),
            ("Check piston rod for scoring or pitting", True, 4),
            ("Inspect all seals and packing for leaks", True, 5),
            ("Check bearing temperatures (max 180°F)", True, 6),
            ("Verify lube oil level and quality", True, 7),
            ("Inspect discharge pulsation dampener", False, 8),
            ("Check suction stabilizer pre-charge pressure", True, 9),
            ("Record vibration levels (DE and NDE)", True, 10),
            ("Inspect pump head stud torque values", True, 11),
            ("Check fluid end bolting", True, 12),
            ("Verify pressure relief valve set point", True, 13),
            ("Inspect driving belt or coupling condition", False, 14),
            ("Document all findings in maintenance log", True, 15),
        ],
        "Blowout Preventer": [
            ("Confirm BOP is depressurized before work", True, 1),
            ("Inspect annular element for wear or extrusion", True, 2),
            ("Check ram block condition and packer rubber", True, 3),
            ("Verify hydraulic fluid level in accumulator", True, 4),
            ("Test open/close function of all rams", True, 5),
            ("Check wellbore seal integrity", True, 6),
            ("Inspect choke and kill line connections", True, 7),
            ("Verify control panel indicator lights", True, 8),
            ("Document pressure test results per API 16A", True, 9),
            ("Check emergency close function (dead man)", True, 10),
        ],
        "default": [
            ("Review work order and safety requirements", True, 1),
            ("Ensure proper PPE is worn", True, 2),
            ("Isolate and lockout equipment", True, 3),
            ("Perform visual inspection", True, 4),
            ("Check for leaks or damage", True, 5),
            ("Lubricate moving parts as required", False, 6),
            ("Test functionality post-maintenance", True, 7),
            ("Document findings and return to service", True, 8),
        ]
    }
    
    total_items = 0
    for cl in created:
        template = items_templates.get(cl.equipment, items_templates["default"])
        for desc, required, step in template:
            item = ChecklistItem(
                description=desc,
                is_required=required,
                step_number=step,
                checklist_id=cl.id
            )
            db.add(item)
            total_items += 1
    
    db.commit()
    print(f"Created {len(created)} checklists with {total_items} items")
    return created

def seed_equipment_kb(db):
    equipment_docs = [
        ("Mud Pump", """MUD PUMP - EQUIPMENT MANUAL
Model: National 12-P-160 Triplex Pump
Manufacturer: National Oilwell Varco

OVERVIEW:
The mud pump is a reciprocating positive displacement pump used to circulate drilling fluid (mud) through the drill string, bit, and back up the annulus to surface. It is one of the most critical pieces of equipment on the rig.

FUNCTION:
The primary function of the mud pump is to circulate drilling fluid at high pressure and volume. This circulation serves multiple purposes: cooling and lubricating the drill bit, carrying drill cuttings to the surface, maintaining hydrostatic pressure to prevent formation fluid influx, and providing hydraulic power to downhole tools.

SPECIFICATIONS:
- Maximum pressure: 7,500 PSI
- Maximum flow rate: 1,600 GPM
- Stroke rate: up to 160 SPM
- Input power: 1,600 HP
- Liner sizes: 5" to 7.5"

MAIN COMPONENTS:
1. Power End: Contains the crankshaft, connecting rods, crossheads, and bearings. Converts rotary motion to reciprocating motion.
2. Fluid End: Contains liners, pistons, valves (suction and discharge), and valve covers. The fluid end handles the pumping action.
3. Pulsation Dampener: Reduces pressure surges in the discharge line.
4. Suction Stabilizer: Ensures smooth suction of drilling fluid.
5. Relief Valve: Safety device set at maximum allowable pump pressure.

OPERATION:
The crankshaft, driven by a diesel engine or electric motor, rotates and drives the connecting rods. The connecting rods move the crossheads in a reciprocating motion, which drives the pistons in the liner bores. On the suction stroke, the piston moves back, creating a vacuum that opens the suction valve and draws mud into the liner. On the discharge stroke, the piston moves forward, pressurizing the mud and forcing it out through the discharge valve into the stand pipe manifold.

MAINTENANCE:
Mud pumps require regular maintenance to sustain efficiency:
- Daily: Check fluid level, listen for unusual noise, check packing for leaks
- Weekly: Inspect valves and seats, check liner wear, lubricate crossheads
- Monthly: Full bearing inspection, replace worn liners and pistons
- 500 Hours: Complete fluid end overhaul, replace all seals and packing

TROUBLESHOOTING:
- Low pressure: Worn or damaged valves, worn liner/piston, suction leak
- High pressure: Plugged bit nozzles, packoff in annulus, restricted flow
- Knocking noise: Loose liner clamp, worn crosshead pin, loose fluid end bolts
- Excessive vibration: Unbalanced crankshaft, worn main bearings, improper foundation
"""),
        ("Top Drive", """TOP DRIVE - EQUIPMENT MANUAL
Model: Canrig 1275AC Top Drive System
Manufacturer: Nabors Industries

OVERVIEW:
The top drive is a power swivel mounted in the derrick that provides rotational force to the drill string from the top, replacing the conventional kelly and rotary table for drilling operations. It allows continuous rotation while making connections, drilling directional wells, and running casing.

FUNCTION:
The top drive performs rotary drilling by rotating the drill string from the top. Unlike the kelly/rotary table system, the top drive allows the driller to drill a full stand of pipe (approximately 90 feet) without stopping to make connections at the rotary table. This significantly improves drilling efficiency and reduces the risk of stuck pipe.

SPECIFICATIONS:
- Maximum torque: 75,000 ft-lbs continuous, 100,000 ft-lbs intermittent
- Maximum RPM: 250
- Maximum hook load: 1,000,000 lbs
- Motor power: 1,275 HP (AC)
- Weight: 65,000 lbs

MAIN COMPONENTS:
1. Motor: AC or DC electric motor providing torque to the drill string.
2. Gearbox: Reduces motor RPM to drilling RPM and multiplies torque.
3. Main Shaft: Transfers torque from gearbox to the saver sub.
4. Swivel: Allows rotation while maintaining a sealed fluid path for drilling mud.
5. Link Tilts and Elevator: Handle tubulars for making and breaking connections.
6. Torque Arrest System: Guide rails and dolly that prevent the unit from spinning.
7. Control System: PLC-based system controlling motor speed and torque limits.

OPERATION:
The top drive travels in the derrick on a track system. During drilling, the driller controls rotation speed (RPM) and torque through the driller's console. Drilling fluid passes through the swivel and main shaft into the drill string. For connections, the top drive stops rotation, the pipe is set in slips, the connection is made, and drilling resumes. The back-reaming capability allows upward drilling motion for difficult wellbore conditions.

MAINTENANCE:
- 8 Hours: Check gear oil level, inspect for leaks
- 50 Hours: Lubricate all grease points, check brake function
- 250 Hours: Inspect swivel seals, check gearbox oil
- 500 Hours: Full gear oil change, inspect motor brushes (DC), check main shaft run-out
- Annual: Complete bearing inspection, motor rewind assessment
"""),
        ("Blowout Preventer", """BLOWOUT PREVENTER (BOP) - EQUIPMENT MANUAL
Model: Cameron Type U RAM BOP
Manufacturer: Schlumberger (Cameron)

OVERVIEW:
The Blowout Preventer (BOP) is a large specialty valve or series of valves installed at the wellhead to prevent uncontrolled release of crude oil, natural gas, or other well fluids from the wellbore. It is the primary well control barrier on any drilling rig.

FUNCTION:
The BOP stack is designed to seal the wellbore in the event of a well control situation (kick). It can seal around the drill string (pipe rams), across an open wellbore (blind/shear rams), or around irregular pipe shapes (annular preventer). The BOP protects rig personnel, equipment, and the environment from blowouts.

SPECIFICATIONS:
- Working pressure: 15,000 PSI
- Bore size: 18-3/4"
- Temperature rating: -20°F to 250°F
- Hydraulic operating pressure: 1,500 PSI
- Accum volume: 120 gallons (minimum API 16A)

BOP STACK COMPONENTS:
1. Annular Preventer (Bag Type): Top of stack, seals around any tubular or open hole.
2. Upper Pipe Rams: Sized to seal around drill pipe OD.
3. Variable Bore Rams: Can seal around range of pipe sizes.
4. Blind/Shear Rams: Cuts drill pipe and seals open wellbore.
5. Choke and Kill Lines: Side outlets for controlling well pressure.
6. BOP Control System (Accumulator): Hydraulic power unit for BOP actuation.

OPERATION:
In normal drilling, the BOP is open (unlatched). Upon detecting a kick (influx of formation fluids), the driller activates the BOP control panel. The annular preventer closes first (quick, seals around any pipe), followed by pipe rams if the situation worsens. If pipe must be cut and hole sealed, shear rams are activated. The choke line is then used to kill the well by circulating heavy mud.

TESTING REQUIREMENTS (API 16A):
- Low pressure test: 200-300 PSI (verify seal function)
- Full working pressure test: 15,000 PSI
- Testing frequency: Every 14 days or after disconnection
- Function test: Every 7 days
"""),
        ("Rotary Table", """ROTARY TABLE - EQUIPMENT MANUAL
Model: National 27-1/2" Rotary Table
Manufacturer: National Oilwell Varco

OVERVIEW:
The rotary table is a mechanical device on the rig floor that provides clockwise rotation to the drill string. In modern rigs equipped with top drives, the rotary table serves as a backup rotation system and holds the drill string in place via slips during connections.

FUNCTION:
In conventional drilling, the rotary table transmits torque to the kelly, which drives the drill string. In top drive operations, the rotary table houses the master bushing and slip bowl, which hold the drill string weight during connections and trips.

SPECIFICATIONS:
- Bore size: 27-1/2"
- Rated static load: 1,500,000 lbs
- Maximum rotary speed: 300 RPM
- Drive: Chain drive from drawworks or independent electric motor
- Weight: 22,000 lbs

MAIN COMPONENTS:
1. Ring Gear: Large gear driven by the chain drive or motor pinion.
2. Pinion Gear: Meshes with ring gear to transmit power.
3. Master Bushing: Fits into the rotary table opening, accepts kelly bushing or drill pipe slips.
4. Kelly Bushing: Square or hexagonal drive bushing that fits the kelly.
5. Rotary Bearings: Large tapered roller bearings that support vertical load.
6. Rotary Lock: Mechanical lock to prevent rotation during connections.

OPERATION:
During rotary drilling, the rotary table is engaged and rotates at the driller's selected RPM. The kelly passes through the kelly bushing, which has a matching square or hexagonal bore, and torque is transmitted to the drill string. During top drive operations, the kelly bushing is removed and drill pipe slips are seated in the master bushing to hold the string while connections are made.

MAINTENANCE:
- Daily: Check for unusual noise, check oil level, inspect lock mechanism
- Weekly: Lubricate master bushing, check drive chain tension and lubrication
- Monthly: Inspect rotary bearings for play, check ring gear teeth condition
- 6 Months: Complete oil change, full bearing inspection, alignment check
"""),
        ("Drill Pipe", """DRILL PIPE - EQUIPMENT MANUAL AND INSPECTION STANDARDS
Specification: API 5DP Grade S-135
Outer Diameter: 5" (127mm)
Wall Thickness: 0.362"

OVERVIEW:
Drill pipe is hollow steel pipe used in drilling operations to transmit drilling fluid, provide rotational torque to the drill bit, and to apply weight on bit. Drill pipe connects the surface equipment (swivel/top drive) to the bottom hole assembly (BHA) and drill bit.

FUNCTION:
Drill pipe serves three primary functions: (1) transmitting rotation from the rotary table or top drive to the drill bit, (2) providing a conduit for drilling fluid to flow from surface pumps to the drill bit, and (3) allowing the driller to apply controlled weight to the drill bit to achieve penetration.

SPECIFICATIONS:
- Grade: S-135 (minimum yield strength 135,000 PSI)
- Outer diameter: 5.0"
- Nominal weight: 19.5 lb/ft
- Wall thickness: 0.362"
- Joint type: NC50 (API IF)
- Unit length: 30-32 feet (Range 2)

COMPONENTS:
1. Tube Body: Main cylindrical steel tube.
2. Tool Joint Pin: Male threaded end at bottom of each joint.
3. Tool Joint Box: Female threaded end at top of each joint.
4. Upset: Thickened section at ends where tool joints are welded.

INSPECTION CRITERIA (API RP 7G):
Grade 1 (Premium): Used in critical sections, strictest tolerances
- OD wear: Not more than 80% of original OD
- Wall thickness: Not less than 80% of nominal wall
- No longitudinal cracks
- Slip cut depth: Not more than 1/8"

Grade 2: Reduced service, use in low-stress sections
Reject Criteria: Excessive wear, cracks, damaged threads, corrosion pits over limit

INSPECTION METHODS:
- Visual: External and internal surface examination
- Dimensional: OD measurement with calipers/ring gauge
- Electromagnetic: EMI inspection for body defects
- Ultrasonic: Wall thickness measurement, crack detection
- Magnetic Particle (MPI): Thread and upset area inspection
"""),
        ("Choke Manifold", """CHOKE MANIFOLD - EQUIPMENT MANUAL
Model: Cameron 15,000 PSI Choke Manifold
Manufacturer: Cameron International

OVERVIEW:
The choke manifold is an arrangement of high-pressure valves, chokes, and fittings used to control wellbore pressure during a well control event. It is connected to the BOP choke line outlet and is used to circulate out a kick safely.

FUNCTION:
The choke manifold provides controlled pressure release from the wellbore. During a kick circulation, the driller uses the adjustable choke to maintain backpressure on the wellbore while circulating heavy kill-weight mud to restore hydrostatic balance. The manifold also provides access points for kill operations, pressure monitoring, and well integrity testing.

SPECIFICATIONS:
- Working pressure: 15,000 PSI
- Bore: 3" minimum
- End connections: 3" 15M flanges per API 6A
- Material: Carbon steel, H2S trim for sour service
- Choke type: Fixed and adjustable positive chokes

COMPONENTS:
1. Manual Chokes: Fixed orifice chokes with interchangeable beans.
2. Adjustable Choke: Variable orifice choke with remote or manual operation.
3. Wing Valves: Gate valves to isolate sections of the manifold.
4. Master Valves: Primary isolation valves.
5. Pressure Gauges: High-pressure Bourdon tube gauges.
6. Remote Choke Panel: Driller's console with choke position indicator and pressure displays.

OPERATION:
When a kick is detected, the well is shut-in using the BOP. Pressure is then monitored on the drill pipe and casing pressure gauges. The kill operation begins by slowly opening the adjustable choke while bringing the mud pump up to kill rate. The choke operator maintains constant casing pressure (constant casing pressure method) or constant drill pipe pressure (driller's method) while pumping heavy mud down the drill string.

MAINTENANCE:
- Daily during operations: Check choke bean condition, verify valve operation
- Weekly: Lubricate all valve stems, test remote choke operation
- Monthly: Full pressure test to working pressure
- After each use: Inspect choke for erosion, replace if worn beyond limits
"""),
        ("Mud Motor", """MUD MOTOR (POSITIVE DISPLACEMENT MOTOR) - EQUIPMENT MANUAL
Model: Navi-Drill X-treme Series
Manufacturer: Baker Hughes

OVERVIEW:
A mud motor (or positive displacement motor, PDM) is a downhole tool used in directional drilling that converts hydraulic power from drilling fluid flow into mechanical rotation at the drill bit. It allows the drill bit to rotate without rotating the entire drill string.

FUNCTION:
Mud motors are used in directional drilling to orient and steer the wellbore. The motor is placed in the BHA above the drill bit. When drilling fluid is pumped through the motor, the rotor rotates, turning the bit. By orienting the motor's bent housing to a specific tool face, the bit drills in a desired direction without rotating the string above (sliding mode). The string can also be rotated slowly to drill ahead (rotating mode).

SPECIFICATIONS:
- OD: 6-3/4"
- Power stages: 7/8 lobe configuration
- Maximum flow rate: 650 GPM
- Maximum RPM at bit: 220
- Maximum differential pressure: 1,200 PSI
- Bent housing angle: 0° to 3°

OPERATION:
The mud motor operates on the Moineau principle. The stator is a helically shaped rubber element bonded inside a steel housing. The rotor is a helically shaped steel shaft that fits inside the stator. When drilling mud flows through the spiraling cavities between rotor and stator, the pressure differential causes the rotor to turn. This rotation is transmitted through a flex shaft (CV joint) and the bent housing to the drill bit.

MAINTENANCE:
- After each run: Complete external inspection, measure wear on rotor and stator
- Check bearing section for float and play
- Inspect flex shaft for cracks or wear
- Inspect bent housing setting
- Power section inspection: Rotor-stator fit, elastomer condition
- Replace stator if differential pressure capability has degraded significantly
"""),
        ("Draw Works", """DRAW WORKS - EQUIPMENT MANUAL
Model: National 1625-UE Drawworks
Manufacturer: National Oilwell Varco

OVERVIEW:
The draw works is the primary hoisting machinery on a drilling rig. It consists of a large winch-like drum driven by high-horsepower prime movers, used to control the vertical movement of the drill string, casing, and other tubulars in the wellbore.

FUNCTION:
The draw works spools and unspools the drilling line (wire rope) to raise and lower the traveling block, hook, and attached equipment. During drilling, the driller uses the draw works to control weight on bit (WOB) by carefully managing the hook load. During trips, the draw works lifts the entire drill string out of the hole and lowers it back in.

SPECIFICATIONS:
- Maximum hook load: 1,500,000 lbs
- Rated horsepower: 3,000 HP
- Number of lines: 14 (7 fast lines)
- Drum grooves: Lebus type
- Braking system: Hydrodynamic (auxiliary) + disc brakes (parking)
- Weight: 180,000 lbs

MAIN COMPONENTS:
1. Main Drum: Large spool that stores the drilling line (wire rope).
2. Crown-O-Matic: Automatic driller/anti-collision system.
3. Electromagnetic Brake (Deadline Anchor): Measures hook load and deadline tension.
4. Hydrodynamic Brake (Hydromatic): Primary working brake for controlled descent.
5. Mechanical Band Brakes: Backup braking system.
6. Cathead: Spinning and backup cathead for making and breaking connections.
7. Transmission: Multi-speed gear transmission.

SAFETY:
Draw works is one of the most hazardous pieces of rig equipment. Key safety systems include:
- Anti-collision devices (crown-o-matic, floor-o-matic)
- Automatic driller (weight on bit control)
- Emergency braking systems
- Load indicators and weight sensors
"""),
        ("Kelly", """KELLY DRIVE SYSTEM - EQUIPMENT MANUAL
Specification: API 7K Kelly Drive
Type: Square Kelly, 55 feet long

OVERVIEW:
The kelly is a long steel bar with a polygonal cross-section (square or hexagonal) that passes through a matching opening in the kelly bushing. The kelly transmits rotary motion from the rotary table to the drill string while allowing vertical movement during drilling.

FUNCTION:
As the rotary table turns the kelly bushing, the kelly slides downward through the bushing while simultaneously rotating with it, transmitting torque to the drill string below. This allows the drill string to advance downward as formation is drilled while maintaining rotary drive.

SPECIFICATIONS:
- Length: 40 or 54 feet (54 feet standard)
- Shape: Square (4 sides) or hexagonal (6 sides)
- Square kelly width: 4-1/4" across flats
- Material: Chrome-moly alloy steel
- Upper connection: Saver sub + swivel
- Lower connection: Kelly cock + kelly saver sub

COMPONENTS:
1. Upper Kelly Cock: Full-opening valve at top of kelly; prevents backflow.
2. Kelly Saver Sub: Protects kelly lower thread from wear.
3. Kelly Bushing: Drive bushing with matching square/hexagonal bore.
4. Kelly Drive Pins (Square): Kelly bushing engages via pins on square kelly.

INSPECTION AND MAINTENANCE:
- Daily: Lubricate kelly with kelly lubricator, inspect for cracks or twist
- Weekly: Inspect saver subs, check kelly cock operation
- Monthly: Full dimensional inspection, check for twist or bend
- Replace: If significant twist, cracks in flats, or worn-out threads

NOTE: With the adoption of top drives in modern drilling, the kelly system has become less common on new rigs but remains in use on many older rigs worldwide.
"""),
        ("Hook", """TRAVELING BLOCK AND HOOK - EQUIPMENT MANUAL
Model: National 750-Ton Traveling Block with Hook
Manufacturer: National Oilwell Varco

OVERVIEW:
The traveling block and hook are hoisting equipment suspended from the crown block by the drilling line. The traveling block contains multiple sheaves around which the drilling line is reeved. The hook hangs below the traveling block and connects to the swivel or top drive.

FUNCTION:
The traveling block multiplies the lifting capacity of the draw works through the mechanical advantage of the block-and-tackle system. The hook provides a point of attachment for the swivel (in kelly systems), top drive quill, or elevator links for running tubulars.

SPECIFICATIONS:
- Hook rating: 750 tons (1,500,000 lbs)
- Number of sheaves: 7 (for 14-line strung system)
- Sheave diameter: 60"
- Wire rope size: 1-3/4"
- Spring assembly: Dual heavy-duty compression springs
- Latch type: Gate latch with safety lock

MAIN COMPONENTS:
1. Traveling Block Body: Steel frame housing the sheave assembly.
2. Sheaves: Large diameter wheels with grooved rims for wire rope.
3. Sheave Pin: Central pin on which all sheaves rotate.
4. Hook Body: Large steel hook with safety latch.
5. Hook Spring: Absorbs shock loads during picking up/setting down.
6. Swivel Pin Connection: Pin-type connection between block and hook.
7. Safety Latch: Prevents accidental unhooking.

INSPECTION AND MAINTENANCE:
- Daily: Inspect latch function and safety mechanism, check lubrication, look for cracks
- Weekly: Lubricate all sheave bearings and hook pivot
- Monthly: Measure sheave groove wear, inspect hook for cracks (MPI)
- Annual: Full disassembly inspection, replace worn sheave bushings

SAFETY:
Hook failures can result in catastrophic dropped load incidents. Never exceed rated capacity. Always ensure safety latch is engaged. Inspect for deformation after any shock loading event.
"""),
        ("Iron Roughneck", """IRON ROUGHNECK - EQUIPMENT MANUAL AND OPERATING GUIDE
Model: NOV ST-80 Iron Roughneck
Manufacturer: National Oilwell Varco

OVERVIEW:
The Iron Roughneck is a floor-mounted or derrick-suspended hydraulic tool used to spin, make up, and break out threaded connections on drill pipe, drill collars, and casing tubulars. It replaces manual tong crews, drastically improving rig floor safety and connection speed.

FUNCTION:
The Iron Roughneck performs two distinct mechanical actions during pipe makeup/breakout:
1. Spinning: High-speed rollers rapidly thread the pin into the box joint.
2. Torquing: High-torque hydraulic jaws apply precise make-up torque to API specifications.

SPECIFICATIONS:
- Tubular range: 3-1/2" to 8-1/2" OD
- Maximum make-up torque: 60,000 ft-lbs
- Maximum break-out torque: 80,000 ft-lbs
- Spinner speed: up to 100 RPM
- Vertical travel: 56 inches
- Operating pressure: 3,000 PSI hydraulic

MAIN COMPONENTS:
1. Torque Wrench Assembly: Fixed lower jaw (holds pipe) and rotating upper jaw (applies torque).
2. Spinner Assembly: Hydraulically driven rubber rollers that spin tubulars in/out.
3. Carriage & Arm: Hydraulic positioning arm that extends tool to centerwell and retracts to park.
4. Hydraulic Control Block: Proportional valves regulating clamping pressure and torque motor flow.
5. Control Console: Remote driller's touchscreen or joysticks on rig floor.

MAINTENANCE:
- Shift check: Inspect spinner rollers for wear, verify torque die tooth sharpness
- Daily: Grease all pivot pins and guide tracks, check hydraulic hoses for abrasion
- Weekly: Calibrate torque transducer against master pressure gauge
- Monthly: Inspect torque wrench cylinder seals and jaw alignment bolts
"""),
        ("Shale Shaker", """SHALE SHAKER - EQUIPMENT MANUAL & SOLIDS CONTROL SPECIFICATIONS
Model: M-I SWACO MONGOOSE PRO Dual-Deck Shaker
Manufacturer: Schlumberger (M-I SWACO)

OVERVIEW:
The shale shaker is the primary phase solids control device on a drilling rig. It receives returning drilling mud from the wellbore conductor pipe and separates drill cuttings from the liquid mud using vibrating wire mesh screens.

FUNCTION:
By vibrating screens at high G-forces, liquid mud passes through screen mesh openings while solid rock cuttings are conveyed off the end of the basket into the ditch/cuttings chute. Effective shale shaker operation prevents fine solids build-up in the mud system.

SPECIFICATIONS:
- Basket motion: Linear motion or Balanced Elliptical motion (switchable)
- Motion G-force: 7.5 Gs continuous
- Screen area: 29.4 sq ft (4 screen panels per shaker)
- Processing capacity: up to 1,200 GPM depending on mud viscosity and mesh size
- Screen mesh range: API 40 to API 325

MAIN COMPONENTS:
1. Vibrating Basket: Steel box housing the screen decks and vibrator motors.
2. Motion Generators: Twin counter-rotating electric vibrator motors (1,800 RPM).
3. Screen Clamping System: Pneumatic or wedge clamping mechanisms for rapid screen replacement.
4. Flow Divider / Possum Belly: Receiving tank that distributes mud evenly across shaker width.
5. Angle Adjustment: Hydraulic deck angle adjustment (-1° to +5°) to control fluid pool depth.

MAINTENANCE:
- Every 2 hours: Inspect screens for tears, blinds, or hole formation
- Shift check: Check vibrator motor bearing temperature (max 170°F)
- Weekly: Torque vibrator motor mounting bolts to specified tension (API standards)
- Monthly: Inspect rubber isolation springs for cracking or fatigue
"""),
        ("Degasser & Mud Gas Separator", """MUD GAS SEPARATOR AND CENTRIFUGAL DEGASSER MANUAL
Model: M-I SWACO Poor Boy Separator & CD-1400 Degasser
Manufacturer: Schlumberger

OVERVIEW:
Mud Gas Separators ("Poor Boy" degassers) and vacuum degassers are critical well control devices designed to remove entrained formation gas (methane, H2S) from drilling fluid before the fluid returns to active mud pits.

FUNCTION:
1. Mud Gas Separator (Primary): Handles free gas/mud mixture during a kick. Separates large gas bubbles by gravity/baffling and vents gas safely to the flare stack while returning mud to shakers.
2. Centrifugal/Vacuum Degasser (Secondary): Removes small entrained gas bubbles from mud downstream of shakers using vacuum or centrifugal force.

SPECIFICATIONS:
- Mud Gas Separator Vessel Diameter: 48" OD x 20 ft height
- Gas Vent Line Diameter: 10" to flare boom
- Liquid Seal Height: 10 feet
- Degasser Capacity: 1,400 GPM
- Vacuum Rating: 15" Hg

MAINTENANCE & SAFETY:
- Always verify liquid mud seal in Poor Boy separator before drilling gas-bearing formations.
- Inspect flare line for obstruction, freezing, or liquid accumulation daily.
- Degasser vacuum pump oil change every 250 operational hours.
"""),
        ("Subsea BOP & MUX Control Pod", """SUBSEA BLOWOUT PREVENTER & MUX CONTROL SYSTEM
Model: Cameron 18-3/4" 15,000 PSI Subsea Stack with Mark III MUX Pods
Manufacturer: Cameron / Schlumberger

OVERVIEW:
Subsea BOP stacks are mounted on the ocean floor (mudline) in deepwater drilling. Multiplex (MUX) electro-hydraulic control pods transmit electrical signals via fiber-optic umbilicals from surface to subsea hydraulic solenoids, achieving subsea valve actuation in under 45 seconds.

SPECIFICATIONS:
- Working Pressure: 15,000 PSI wellbore rating
- Stack Configuration: 1 Double Annular (10,000 PSI), 4 Ram Cavities (Pipe, Variable, Shear, Blind Shear)
- Control System: Dual Redundant MUX Pods (Blue Pod & Yellow Pod)
- Umbilical: Armored fiber-optic / electric / hydraulic main umbilical cable
- Acoustic Control: Backup acoustic transducer system for pod actuation
- Emergency Systems: Auto-shear, Deadman system, and EDS (Emergency Disconnect System)

EDS SEQUENCE:
Upon initiation, EDS closes blind shear rams to cut drill pipe and seal wellbore, unlatches Lower Marine Riser Package (LMRP) hydraulic connector, and frees vessel to drift away from wellhead in severe storm or DP failure.
"""),
        ("Standpipe Manifold", """HIGH-PRESSURE STANDPIPE MANIFOLD MANUAL
Specification: 15,000 PSI Dual Standpipe System per API 6A
Manufacturer: Cameron / NOV

OVERVIEW:
The standpipe manifold is located on the rig floor derrick leg. It connects the high-pressure mud pump discharge lines to the rigid vertical standpipes that carry mud up into the derrick to the rotary hose and top drive.

SPECIFICATIONS:
- Working Pressure: 15,000 PSI test / 10,000 PSI continuous
- Main Bore: 4" 15M API Flanged & Hammer Lug Connections
- Valves: 4-1/16" 15M Gate Valves with Stellite Trim
- Standpipes: Dual 5" OD Schedule 160 Seamless Pipes

COMPONENTS & OPERATION:
Includes mud pressure transducers, relief valve dump line, fill-up line connection, and dual isolation gate valves allowing seamless switching between Standpipe 1 and Standpipe 2 without stopping mud pumps.
"""),
        ("Managed Pressure Drilling (MPD)", """MANAGED PRESSURE DRILLING (MPD) & ROTATING CONTROL DEVICE (RCD) MANUAL
Model: Weatherford Model 7875 RCD & Automatic Surface Backpressure System
Manufacturer: Weatherford International

OVERVIEW:
MPD is an adaptive drilling process used to precisely control the annular pressure profile throughout the wellbore. The RCD seals around the rotating drill pipe at surface, converting the open mud system into a closed, pressurized system.

SPECIFICATIONS:
- RCD Dynamic Pressure Rating: 3,000 PSI rotating / 5,000 PSI static
- RCD Pass-through Bore: 7-1/16"
- Automated MPD Choke Response: < 1 second PLC response time
- Flow Metering: High-precision Coriolis mass flow meter on return line

FUNCTION & BENEFIT:
MPD enables drilling narrow pore pressure / fracture gradient windows, preventing lost circulation while instantly detecting micro-kicks via mass flow meter imbalance (gain/loss detection down to 0.5 bbl).
"""),
        ("Heave Compensator", """CROWN MOUNTED HEAVE COMPENSATOR (CMC) MANUAL
Model: NOV 25-ft Stroke Active/Passive Crown Compensator
Manufacturer: National Oilwell Varco

OVERVIEW:
Installed at the top of the derrick on floating drilling vessels (drillships and semi-submersibles), the heave compensator decouples vessel vertical wave motion from the drill string, maintaining constant Weight on Bit (WOB) and preventing bit bounce.

SPECIFICATIONS:
- Stroke Length: 25 feet total travel
- Compensating Capacity: 800,000 lbs continuous
- Maximum Hook Load (Locked): 1,500,000 lbs
- Accumulator Pressure: 3,000 PSI Nitrogen/Hydraulic Air Banks
- Active Heave System: Electric servo-drive fine adjustment (+/- 2 inches accuracy)
"""),
        ("Marine Riser System", """MARINE DRILLING RISER & TELESCOPIC JOINT MANUAL
Specification: 21" OD High-Yield Steel Riser Joints per API 16F
Manufacturer: Cameron / NOV

OVERVIEW:
The marine riser connects the subsea BOP stack on the seabed to the floating drilling vessel. It acts as a conduit for the drill string, returning mud/cuttings, and auxiliary lines (choke, kill, hydraulic power, mud boost).

COMPONENTS:
1. Riser Joint: 21" OD x 0.625" wall thickness steel pipe wrapped in syntactic foam buoyancy modules.
2. Telescopic (Slip) Joint: Dual-packing outer barrel pinned to rig moonpool, inner barrel attached to riser string, accommodating vessel heave (up to 30 ft stroke).
3. Flex Joint: Angular deflection joint (+/- 10° tilt) at top of BOP and bottom of moonpool.
4. Riser Tensioners: Hydro-pneumatic cylinders applying 1.2M - 2.5M lbs constant tension to prevent riser column buckling.
"""),
        ("Rig Power & Diesel Generators", """RIG POWER SYSTEM & SCR/VFD SWITCHGEAR MANUAL
Model: 4x Caterpillar 3516B Diesel Generator Sets & ABB VFD Drives
Manufacturer: Caterpillar / ABB

OVERVIEW:
Offshore drilling rigs generate independent electric power via heavy diesel generator sets. A centralized VFD (Variable Frequency Drive) or SCR (Silicon Controlled Rectifier) switchgear converts AC/DC power to drive mud pumps, top drive, drawworks, and thrusters.

SPECIFICATIONS:
- Main Engines: 4x CAT 3516B V-16 Turbocharged Diesel Engines (2,150 HP each at 1,200 RPM)
- Alternators: 4x KATO 600V 3-Phase 60Hz 1,825 kVA Generators
- Total Installed Power: ~8.6 MW (11,600 HP)
- VFD System: ABB ACS800 liquid-cooled drives supplying 0-600V variable frequency to AC motors.
- Emergency Generator: CAT 3412 emergency genset located above waterline deck.
"""),
        ("Dynamic Positioning System", """DYNAMIC POSITIONING (DP2/DP3) SYSTEM MANUAL
Model: Kongsberg K-Pos DP-22 Dual Redundant DP System
Manufacturer: Kongsberg Maritime

OVERVIEW:
Dynamic Positioning (DP) automatically maintains a floating drilling vessel's position and heading over the subsea wellhead using vessel-mounted computer control and variable-pitch azimuth thrusters, eliminating anchor mooring lines in deepwater.

SPECIFICATIONS:
- DP Class: IMO DP-2 / DP-3 (Redundant computer architecture & segregated engine rooms)
- Position Reference Systems: Dual DGPS (Differential GPS), Hydroacoustic (HiPAP subsea beacons), Taut Wire, and Cyscan laser.
- Environmental Inputs: Anemometers (wind speed/direction), MRU (Motion Reference Units for pitch/roll/heave), Gyrocompasses.
- Propulsion: 6x 3,500 kW 360° steerable underwater azimuth thrusters.
""")
    ]
    
    for name, content in equipment_docs:
        kb = EquipmentKB(equipment_name=name, content=content)
        db.add(kb)
    
    db.commit()
    print(f"Created {len(equipment_docs)} equipment KB entries")

def main():
    print("Creating database tables...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Check if already seeded
        existing = db.query(WorkPack).count()
        if existing > 0:
            print("Database already seeded. Use --force to re-seed.")
            if "--force" not in sys.argv:
                return
            # Clear existing data
            print("Force re-seeding...")
            db.query(ChecklistItem).delete()
            db.query(Checklist).delete()
            db.query(Operation).delete()
            db.query(Procedure).delete()
            db.query(WorkPack).delete()
            db.query(Shift).delete()
            db.query(EquipmentKB).delete()
            db.commit()
        
        print("Seeding work packs...")
        work_packs = seed_work_packs(db)
        print(f"Created {len(work_packs)} work packs")
        
        print("Seeding procedures...")
        procedures = seed_procedures(db, work_packs)
        print(f"Created {len(procedures)} procedures")
        
        print("Seeding operations...")
        seed_operations(db, procedures)
        
        print("Seeding shifts...")
        seed_shifts(db)
        
        print("Seeding checklists...")
        seed_checklists(db, work_packs)
        
        print("Seeding equipment knowledge base...")
        seed_equipment_kb(db)
        
        print("\nDatabase seeding complete!")
        print(f"Summary:")
        print(f"  Work Packs: {db.query(WorkPack).count()}")
        print(f"  Procedures: {db.query(Procedure).count()}")
        print(f"  Operations: {db.query(Operation).count()}")
        print(f"  Shifts: {db.query(Shift).count()}")
        print(f"  Checklists: {db.query(Checklist).count()}")
        print(f"  Checklist Items: {db.query(ChecklistItem).count()}")
        print(f"  Equipment KB: {db.query(EquipmentKB).count()}")
    
    finally:
        db.close()

if __name__ == "__main__":
    main()
