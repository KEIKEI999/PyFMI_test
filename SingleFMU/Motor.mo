model Motor
  parameter Modelica.SIunits.Torque TLoad=ViNominal*dcpmData.IaNominal/dcpmData.wNominal "Nominal load torque";
  parameter Modelica.SIunits.AngularVelocity wLoad=dcpmData.wNominal "Nominal load torque";
  parameter Modelica.SIunits.Inertia JLoad=dcpmData.Jr "Load's moment of inertia";
  parameter Modelica.SIunits.Resistance Ra=Modelica.Electrical.Machines.Thermal.convertResistance(
    dcpmData.Ra,
    dcpmData.TaRef,
    dcpmData.alpha20a,
    dcpmData.TaNominal) "Warm armature resistance";
  parameter Modelica.SIunits.Voltage ViNominal=dcpmData.VaNominal - Ra*dcpmData.IaNominal "Nominal induced voltage";
  parameter Modelica.SIunits.Time Ta=dcpmData.La/Ra "Armature time constant";
  parameter Modelica.SIunits.Time Ts=1e-3 "Dead time of inverter";
  parameter Modelica.SIunits.Resistance k=Ra*Ta/(2*Ts) "Current controller proportional gain";
  parameter Modelica.SIunits.Time Ti=Ta "Current controller integral time constant";
  parameter Modelica.SIunits.MagneticFlux kPhi=ViNominal/dcpmData.wNominal "Voltage constant";

  Modelica.Electrical.Analog.Sources.SignalVoltage signalVoltage annotation(
    Placement(visible = true, transformation(extent = {{20, 20}, {0, 40}}, rotation = 0)));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor annotation(
    Placement(visible = true, transformation(origin = {20, 10}, extent = {{10, -10}, {-10, 10}}, rotation = 90)));
  Modelica.Electrical.Machines.BasicMachines.DCMachines.DC_PermanentMagnet dcpm(IaNominal = dcpmData.IaNominal, Jr = dcpmData.Jr, Js = dcpmData.Js, La = dcpmData.La, Ra = dcpmData.Ra, TaNominal = dcpmData.TaNominal, TaOperational = 293.15, TaRef = dcpmData.TaRef, VaNominal = dcpmData.VaNominal, alpha20a = dcpmData.alpha20a, brushParameters = dcpmData.brushParameters, coreParameters = dcpmData.coreParameters, frictionParameters = dcpmData.frictionParameters, ia(fixed = true), phiMechanical(fixed = true), strayLoadParameters = dcpmData.strayLoadParameters, useSupport = false, wMechanical(fixed = true), wNominal = dcpmData.wNominal) annotation(
    Placement(visible = true, transformation(extent = {{0, -30}, {20, -10}}, rotation = 0)));
  Modelica.Mechanics.Rotational.Sensors.SpeedSensor speedSensor annotation(
    Placement(visible = true, transformation(origin = {30, -38}, extent = {{-10, -10}, {10, 10}}, rotation = 270)));
  parameter Modelica.Electrical.Machines.Utilities.ParameterRecords.DcPermanentMagnetData dcpmData annotation(
    Placement(visible = true, transformation(extent = {{0, -60}, {20, -40}}, rotation = 0)));
  Modelica.Mechanics.Rotational.Components.Inertia loadInertia(J = JLoad) annotation(
    Placement(visible = true, transformation(extent = {{40, -30}, {60, -10}}, rotation = 0)));
  Modelica.Electrical.Analog.Basic.Ground ground annotation(
    Placement(visible = true, transformation(origin = {-10, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 270)));
  Modelica.Blocks.Interfaces.RealOutput current annotation(
    Placement(visible = true, transformation(origin = {80, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {80, 10}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput voltage annotation(
    Placement(visible = true, transformation(origin = {-33, 51}, extent = {{-7, -7}, {7, 7}}, rotation = 0), iconTransformation(origin = {-33, 51}, extent = {{-7, -7}, {7, 7}}, rotation = 0)));
  Modelica.Mechanics.Rotational.Sources.TorqueStep loadTorqueStep(offsetTorque = 0, startTime = 1.5, stepTorque = -63.66, useSupport = false) annotation(
    Placement(visible = true, transformation(extent = {{92, -30}, {72, -10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput speed annotation(
    Placement(visible = true, transformation(origin = {58, -64}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {58, -64}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
equation
  connect(dcpm.pin_an, ground.p) annotation(
    Line(points = {{4, -10}, {4, 0}, {0, 0}}, color = {0, 0, 255}));
  connect(signalVoltage.n, ground.p) annotation(
    Line(points = {{0, 30}, {0, 0}}, color = {0, 0, 255}));
  connect(dcpm.flange, loadInertia.flange_a) annotation(
    Line(points = {{20, -20}, {40, -20}}));
  connect(currentSensor.n, dcpm.pin_ap) annotation(
    Line(points = {{20, 0}, {16, 0}, {16, -10}}, color = {0, 0, 255}));
  connect(dcpm.flange, speedSensor.flange) annotation(
    Line(points = {{20, -20}, {30, -20}, {30, -28}}));
  connect(signalVoltage.p, currentSensor.p) annotation(
    Line(points = {{20, 30}, {20, 20}}, color = {0, 0, 255}));
  connect(currentSensor.i, current) annotation(
    Line(points = {{32, 10}, {80, 10}}, color = {0, 0, 127}));
  connect(loadInertia.flange_b, loadTorqueStep.flange) annotation(
    Line(points = {{60, -20}, {72, -20}, {72, -20}, {72, -20}}));
  connect(voltage, signalVoltage.v) annotation(
    Line(points = {{-32, 52}, {10, 52}, {10, 42}, {10, 42}}, color = {0, 0, 127}));
  connect(speedSensor.w, speed) annotation(
    Line(points = {{30, -48}, {30, -64}, {58, -64}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "3.2.3")),
    Diagram(coordinateSystem(initialScale = 0.1)),
    experiment(StopTime = 4));
end Motor;
