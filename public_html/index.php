<?php
$database = new PDO("mysql:host=localhost;dbname=transfer", "root", "");

if(empty($_GET['email']) || empty($_GET['key']))
{
	die("No valid email and key specified. Please check the email you received about the migration of your servers.");
}

$statement = $database->prepare("SELECT * FROM emails WHERE `EmailAddress` = ? AND `Key` = ?");
$statement->bindValue(1, $_GET['email'], PDO::PARAM_STR);
$statement->bindValue(2, $_GET['key'], PDO::PARAM_STR);
$statement->execute();
$results = $statement->fetchAll();

if(count($results) == 0)
{
	die("No valid email and key specified. Please check the email you received about the migration of your servers.");
}

$statement = $database->prepare("SELECT * FROM entries WHERE `EmailAddress` = ? ORDER BY `Finished` DESC");
$statement->bindValue(1, $_GET['email'], PDO::PARAM_STR);
$statement->execute();
$vpses = $statement->fetchAll();

?>

<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<link rel="stylesheet" href="style.css">
		<link href='http://fonts.googleapis.com/css?family=Orienta' rel='stylesheet' type='text/css'>
	</head>
	<body>
		<div class="header">
			<img src="logo.png">
		</div>
		<div class="main">
			<h1>VPS migration status</h1>
			<table>
				<tr>
					<th></th>
					<th>Username</th>
					<th>Status</th>
				</tr>
				<?php
				foreach($vpses as $row)
				{
					?>
					<tr>
						<?php if($row['Finished'] == "0") 
						{ 
							?>
							<td class="status"><span class="done">A</span> ⇒ B</td>
							<?php
						}
						elseif($row['Finished'] == "1")
						{
							?>
							<td class="status">A <span class="done"><img src="processing.gif"></span> B</td>
							<?php
						}
						elseif($row['Finished'] == "2")
						{
							?>
							<td class="status">A ⇒ <span class="done">B</span></td>
							<?php
						}
						elseif($row['Finished'] == "3")
						{
							?>
							<td class="status">A ⇒ B</td>
							<?php
						}
						?>
						
						<td><?php echo(htmlspecialchars($row["Username"])); ?></td>
						
						<?php if($row['Finished'] == "0") 
						{
							$my_pos = $row['Position'];
							
							$statement = $database->prepare("SELECT * FROM servers WHERE `Host` = ?");
							$statement->bindValue(1, $row['TargetNode'], PDO::PARAM_STR);
							$statement->execute();
							$node = $statement->fetch();
							$current_pos = $node['Current'];
							
							$real_pos = $my_pos - $current_pos;
							?>
							<td class="queue">Queued in position <?php echo($real_pos); ?>.</td>
							<?php
						}
						elseif($row['Finished'] == "1")
						{
							?>
							<td class="queue">Transferring...</td>
							<?php
						}
						elseif($row['Finished'] == "2")
						{
							?>
							<td class="queue">Done!</td>
							<?php
						}
						elseif($row['Finished'] == "3")
						{
							?>
							<td class="queue">Failed</td>
							<?php
						}
						?>
					</tr>
					<?php
				}	
				?>
			</table>
		</div>
	</body>
</html>
