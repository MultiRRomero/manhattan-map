<?php
  $call_args = 123;
?>

<html style="height:100%;">

  <head>
    <title>Google Maps API v3 : Hardcoded Polygon</title>
    <script type="text/javascript" src="http://maps.google.com/maps/api/js?sensor=false">
      </script>
    <script type="text/javascript" src="main.js"></script>
  </head>

  <body onload="initialize(<?php echo $call_args; ?>)" style="height:100%; margin:0; padding:0;">
    <div id="map" style="height:100%; width:100%;"></div>
  </body>

</html>
