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

$TITLE = "b8 interface work database editor";
require "header.php";

echo "<h1>Work database editor</h1>\n\n";

if(!isset($_POST['action'])) {

echo "<form action=\"{$_SERVER['PHP_SELF']}\" method=\"POST\">\n";

?>

<h2>Direct SQL querying</h2>

<p>
Enter the SQL query to perform:<br />
<input type="text" size="80" name="sqlquery" />
</p>

<p>
<input type="submit" name="action" value="Query the database" />
</p>

<h2>Query assembler</h2>

<table>

<tr>

<td><b>Token name</b></td>

<td>
<table>
<tr>
<td>
<select name="like_type">
<option value="match">Does</option>
<option value="notmatch">Does not</option>
</select>
</td>
<td>contain string</td>
<td><input type="text" name="like" /> (SQL LIKE)</td>
</tr>
<tr>
<td>
<select name="rlike_type">
<option value="match">Does</option>
<option value="notmatch">Does not</option>
</select>
</td>
<td>match regular expression</td>
<td><input type="rlike" name="rlike" /> (SQL RLIKE, e.&thinsp;g. "[0-9]+\\\.[0-9]+\\\.[0-9]+\\\.[0-9+]" for IP addresses)</td>
</tr>
</table>
</td>

</tr>

<tr>

<td><b>Token age</b></td>

<td>
<table>
<tr>
<td rowspan="2">Was not seen</td>
<td>
<select name="type_date_old">
<option value="days" selected="selected">for minimal number of days:</option>
<option value="date">after date (YY-MM-DD):</option>
</select>
</td>
<td>
<input type="text" size="8" name="date_old" />
</td>
</tr>
<tr>
<td>
<select name="type_date_new">
<option value="days" selected="selected">for maximal number of days:</option>
<option value="date">before date (YY-MM-DD):</option>
</select>
</td>
<td>
<input type="text" size="8" name="date_new" />
</td>
</tr>
</table>
</td>

</tr>

<tr>

<td><b>Token occurance</b></td>

<td>
<table>
<tr>
<td>Occured in <i>ham</i> at least</td>
<td><input type="text" size="5" name="ham_min" /></td>
<td>times, at most</td>
<td><input type="text" size="5" name="ham_max" /></td>
<td>times</td>
<tr>
<tr>
<td>Occured in <i>spam</i> at least</td>
<td><input type="text" size="5" name="spam_min" /></td>
<td>times, at most</td>
<td><input type="text" size="5" name="spam_max" /></td>
<td>times</td>
</tr>
</table>
</td>

</tr>

<tr>

<td><b>Token rating</b></td>

<td>
Is rated with at least
<input type="text" size="8" name="rating_min" />,
at most <input type="text" size="8" name="rating_max" />
</td>

</tr>

<tr>

<td><b>Result ordering</b></td>

<td>
<table>
<tr>
<td>Order result</td>
<td>
<select name="desc">
<option value="">ascending</option>
<option value=" DESC">descending</option>
</select>
</td>
<td>by</td>
<td>
<select name="orderby">
<option value="token">token name</option>
<option value="ham">occurance in ham</option>
<option value="spam">occurance in spam</option>
<option value="lastseen">the last seen date</option>
<option value="rating">rating</option>
</select>
</td>
</tr>
</table>
</td>

</tr>

</table>

<p>
<input type="submit" name="action" value="Select tokens" />
<input type="submit" name="action" value="Delete tokens" />
</p>

</form>

<?php

}

