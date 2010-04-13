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

# Get the base MySQL storage class (and the shared functions)
require_once dirname(__FILE__) . "/../../storage/storage_mysql.php";

# Use a MySQL table

class storage_b8_mysql extends storage_mysql
{

	# This contains a resource for a SELECT * query
	var $selectRes;

	# Read the whole database entry by entry (excluding database internals)

	function getCursor()
	{

		# Check if this is called for the first time

		if(!$this->selectRes) {

			# If so, query MySQL for all entries

			$this->selectRes = mysql_query("
				SELECT *
				FROM " . $this->config['tableName'] . "
				WHERE token NOT LIKE 'bayes*%'
				", $this->mysqlRes);

		}

		# Get the current entry
		$tmp = mysql_fetch_assoc($this->selectRes);

		# Check if it exists
		if($tmp !== FALSE) {
			# It's there, so return it
			return array($tmp['token'], $tmp['count']);
		}
		else {
			# We reached the end of the database
			return FALSE;
		}

	}

	# Delete all tokens

	function wipeTokens()
	{
		return mysql_query("
			DELETE FROM " . $this->config['tableName'] . "
			WHERE token NOT LIKE 'bayes*%'
			", $this->mysqlRes);
	}

	# Empty the whole database

	function drop()
	{
		return mysql_query("DELETE FROM " . $this->config['tableName'], $this->mysqlRes);
	}

	# Optimize a table

	function optimize()
	{

		$res = mysql_query("OPTIMIZE TABLE " . $this->config['tableName'], $this->mysqlRes);

		$line = mysql_fetch_assoc($res);

		if($line['Msg_text'] == "OK")
			return "Optimized the database";
		else
			return $line['Msg_text'];

	}

}

?>