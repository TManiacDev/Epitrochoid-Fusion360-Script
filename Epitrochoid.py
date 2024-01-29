#Author-TManiac Engineering
#Description-Creates a Epitrochoid spline sketch.

# TMANIAC PROVIDES THIS PROGRAM "AS IS" AND WITH ALL FAULTS. TMANIAC SPECIFICALLY  
# DISCLAIMS ANY IMPLIED WARRANTY OF MERCHANTABILITY OR FITNESS FOR A PARTICULAR USE.  
# TMANIAC DOES NOT WARRANT THAT THE OPERATION OF THE PROGRAM WILL BE  
# UNINTERRUPTED OR ERROR FREE. 

import adsk.core, adsk.fusion, traceback

import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_standard = adsk.core.DropDownCommandInput.cast(None)
_innerCircleDia = adsk.core.FloatSliderCommandInput.cast(None)
_outerCircleDia = adsk.core.FloatSliderCommandInput.cast(None)
_distanceValue = adsk.core.FloatSliderCommandInput.cast(None)
_stepsPerCycle = adsk.core.IntegerSpinnerCommandInput.cast(None)
_cycleCount = adsk.core.IntegerSpinnerCommandInput.cast(None)

_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

radius_big = 3
radius_small = 1
distance = 0.5
count_points = 10
cycle_count = 10

def drawEpitrochoid(design: adsk.fusion.Design, 
                    radius_big:float, 
                    radius_small: float, 
                    distance: float, 
                    count_points: int, 
                    cycle_count: int)  -> adsk.fusion.Sketch:
    try:
        global _app, _ui

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create a new sketch on the xy plane.
        sketch = rootComp.sketches.add(rootComp.xYConstructionPlane)

        # Create an object collection for the points.
        points = adsk.core.ObjectCollection.create()
        arcStep = 2*math.pi / count_points

        i = 0
        while i < ( ( count_points * cycle_count ) +1):
            x = (radius_big + radius_small) * math.cos(arcStep * i) - distance * math.cos( ((radius_big+radius_small)/radius_small ) * (arcStep * i))
            y = (radius_big + radius_small) * math.sin(arcStep * i) - distance * math.sin( ((radius_big+radius_small)/radius_small ) * (arcStep * i))
            points.add(adsk.core.Point3D.create(x, y, 0))
            i += 1 
            

        # Create the spline.
        spline = sketch.sketchCurves.sketchFittedSplines.add(points)
        return sketch
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
    try: 
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        cmdDef = _ui.commandDefinitions.itemById('tmEpitrochoidPythonScript')
        if not cmdDef:
            # Create a command definition.
            cmdDef = _ui.commandDefinitions.addButtonDefinition('tmEpitrochoidPythonScript', 'Epitrochoid', 'Creates a Epitrochoid') 
        
        # Connect to the command created event.
        onCommandCreated = EpitrochoidCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Execute the command.
        cmdDef.execute()

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
# Verfies that a value command input has a valid expression and returns the 
# value if it does.  Otherwise it returns False.  This works around a 
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make 
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager
        
        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class EpitrochoidCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            
            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()
                
            defaultUnits = des.unitsManager.defaultLengthUnits
                
            # Determine whether to use inches or millimeters as the intial default.
            global _units
            if defaultUnits == 'in' or defaultUnits == 'ft':
                _units = 'in'
            else:
                _units = 'mm'
                        
            # Define the default values and get the previous values from the attributes.
            if _units == 'in':
                standard = 'English'
            else:
                standard = 'Metric'
            standardAttrib = des.attributes.itemByName('Epitrochoid', 'standard')
            if standardAttrib:
                standard = standardAttrib.value
                
            if standard == 'English':
                _units = 'in'
            else:
                _units = 'mm'            
            
            innerCircleDia = '3'
            innerCircleDiaAttrib = des.attributes.itemByName('Epitrochoid', 'innerCircleDia')
            if innerCircleDiaAttrib:
                innerCircleDia = innerCircleDiaAttrib.value

            outerCircleDia = '1'
            outerCircleDiaAttrib = des.attributes.itemByName('Epitrochoid', 'outerCircleDia')
            if outerCircleDiaAttrib:
                outerCircleDia = outerCircleDiaAttrib.value

            distanceValue = '0.7'
            distanceValueAttrib = des.attributes.itemByName('Epitrochoid', 'distanceValue')
            if distanceValueAttrib:
                distanceValue = distanceValueAttrib.value

            stepsPerCycle = '20'
            stepsPerCycleAttrib = des.attributes.itemByName('Epitrochoid', 'stepsPerCycle')
            if stepsPerCycleAttrib:
                stepsPerCycle = stepsPerCycleAttrib.value

            cycleCount = '1'
            cycleCountAttrib = des.attributes.itemByName('Epitrochoid', 'cycleCount')
            if cycleCountAttrib:
                cycleCount = cycleCountAttrib.value
            
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs
            
            global _standard, _innerCircleDia, _outerCircleDia, _distanceValue, _stepsPerCycle, _cycleCount, _errMessage

            # Define the command dialog.
            _standard = inputs.addDropDownCommandInput('standard', 'Standard', adsk.core.DropDownStyles.TextListDropDownStyle)
            if standard == "English":
                _standard.listItems.add('English', True)
                _standard.listItems.add('Metric', False)
                #_imgInputMetric.isVisible = False
            else:
                _standard.listItems.add('English', False)
                _standard.listItems.add('Metric', True)
                #_imgInputEnglish.isVisible = False       
            _innerCircleDia = inputs.addFloatSliderCommandInput('innerCircleDia', 'Inner Circle Radius', _units, 0.0, 100, False)
            _innerCircleDia.valueOne = float(innerCircleDia)
            _outerCircleDia = inputs.addFloatSliderCommandInput('outerCircleDia', 'Outer Circle Radius', _units, 0.0, 100, False)
            _outerCircleDia.valueOne = float(outerCircleDia)
            _distanceValue = inputs.addFloatSliderCommandInput('distanceValue', 'Offset Distance', _units, 0.0, 100, False)
            _distanceValue.valueOne = float(distanceValue)

            _stepsPerCycle = inputs.addIntegerSpinnerCommandInput('stepsPerCycle', 'Steps per Cycle', 1, 100,  1, int(stepsPerCycle) )

            _cycleCount = inputs.addIntegerSpinnerCommandInput('cycleCount', 'Cycles', 1, 100,  1, int(cycleCount))

            _errMessage = inputs.addTextBoxCommandInput('errMessage', '', '', 2, True)
            _errMessage.isFullWidth = True

            # Connect to the command related events.
            onDestroy = EpitrochoidCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            onExecute = EpitrochoidCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)  
            
            onPreview = EpitrochoidCommandPreviewHandler()
            cmd.executePreview.add(onPreview)
            _handlers.append(onPreview)   

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
        
class EpitrochoidCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler for the inputChanged event.
class EpitrochoidCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            des = adsk.fusion.Design.cast(_app.activeProduct)

            innerCircleDia = _innerCircleDia.valueOne
            outerCircleDia = _outerCircleDia.valueOne
            distanceValue = _distanceValue.valueOne
            stepsPerCycle = int(_stepsPerCycle.value)
            cycleCount = int(_cycleCount.value)


            sketch = drawEpitrochoid(des, innerCircleDia, outerCircleDia, distanceValue, stepsPerCycle, cycleCount)
            
            # Save the current values as attributes.
            attribs = sketch.attributes
            attribs.add('Epitrochoid', 'standard', _standard.selectedItem.name)
            attribs.add('Epitrochoid', 'innerCircleDia', str(_innerCircleDia.valueOne))
            attribs.add('Epitrochoid', 'outerCircleDia', str(_outerCircleDia.valueOne))
            attribs.add('Epitrochoid', 'distanceValue', str(_distanceValue.valueOne))
            attribs.add('Epitrochoid', 'stepsPerCycle', str(_stepsPerCycle.value))
            attribs.add('Epitrochoid', 'cycleCount', str(_cycleCount.value))
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
# Event handler for the inputChanged event.def command_preview(args: adsk.core.CommandEventArgs): 
class EpitrochoidCommandPreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:

            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Save the current values as attributes.
            des = adsk.fusion.Design.cast(_app.activeProduct)

            innerCircleDia = _innerCircleDia.valueOne
            outerCircleDia = _outerCircleDia.valueOne
            distanceValue = _distanceValue.valueOne
            stepsPerCycle = int(_stepsPerCycle.value)
            cycleCount = int(_cycleCount.value)
            drawEpitrochoid(des, innerCircleDia, outerCircleDia, distanceValue, stepsPerCycle, cycleCount)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))