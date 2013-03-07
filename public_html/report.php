<?php
$db = "schedule.db";

$database = new PDO("mysql:host=localhost;dbname=transfer", "root", "");

$database->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

if($_GET['key'] == "keygoeshere")
{
	if($_GET['action'] == "done")
	{
		$statement = $database->prepare("UPDATE entries SET `Finished` = 2 WHERE `Finished` = 1 AND `TargetNode` = ?");
		$statement->bindValue(1, $_GET['server'], PDO::PARAM_STR);
		$statement->execute();
		$statement = $database->prepare("UPDATE servers SET `Busy` = 0 WHERE `Host` = ? AND `Busy` != 4");
		$statement->bindValue(1, $_GET['server'], PDO::PARAM_STR);
		$statement->execute();
	}
	elseif($_GET['action'] == "failed")
	{
		$statement = $database->prepare("UPDATE entries SET `Finished` = 3 WHERE `Finished` = 1 AND `TargetNode` = ?");
		$statement->bindValue(1, $_GET['server'], PDO::PARAM_STR);
		$statement->execute();
		$statement = $database->prepare("UPDATE servers SET `Busy` = 2 WHERE `Host` = ? AND `Busy` != 4");
		$statement->bindValue(1, $_GET['server'], PDO::PARAM_STR);
		$statement->execute();
	}
}
