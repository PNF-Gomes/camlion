


<?php
$servername = "localhost";
$username = "PedroGomes";
$password = "2020guarda#";
$dbname = "camlion";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 

$sql = "SELECT * FROM heat";

$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
        echo $row["x"]. ";" . $row["y"].";" . $row["date"].">";
    }
} else {
    echo "0 results";
}
$conn->close();
?>