else {

	# Set up the interface
	require "interface_functions.php";
	$interface = new interfaceFunctions;

	# Check if everything worked smoothly
	if(!$interface->constructed) {
		echo "<b>workdb:</b> Failed to initialize the interface class. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Check what to do

	if($_POST['action'] == "Query the database") {
		# An SQL query was requested, so we don't need to assemble one
		$query = stripslashes($_POST['sqlquery']);
	}

	else {

		# We have to build the query from the user's choices

		# Use "WHERE" for the first condition, "AND" for the following ones
		$firstCond = TRUE;

		function cond()
		{

			global $firstCond;

			if($firstCond) {
				$firstCond = FALSE;
				return "WHERE ";
			}
			else {
				return "AND ";
			}

		}

		# Start with no query

		$query = "";

		# Select or delete?

		if($_POST['action'] == "Select tokens")
			$query .= "SELECT * FROM ";
		else
			$query .= "DELETE FROM ";

		$query .= $interface->workStorage->config['tableName'] . "\n";

		# Was LIKE used?

		if($_POST['like'] != "") {

			$query .= cond() . "token ";

			if($_POST['like_type'] == "match")
				$query .= "LIKE ";
			else
				$query .= "NOT LIKE ";

			$query .= "'" . stripslashes($_POST['like']) . "'\n";

		}

		# Was RLIKE used?

		if($_POST['rlike'] != "") {

			$query .= cond() . "token ";

			if($_POST['rlike_type'] == "match")
				$query .= "RLIKE ";
			else
				$query .= "NOT RLIKE ";

			$query .= "'" . stripslashes($_POST['rlike']) . "'\n";

		}

		# Was an age condition given?

		if($_POST['date_old'] != "") {

			$query .= cond() . "lastseen < ";

			if($_POST['type_date_old'] == "days")
				$query .= "DATE_SUB(CURDATE(), INTERVAL {$_POST['date_old']} DAY)\n";
			else
				$query .= "'{$_POST['date_old']}'\n";

		}

		if($_POST['date_new'] != "") {

			$query .= cond() . "lastseen > ";

			if($_POST['type_date_new'] == "days")
				$query .= "DATE_ADD(CURDATE(), INTERVAL {$_POST['date_new']} DAY)\n";
			else
				$query .= "'{$_POST['date_new']}'\n";

		}

		# Was ham occurance used?

		$hamMinEqualMax = FALSE;

		if($_POST['ham_min'] != "") {

			$query .= cond() . "count_ham ";

			if($_POST['ham_min'] == $_POST['ham_max']) {
				$query .= "= {$_POST['ham_min']}\n";
				$hamMinEqualMax = TRUE;
			}
			else
				$query .= ">= {$_POST['ham_min']}\n";

		}

		if($_POST['ham_max'] != "" and !$hamMinEqualMax) {
			$query .= cond() . "count_ham <= {$_POST['ham_max']}\n";
		}

		$spamMinEqualMax = FALSE;

		# Was spam occurance used?

		if($_POST['spam_min'] != "") {

			$query .= cond() . "count_spam ";

			if($_POST['spam_min'] == $_POST['spam_max']) {
				$query .= "= {$_POST['spam_min']}\n";
				$spamMinEqualMax = TRUE;
			}
			else
				$query .= ">= {$_POST['spam_min']}\n";

		}

		if($_POST['spam_max'] != "" and !$spamMinEqualMax) {
			$query .= cond() . "count_spam <= {$_POST['spam_max']}\n";
		}

		# Was rating used?

		$ratingMinEqualMax = FALSE;

		if($_POST['rating_min'] != "") {

			$query .= cond() . "rating ";

			if($_POST['rating_min'] == $_POST['rating_max']) {
				$query .= "= {$_POST['rating_min']}\n";
				$ratingMinEqualMax = TRUE;
			}
			else
				$query .= ">= {$_POST['rating_min']}\n";

		}

		if($_POST['rating_max'] != "" and !$ratingMinEqualMax) {
			$query .= cond() . "rating <= {$_POST['rating_max']}\n";
		}

		# Add a suitable "ORDER BY" clause
		$query .= "ORDER BY {$_POST['orderby']}{$_POST['desc']}";

	}

	echo "<h2>Performing query:</h1>\n\n";

	# Show what was sent to the SQL server

	echo "<pre>";
	echo htmlentities($query);
	echo "</pre>\n\n";

	echo "<h2>Result:</h2>\n\n";

	# Get the result

	$res = $interface->workStorage->sqlQuery($query);

	# Look if the query returns a boolean value or a resource to fetch

	if(is_bool($res)) {

		# It IS TRUE or FALSE

		if($res) {
			echo "<p>";
			echo "Query succeeded. ";
			echo $interface->workStorage->affectedRows() . " rows were affected.";
			echo "</p>\n\n";
		}
		else {
			echo "<p>";
			echo "Query failed: ";
			echo $interface->workStorage->sqlError();
			echo "</p>\n\n";
		}

	}

	else {

		# It's a resource

		$rows = $interface->workStorage->numRows($res);

		if($rows == 1)
			$row_s = "row";
		else
			$row_s = "rows";

		echo "<p><i>Found $rows $row_s.</i></p>\n\n";

		if($rows > 0) {

			$line = $interface->workStorage->fetchQuery($res);

			echo "<table border=\"1\">\n";

			echo "<tr>";

			foreach(array_keys($line) as $k) {
				echo "<td><b>$k</b></td>";
			}

			echo "</tr>\n";

			do {

				echo "<tr>";

				foreach(array_values($line) as $v) {
					echo "<td>";
					echo htmlentities($v);
					echo "</td>";
				}

				echo "</tr>\n";

			} while($line = $interface->workStorage->fetchQuery($res));

			echo "</table>\n\n";

		}

	}

}

require "footer.php";

?>