<?php

#   Copyright (C) 2006-2009 Tobias Leupold <tobias.leupold@web.de>
#
#   This file is part of the b8 package
#
#   This program is free software; you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation in version 2.1 of the License.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#   or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#   License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


### This is an example script demonstrating how b8 can be used. ###


# If you use MySQL as b8's storage backend, you can either set your access
# data in config_storage or fill it in here and uncomment the code (example way to do it).

# If set here, $mysqlRes will be passed to b8 below.

/**/
/**
$host = "localhost";//127.0.0.1";
$user = "root";
$pass = "842519";
$db   = "b8";

$mysqlRes = mysql_connect($host, $user, $pass);

if(!$mysqlRes)
	die("<b>Example:</b> Could not connect to MySQL (" . mysql_error() . ")<br />\n");

mysql_select_db($db) or die("<b>Example:</b> Could not select database \"$db\". Truncating.<br />\n");
 */
/**/

# Output a nicely colored rating

function formatRating($rating)
{

	if($rating === FALSE)
		return "<span style=\"color:red\">could not calculate spaminess</span>";

	$red   = floor(255 * $rating);
	$green = floor(255 * (1 - $rating));

	return "<span style=\"color:rgb($red, $green, 0);\"><b>" . sprintf("%5f", $rating) . "</b></span>";

}
?><<?php
echo "?";?>xml version="1.0" encoding="utf-8"<?php echo "?";?>>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
   "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>

<title>example b8 interface</title>

<meta http-equiv="content-type" content="text/html; charset=utf-8" />

<meta name="dc.creator" content="Tobias Leupold" />
<meta name="dc.rights" content="Copyright (c) by Tobias Leupold" />

</head>

<body>

<div>

<h1>example b8 interface</h1>

<?php
$postedText = "";

if(isset($_POST['action']) and $_POST['text'] ==  "")
	echo "<p style=\"color:red;\"><b>Please type in a text!</b></p>\n\n";

elseif(isset($_POST['action']) and $_POST['text'] !=  "") {

	# Include the b8 code
	require dirname(__FILE__) . "/../b8.php";

	# Create a new b8 instance

	# Check if a MySQL-link resource was set above

	if(isset($mysqlRes)) {
		# It was set, so pass it to b8
		$b8 = new b8($mysqlRes);
	}
	else
		$b8 = new b8;

	# Check if everything worked smoothly
	if(!$b8->constructed) {
		echo "<b>example:</b> Could not initialize b8. Truncating.";
		exit;
	}

	$text = stripslashes($_POST['text']);

	//$postedText = htmlentities($text);
	$postedText = $text;

	switch($_POST['action']) {

		case "Classify":
			echo "<p><b>Spaminess: " . formatRating($b8->classify($text)) . "</b></p>\n";
			break;

		case "Save as Spam":

			$ratingBefore = $b8->classify($text);
			$b8->learn($text, "spam");
			$ratingAfter = $b8->classify($text);

			echo "<p>Saved the text as Spam</p>\n\n";

			echo "<div><table>\n";
			echo "<tr><td>Classification before learning:</td><td>" . formatRating($ratingBefore) . "</td></tr>\n";
			echo "<tr><td>Classification after learning:</td><td>"  . formatRating($ratingAfter)  . "</td></tr>\n";
			echo "</table></div>\n\n";

			break;

		case "Save as Ham":

			$ratingBefore = $b8->classify($text);
			$b8->learn($text, "ham");
			$ratingAfter = $b8->classify($text);

			echo "<p>Saved the text as Ham</p>\n\n";

			echo "<div><table>\n";
			echo "<tr><td>Classification before learning:</td><td>" . formatRating($ratingBefore) . "</td></tr>\n";
			echo "<tr><td>Classification after learning:</td><td>"  . formatRating($ratingAfter)  . "</td></tr>\n";
			echo "</table></div>\n\n";

			break;

		case "Delete from Spam":
			$b8->unlearn($text, "spam");
			echo "<p style=\"color:green\">Deleted the text from Spam</p>\n\n";
			break;

		case "Delete from Ham":
			$b8->unlearn($text, "ham");
			echo "<p style=\"color:green\">Deleted the text from Ham</p>\n\n";
			break;

	}

}

echo <<<END
<div>
<form action="{$_SERVER['PHP_SELF']}" method="post">
<div>
<textarea name="text" cols="50" rows="16">$postedText</textarea>
</div>
<table>
<tr>
<td><input type="submit" name="action" value="Classify" /></td>
</tr>
<tr>
<td><input type="submit" name="action" value="Save as Spam" /></td>
<td><input type="submit" name="action" value="Save as Ham" /></td>
</tr>
<tr>
<td><input type="submit" name="action" value="Delete from Spam" /></td>
<td><input type="submit" name="action" value="Delete from Ham" /></td>
</tr>
</table>
</form>
</div>

</div>

</body>

</html>
END;

?>
