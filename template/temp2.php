
<?php
$servername = "localhost";
$username = "PedroGomes";
$password = "2020guarda#";
$dbname = "camlion";

$conn = new mysqli($servername, $username, $password, $dbname);


if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 



$sql = "SELECT * FROM monitoring";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {

	$pm2=$row["pm2"];
	$fisicdist=$row["fisicdist"];
	$zonedanger=$row["zonedanger"];
	$risk=$row["risk"];
	$data=$row["data"];

        echo $row["pm2"]. ";" . $row["fisicdist"].";" . $row["zonedanger"].";" . $row["risk"].";" . $row["data"].";" . $row["georisk"];
    }
} else {
    echo "0 results";
}
$conn->close();
?>
