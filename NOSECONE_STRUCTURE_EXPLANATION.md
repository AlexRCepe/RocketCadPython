# Understanding NoseCone Shape Functions (Lines 2610-2614)

## Overview
The lines 2610-2614 in `rocket.py` define **4 different nose cone shapes** using mathematical functions. Each defines **how the radius changes along the length** of the cone.

## The Structure

Each shape is defined as:
```python
NoseCone.Shape.SHAPE_NAME = NoseCone.Shape("NAME", parameter_range, radius_function)
```

Where:
- **Name**: String identifier
- **parameter_range**: `None` if no parameter needed, or `(min, max)` tuple for shape-specific parameters
- **radius_function**: Lambda that calculates radius at any point

## How It Works

### The Radius Function Signature
```python
lambda x, R, L, k: <formula>
```

**Parameters:**
- `x` = Position along the cone (0 at tip, L at base)
- `R` = Maximum radius (half the diameter, at the base)
- `L` = Total length of the cone
- `k` = Shape parameter (e.g., determines how "pointy" or "round" the cone is)

### How It's Used
In the `NoseCone` class, `get_radius(x)` method calls:
```python
return self.shape.radius_function(x, self.right_diameter/2, self.length, self.shape_parameter)
```

This gives you the radius at any position `x` along the nosecone.

---

## The 4 Shapes Explained

### 1. **CONICAL** (Line 2610)
```python
lambda x, R, L, k: x*R/L
```
- **Formula**: Linear relationship
- **Physics**: Radius increases linearly from tip (0) to base (R)
- **At x=0**: radius = 0 (sharp tip)
- **At x=L**: radius = R (full diameter)
- **Parameter**: None needed

**Visual:**
```
    /|
   / |
  /  | R
 /   |
/____|
  L
```

---

### 2. **OGIVE** (Line 2612)
```python
lambda x, R, L, k: (((R**2 + L**2)/2.0/R)**2 - (L - x)**2)**(0.5) + R - ((R**2 + L**2)/2.0/R)
```
- **Formula**: Circular arc tangent to body
- **Physics**: Most realistic for aerodynamics
- **Shape**: Curved, starts sharp but curves smoothly
- **Parameter**: None needed
- **Note**: This is called "Tangent Ogive" - the curve tangentially connects to the body tube

**Visual:**
```
    *
   * *
  *   *
 *     *
*       *
```

---

### 3. **ELLIPTICAL** (Line 2614)
```python
lambda x, R, L, k: R*(2*(x/L) - (x/L)**2)**(0.5)
```
- **Formula**: Elliptical arc
- **Physics**: Smoother than conical but less aerodynamic than ogive
- **Shape**: Parabolic curve
- **Parameter**: None needed

**Visual:**
```
   )
  ( )
 (   )
(     )
```

---

### 4. **POWER_LAW** (Line 2616 - bonus)
```python
lambda x, R, L, k: R*(x/L)**k
```
- **Formula**: Power function, highly parameterized
- **Parameter range**: `(0, 1)` - shape parameter determines curve
- **Physics**: 
  - k=0.5 → elliptical-like
  - k→0 → more conical
  - k→1 → parabolic
- **Flexible**: Adjust `k` to get different cone shapes

---

## How to Use in `primitives.py`

### Step 1: Create a Function Generator
```python
def create_conical_nosecone(length, diameter, thickness):
    """Create a conical nosecone."""
    R = diameter / 2  # Radius
    L = length
    
    # Generate points along the cone
    points = []
    num_steps = 20
    
    for i in range(num_steps + 1):
        x = i * L / num_steps  # Position along length
        radius = (x * R / L)   # CONICAL formula
        points.append((x, radius))
    
    return points
```

### Step 2: Generic Function Builder
```python
def create_nosecone_profile(length, diameter, shape_name, shape_parameter=0, num_steps=20):
    """
    Generate a nosecone profile points.
    
    Args:
        length: Length of nosecone
        diameter: Base diameter
        shape_name: 'CONICAL', 'OGIVE', 'ELLIPTICAL', 'POWER_LAW'
        shape_parameter: For shapes that need it (POWER_LAW, etc)
        num_steps: Number of profile points
    
    Returns:
        List of (x_position, radius) tuples
    """
    import math
    
    R = diameter / 2
    L = length
    k = shape_parameter
    
    # Define shape formulas
    shapes = {
        'CONICAL': lambda x: x * R / L,
        'OGIVE': lambda x: (((R**2 + L**2)/2.0/R)**2 - (L - x)**2)**(0.5) + R - ((R**2 + L**2)/2.0/R),
        'ELLIPTICAL': lambda x: R * (2*(x/L) - (x/L)**2)**(0.5),
        'POWER_LAW': lambda x: R * (x/L)**k,
    }
    
    if shape_name not in shapes:
        raise ValueError(f"Unknown shape: {shape_name}")
    
    radius_fn = shapes[shape_name]
    points = []
    
    for i in range(num_steps + 1):
        x = i * L / num_steps
        radius = radius_fn(x)
        points.append((x, radius))
    
    return points
```

### Step 3: Create 3D Geometry (with CadQuery)
```python
def create_nosecone_3d(length, diameter, thickness, shape_name, shape_parameter=0):
    """
    Create a 3D nosecone using CadQuery from profile points.
    """
    import cadquery as cq
    import math
    
    profile = create_nosecone_profile(length, diameter, shape_name, shape_parameter, num_steps=30)
    
    # Create a revolution of the profile around the Z-axis
    points = [(x, r) for x, r in profile]
    
    # Build spline through profile
    wire = cq.Workplane().polyline(points).val()
    
    # Revolve around Y-axis to create 3D shape
    nosecone = cq.Workplane("XY").revolve(360, axisEnd=(0, 0, length))
    
    return nosecone
```

---

## Key Insights

1. **All formulas are normalized**: `x` ranges from 0 to L, so divide by L first
2. **Radius is always 0 at tip**: When x=0, all formulas should give r=0
3. **Radius is R at base**: When x=L, all formulas should give r=R
4. **Parameterized flexibility**: Some shapes use `k` to allow variations
5. **Generate profile first**: Get (x, radius) points, then revolve to create 3D

---

## Quick Reference Table

| Shape | Uses k? | Formula Type | Aerodynamics |
|-------|---------|--------------|--------------|
| CONICAL | No | Linear | Poor |
| OGIVE | No | Circular arc | Excellent |
| ELLIPTICAL | No | Elliptical | Good |
| POWER_LAW | Yes | Power function | Variable |
