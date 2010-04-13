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

$TITLE = "b8 interface database info";
require "header.php";

echo "<h1>Database info</h1>";

# Set up the interface
require "interface_functions.php";
$interface = new interfaceFunctions;

# Check if everything worked smoothly
if(!$interface->constructed) {
	echo "<b>workdb:</b> Failed to initialize the interface class. Truncating.<br />\n";
	require "footer.php";
	exit;
}

# Get all relevant information

# Info from b8's database
$info['texts_ham'] = $interface->b8Storage->get("bayes*texts.ham");
$info['texts_spam'] = $interface->b8Storage->get("bayes*texts.spam");
$info['dbversion'] = $interface->b8Storage->get("bayes*dbversion");

# Token info from the work database

# Number of ham tokens in the database

$res = $interface->workStorage->sqlQuery("
	SELECT COUNT(token) AS count
	FROM " . $interface->workStorage->config['tableName'] . "
	WHERE count_ham > 0
	");

$tmp = $interface->workStorage->fetchQuery($res);

$info['tokens_ham'] = $tmp['count'];

# Number of spam tokens in the database

$res = $interface->workStorage->sqlQuery("
	SELECT COUNT(token) AS count
	FROM " . $interface->workStorage->config['tableName'] . "
	WHERE count_spam > 0
	");

$tmp = $interface->workStorage->fetchQuery($res);

$info['tokens_spam'] = $tmp['count'];

# Number of spam tokens both in ham and spam

$res = $interface->workStorage->sqlQuery("
	SELECT COUNT(token) AS count
	FROM " . $interface->workStorage->config['tableName'] . "
	WHERE
		count_ham > 0
		AND count_spam > 0
	");

$tmp = $interface->workStorage->fetchQuery($res);

$info['tokens_both'] = $tmp['count'];

# Oldest token

$res = $interface->workStorage->sqlQuery("
	SELECT MIN(lastseen) AS date
	FROM " . $interface->workStorage->config['tableName'] . "
	");

$tmp = $interface->workStorage->fetchQuery($res);

$info['oldest'] = $tmp['date'];

# Newest token

$res = $interface->workStorage->sqlQuery("
	SELECT MAX(lastseen) AS date
	FROM " . $interface->workStorage->config['tableName'] . "
	");

$tmp = $interface->workStorage->fetchQuery($res);

$info['newest'] = $tmp['date'];

# All tokens
$info['tokens'] = $info['tokens_ham'] + $info['tokens_spam'] - $info['tokens_both'];

echo <<<END
<table>
<tr><td><b>Database version:</b></td><td>{$info['dbversion']}</td></tr>
<tr><td><b>Learned ham texts:</b></td><td>{$info['texts_ham']}</td></tr>
<tr><td><b>Learned spam texts:</b></td><td>{$info['texts_spam']}</td></tr>
<tr><td><b>Tokens in the database:</b></td><td>{$info['tokens']}</td></tr>
<tr><td><b>Ham tokens:</b></td><td>{$info['tokens_ham']}</td></tr>
<tr><td><b>Spam tokens:</b></td><td>{$info['tokens_spam']}</td></tr>
<tr><td><b>Tokens both in ham and spam:</b></td><td>{$info['tokens_both']}</td></tr>
<tr><td><b>Least recent seen token date:</b></td><td>{$info['oldest']}</td></tr>
<tr><td><b>Most recent seen token date:</b></td><td>{$info['newest']}</td></tr>
</table>


END;

require "footer.php";

?>