import adsk.core, adsk.fusion, adsk.cam, traceback
import math

def create_cycloidal_disk(params):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        # Extract parameters
        num_outer_pins = params['num_outer_pins']
        diameter_outer_pins = params['diameter_outer_pins'] / 10.0  # Convert from mm to cm
        diameter_outer_circle = params['diameter_outer_circle'] / 10.0  # Convert from mm to cm

        # Get the design from the active product
        design = app.activeProduct
        if not isinstance(design, adsk.fusion.Design):
            ui.messageBox('No active Fusion design', 'Error')
            return

        # Calculate parameters for the cycloidal disk
        outer_circle_radius = diameter_outer_circle / 2
        pin_radius = diameter_outer_pins / 2
        rolling_circle_radius = outer_circle_radius / num_outer_pins

        # Create user parameters for the offset distance, pin radius, and outer circle radius
        offset_param = design.userParameters.itemByName('CycloidalOffset')
        if offset_param is None:
            design.userParameters.add('CycloidalOffset', adsk.core.ValueInput.createByReal(rolling_circle_radius), 'mm', 'Offset distance for the cycloidal disk')
        else:
            offset_param.value = rolling_circle_radius
        
        pin_radius_param = design.userParameters.itemByName('PinRadius')
        if pin_radius_param is None:
            design.userParameters.add('PinRadius', adsk.core.ValueInput.createByReal(pin_radius), 'mm', 'Radius of the pins')
        else:
            pin_radius_param.value = pin_radius
        
        outer_circle_radius_param = design.userParameters.itemByName('OuterCircleRadius')
        if outer_circle_radius_param is None:
            design.userParameters.add('OuterCircleRadius', adsk.core.ValueInput.createByReal(outer_circle_radius), 'mm', 'Radius of the outer circle')
        else:
            outer_circle_radius_param.value = outer_circle_radius

        # Create a new sketch for the outer pins and housing
        root_comp = design.rootComponent
        sketches = root_comp.sketches
        xy_plane = root_comp.xYConstructionPlane
        housing_sketch = sketches.add(xy_plane)

        # Draw the outer pins circle
        center_point = adsk.core.Point3D.create(0, 0, 0)
        housing_sketch.sketchCurves.sketchCircles.addByCenterRadius(center_point, outer_circle_radius)

        # Draw all the outer pins
        for i in range(num_outer_pins):
            angle = (2 * math.pi / num_outer_pins) * i
            pin_center_x = outer_circle_radius * math.cos(angle)
            pin_center_y = outer_circle_radius * math.sin(angle)
            pin_center = adsk.core.Point3D.create(pin_center_x, pin_center_y, 0)
            housing_sketch.sketchCurves.sketchCircles.addByCenterRadius(pin_center, pin_radius)

        # Draw the offset line representing the cycloidal disk offset
        offset_distance = rolling_circle_radius  # Offset is equal to the rolling circle radius
        offset_point = adsk.core.Point3D.create(offset_distance, 0, 0)
        housing_sketch.sketchCurves.sketchLines.addByTwoPoints(center_point, offset_point)

        # Create a new sketch for the epitrochoid path
        num_points = 360  # Number of points to approximate the path
        cycloidal_sketch = sketches.add(xy_plane)

        # Calculate and draw the epitrochoid path
        path_points = adsk.core.ObjectCollection.create()
        for i in range(num_points):
            angle = math.radians(i)
            x = (outer_circle_radius - rolling_circle_radius) * math.cos(angle) + rolling_circle_radius * math.cos((num_outer_pins - 1) * angle)
            y = (outer_circle_radius - rolling_circle_radius) * math.sin(angle) + rolling_circle_radius * math.sin((num_outer_pins - 1) * angle)
            path_points.add(adsk.core.Point3D.create(x, y, 0))
        path_curve = cycloidal_sketch.sketchCurves.sketchFittedSplines.add(path_points)
        path_curve.isClosed = True  # Ensure the spline is closed

        # Show the rolling circle radius in a message box
        ui.messageBox(f'Cycloidal disk offset distance: {rolling_circle_radius * 10:.2f} mm')  # Convert back to mm for display

    except Exception as e:
        if ui:
            ui.messageBox('Failed: {}'.format(traceback.format_exc()))

# Example usage
def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        # Create input box to get parameters from user
        num_outer_pins_input = ui.inputBox('Enter the number of outer pins:', 'Cycloidal Disk Parameters', '6')[0]
        diameter_outer_pins_input = ui.inputBox('Enter the diameter of outer pins (mm):', 'Cycloidal Disk Parameters', '3.0')[0]
        diameter_outer_circle_input = ui.inputBox('Enter the diameter of the outer circle (mm):', 'Cycloidal Disk Parameters', '25.0')[0]
        
        # Convert inputs
        params = {
            'num_outer_pins': int(num_outer_pins_input),
            'diameter_outer_pins': float(diameter_outer_pins_input),
            'diameter_outer_circle': float(diameter_outer_circle_input)
        }
        
        create_cycloidal_disk(params)
    except Exception as e:
        if ui:
            ui.messageBox('Failed to get user inputs: {}'.format(traceback.format_exc()))
