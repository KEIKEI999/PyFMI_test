model PID
  Modelica.Blocks.Interfaces.RealInput u annotation(
    Placement(visible = true, transformation(origin = {-37, 4}, extent = {{-11, -11}, {11, 11}}, rotation = 0), iconTransformation(origin = {-37, 4}, extent = {{-11, -11}, {11, 11}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealOutput y annotation(
    Placement(visible = true, transformation(origin = {38, 28}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {38, 28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput target annotation(
    Placement(visible = true, transformation(origin = {-60, 28}, extent = {{-12, -12}, {12, 12}}, rotation = 0), iconTransformation(origin = {-60, 28}, extent = {{-12, -12}, {12, 12}}, rotation = 0)));
  Modelica.Blocks.Continuous.LimPID pid(Ti = 0.03, k = 0.75, kFF = 0.63, limitsAtInit = true, withFeedForward = true, yMax = 100)  annotation(
    Placement(visible = true, transformation(origin = {-6, 28}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput ff annotation(
    Placement(visible = true, transformation(origin = {-36, -14}, extent = {{-12, -12}, {12, 12}}, rotation = 0), iconTransformation(origin = {-36, -14}, extent = {{-12, -12}, {12, 12}}, rotation = 0)));
equation
  connect(target, pid.u_s) annotation(
    Line(points = {{-60, 28}, {-18, 28}}, color = {0, 0, 127}));
  connect(pid.y, y) annotation(
    Line(points = {{6, 28}, {28, 28}, {28, 28}, {38, 28}}, color = {0, 0, 127}));
  connect(u, pid.u_m) annotation(
    Line(points = {{-36, 4}, {-6, 4}, {-6, 16}, {-6, 16}}, color = {0, 0, 127}));
  connect(ff, pid.u_ff) annotation(
    Line(points = {{-36, -14}, {0, -14}, {0, 16}, {0, 16}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "3.2.3")));
end PID;
