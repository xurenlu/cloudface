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

$TITLE = "b8 database maintainance interface &ndash; database backup/recovering";

if(isset($_GET['action']) or isset($_FILES['dbdump'])) {

	# Check what we want to do

	if(isset($_FILES['dbdump'])) {

		# We want to recover a database dump

		require "header.php";
		echo "<h1>Database recovering</h1>\n\n";

		# Check if a file was uploaded; simply show the main interface otherwise

		if($_FILES['dbdump']['tmp_name'] != "") {

			# Open the file and get it's first line
			$dz = fopen($_FILES['dbdump']['tmp_name'], "r");
			$line = fgets($dz);

			# Check if it's a b8 database dump
			if(strpos($line, "# b8 database dump") === FALSE){
				echo "<b>backup:</b> The uploaded file is no b8 database backup. Truncating.<br />\n";
				require "footer.php";
				exit;
			}

			# Recover it

			echo "<p>Recovering:</p>\n";
			echo "<pre>$line</pre>\n\n";

			$line = fgets($dz);

			# Get the interface
			require "interface_functions.php";
			$interface = new interfaceFunctions("noWorkStorage");

			# Check if everything worked smoothly
			if(!$interface->constructed) {
				echo "<b>backup:</b> Failed to initialize the interface class. Truncating.<br />\n";
				require "footer.php";
				exit;
			}

			$added = 0;
			$updated = 0;

			while(!feof($dz)) {

				# Get the dump line per line

				$line = fgets($dz);
				$line = chop($line);

				if($line == "")
					break;

				$data = explode(" ", $line, 2);

				# Insert the data

				if($interface->b8Storage->put($data[0], $data[1]))
					$added++;
				else {
					if($interface->b8Storage->update($data[0], $data[1]))
						$updated++;
					else {
						echo "<b>backup:</b> Failed to recover the database dump.<br />\n";
						require "footer.php";
						exit;
					}
				}

			}

			if($added == 1)
				$ent_add = "entry";
			else
				$ent_add = "entries";

			if($updated == 1)
				$ent_upd = "entry";
			else
				$ent_upd = "entries";

			echo "<p>Finished recovering the database (added $added new $ent_add, updated $updated existing $ent_upd).</p>\n\n";
			echo "<p><a href=\"{$_SERVER['PHP_SELF']}\">Back to database backup/recovering</a>";

			require "footer.php";
			exit;

		}

	}

	elseif($_GET['action'] == "dump") {

		# We want a database dump

		# Get the interface
		require "interface_functions.php";
		$interface = new interfaceFunctions("noWorkStorage");

		# Check if everything worked smoothly
		if(!$interface->constructed) {
			echo "<b>backup:</b> Failed to initialize the interface class. Truncating.<br />\n";
			require "footer.php";
			exit;
		}

		# Tell the browser this is a file to download
		header("Content-type: text/plain");
		header("Content-Disposition: attachment; filename=\"b8-dbdump-" . date("Y-m-d--H-i", time()) . ".txt\"");

		# Output the header
		echo "# b8 database dump, created " . date("Y-m-d H:i", time()) . "\n\n";

		# Output the database internals
		echo "bayes*texts.ham " . $interface->b8Storage->get("bayes*texts.ham")  . "\n";
		echo "bayes*texts.spam " . $interface->b8Storage->get("bayes*texts.spam") . "\n";
		echo "bayes*dbversion "  . $interface->b8Storage->get("bayes*dbversion")  . "\n";

		# Output all entries
		while($entry = $interface->b8Storage->getCursor()) {
			echo "{$entry[0]} {$entry[1]}\n";
		}

		# ... and quit
		exit;

	}

	elseif($_GET['action'] == "dropdb") {

		# We want to delete all content from b8's current database

		require "header.php";
		echo "<h1>Database recovering</h1>\n\n";

		# Get the interface
		require "interface_functions.php";
		$interface = new interfaceFunctions;

		# Check if everything worked smoothly
		if(!$interface->constructed) {
			echo "<b>backup:</b> Failed to initialize the interface class. Truncating.<br />\n";
			require "footer.php";
			exit;
		}

		# Delete all content from the current database
		if(!$interface->b8Storage->drop()) {
			echo "<b>backup:</b> Failed emptying the current database.<br />\n";
			require "footer.php";
			exit;
		}

		# Insert the dbversion token, so that the database will
		# work, even if no backup file is recovered afterwards
		if(!$interface->b8Storage->put("bayes*dbversion", "2")) {
			echo "<b>backup:</b> Failed setting the database version.<br />\n";
			require "footer.php";
			exit;
		}

		echo "<p>Deleted all content from the current database.</p>\n\n";
		echo "<p><a href=\"{$_SERVER['PHP_SELF']}\">Back to database backup/recovering</a>";

		require "footer.php";
		exit;

	}

	else {

		# Garbage in ?action=

		require "header.php";
		echo "<h1>Database backup/recovering</h1>\n\n";
		echo "<b>backup:</b> Unknown command. Truncating.<br />\n";
		require "footer.php";
		exit;

	}

}

# If we reached here, output the basic interface

require "header.php";

echo <<<END
<h1>Database backup/recovering</h1>

<h2>Database backup</h2>

<p>
A database backup will be provided by the following link:<br />
<a href="{$_SERVER['PHP_SELF']}?action=dump">Database backup</a>
</p>

<h2>Database recovering</h2>

<p>Select a file containing a b8 database dump:</p>

<form action="{$_SERVER['PHP_SELF']}" method="post" enctype="multipart/form-data">

<input name="dbdump" type="file" />
<input type="submit" value="Recover database" />

<p>
The database dump will be merged into the current database. Non-existing entries will be added, existing ones will be updated. Entries that exist in the database but not in the dump will be left untouched.
</p>

<p>
If you want your database completely replaced by the dump, you can<br />
<a href="{$_SERVER['PHP_SELF']}?action=dropdb">delete all content from the current database</a><br />
before. <b>HAVE A BACKUP WHEN DOING THIS! ALL DATA COULD BE LOST!
</p>

</form>


END;

require "footer.php";

?>