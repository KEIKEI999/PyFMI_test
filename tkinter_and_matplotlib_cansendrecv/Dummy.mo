model Dummy
  Modelica.Blocks.Interfaces.RealOutput y annotation(
    Placement(visible = true, transformation(origin = {-2, 38}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {-2, 38}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Sources.Ramp ramp(duration = 0.8, height = 100, startTime = 0.2) annotation(
    Placement(visible = true, transformation(extent = {{-46, 28}, {-26, 48}}, rotation = 0)));
equation
  connect(ramp.y, y) annotation(
    Line(points = {{-24, 38}, {-12, 38}, {-12, 40}, {-2, 40}, {-2, 38}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "3.2.3")));
end Dummy;
