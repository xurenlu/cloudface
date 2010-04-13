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

$TITLE = "b8 interface work table functions";
require "header.php";

if(isset($_GET['b82sql'])) {

	# Copy all token data from the b8 database to the work database

	# Set up the interface
	require "interface_functions.php";
	$interface = new interfaceFunctions;

	# Check if everything worked smoothly
	if(!$interface->constructed) {
		echo "<b>workdb:</b> Failed to initialize the interface class. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Create the work table
	if(!$interface->workStorage->createWorkTable()) {
		echo "<b>workdb:</b> Failed to create the work table. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Get the number of ham and spam texts stored
	# (needed to calculate the spam probability)
	$texts_ham = $interface->b8Storage->get("bayes*texts.ham");
	$texts_spam = $interface->b8Storage->get("bayes*texts.spam");

	# Insert all tokens into the work database

	$inserted = 0;

	while($entry = $interface->b8Storage->getCursor()) {

		$data['token'] = $entry[0];

		$tmp = explode(" ", $entry[1]);

		$data['count_ham'] = $tmp[0];
		$data['count_spam'] = $tmp[1];

		preg_match("/(\d{2})(\d{2})(\d{2})/", $tmp[2], $tmp);
		$data['lastseen'] = "20{$tmp[1]}-{$tmp[2]}-{$tmp[3]}";

		$data['rating'] = $interface->b8Calc->calcProbability($entry[1], $texts_ham, $texts_spam);

		# Insert the separated and calculated data into the work table

		if(!$interface->workStorage->sqlQuery("
			INSERT INTO " . $interface->workStorage->config['tableName'] . "(
				token,
				count_ham,
				count_spam,
				lastseen,
				rating
			)
			VALUES(
				'" . $interface->workStorage->escapeString($data['token']) . "',
				'{$data['count_ham']}',
				'{$data['count_spam']}',
				'{$data['lastseen']}',
				'{$data['rating']}'
			)
			")) {

			# Something didn't work, so break ...

			# ... try to empty the table ...
			$interface->workStorage->createWorkTable();

			# ... and quit

			echo "<b>workdb:</b> Failed to insert token \"" . htmlentities($data['token']) . "\". Truncating.<br />\n";

			require "footer.php";
			exit;

		}

		$inserted++;

	}

	echo "<p>Inserted $inserted tokens into the work database.</p>\n\n";

}

elseif(isset($_GET['sql2b8'])) {

	# Copy all tokens from the work database to the b8 database

	# Set up the interface
	require "interface_functions.php";
	$interface = new interfaceFunctions;

	# Check if everything worked smoothly
	if(!$interface->constructed) {
		echo "<b>workdb:</b> Failed to initialize the interface class. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Delete all tokens from b8's database

	if(!$interface->b8Storage->wipeTokens()) {
		echo "<b>workdb:</b> Failed to clean b8's database. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Select all relevant entries

	$res = $interface->workStorage->sqlQuery("
		SELECT
			token,
			count_ham,
			count_spam,
			DATE_FORMAT(lastseen, '%y%m%d') AS lastseen
		FROM " . $interface->workStorage->config['tableName'] . "
		");

	if(!$res) {
		echo "<b>workdb:</b> Failed to query the database. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	# Get all entries and put them into b8's database

	$inserted = 0;

	while($data = $interface->workStorage->fetchQuery($res)) {

		if(!$data) {
			echo "<b>workdb:</b> Failed to fetch the query. Truncating.<br />\n";
			require "footer.php";
			exit;
		}

		# Assemble the data ...
		$token = $data['token'];
		$data = "{$data['count_ham']} {$data['count_spam']} {$data['lastseen']}";

		# ... and put it in b8's database
		if(!$interface->b8Storage->put($token, $data)) {
			echo "<b>workdb:</b> Failed to update b8's database. Truncating.<br />\n";
			require "footer.php";
			exit;
		}

		$inserted++;

	}

	echo "<p>Inserted $inserted tokens into b8's database.</p>\n\n";

}

else {

echo <<<END
<h1>Work database functions</h1>

<p>You can &hellip;</p>

<dl>

<dt><a href="{$_SERVER['PHP_SELF']}?b82sql">Create a work database from the current b8 database</a></dt>
<dd>This will create a queryable SQL database from the current b8 database with all tokens, counts and ratings.<br /><b>THE WORK TABLE GIVEN IN THE CONFIG FILE WILL BE DELETED AND RE-CREATED WHEN DOING THIS!</b><br />&nbsp;</dd>

<dt><a href="{$_SERVER['PHP_SELF']}?sql2b8">Make the work database the current b8 database</a><dt>
<dd><b>PLEASE HAVE A BACKUP WHEN DOING THIS!</b><br />
This will first delete all tokens from the current b8 database and then fill in all tokens found in the work database.<br />
<b>If something goes wrong doing this, YOUR DATA COULD BE LOST COMPLETELY!</b></dd>

</dl>


END;

}

require "footer.php";

?>