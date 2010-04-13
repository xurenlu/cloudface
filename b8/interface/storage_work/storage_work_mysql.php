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

# Get the shared functions class file (if not already loaded)
require_once dirname(__FILE__) . "/../../shared_functions.php";

# Use a MySQL table

class storage_work_mysql extends b8SharedFunctions
{

	# This contains the MySQL-resource link
	var $mysqlRes;

	# Constructor
	# Set up and test the MySQL connection

	function storage_work_mysql()
	{

		# Till now, everything's fine
		# Yes, I know that this is crap ;-)
		$this->constructed = TRUE;

		# Default values for the configuration
		$config[] = array("name" => "tableName",	"type" => "string",	"default" => "b8_wordlist");
		$config[] = array("name" => "host",		"type" => "string",	"default" => "localhost");
		$config[] = array("name" => "user",		"type" => "string",	"default" => "");
		$config[] = array("name" => "pass",		"type" => "string",	"default" => "");
		$config[] = array("name" => "db",		"type" => "string",	"default" => "");

		# Get the configuration

		$configFile = "config_storage_work";

		if(!$this->loadConfig($configFile, $config)) {
			$this->echoError("Failed initializing the configuration.");
			$this->constructed = FALSE;
		}

		if($this->constructed) {

			# Get the MySQL link resource to use

			$arg = FALSE;

			if(func_num_args() > 0)
				$arg = func_get_arg(0);

			if($arg != FALSE) {

				# A resource was passed, so use this one ...
				$this->mysqlRes = $arg;

				# ... and check if it's really a MySQL-link resource

				$argType = gettype($this->mysqlRes);

				if(!is_resource($this->mysqlRes)) {
					$this->echoError("The given argument is not a resource (passed variable: \"$argType\"). Please be sure to setup a proper MySQL connection in <kbd>connect_mysql.php</kbd> or comment out or delete this file and make sure that all of the following values are set in <kbd>$configFile</kbd>: <i><kbd>host</kbd></i>, <i><kbd>user</kbd></i>, <i><kbd>pass</kbd></i> and <i><kbd>db</kbd></i> so that a separate MySQL connection can be set up by the interface.");
					$this->constructed = FALSE;
				}

				$resType = get_resource_type($this->mysqlRes);

				if($resType != "mysql link" and $this->constructed) {
					$this->echoError("The passed resource is not a MySQL-link resource (passed resource: \"$resType\"). Please be sure to setup a proper MySQL connection in <kbd>connect_mysql.php</kbd> or comment out or delete this file and make sure that all of the following values are set in <kbd>$configFile</kbd>: <i><kbd>host</kbd></i>, <i><kbd>user</kbd></i>, <i><kbd>pass</kbd></i> and <i><kbd>db</kbd></i> so that a separate MySQL connection can be set up by the interface.");
					$this->constructed = FALSE;
				}

			}

			else {

				# No resource was passed, so we want to set up our own connection

				# Set up the MySQL connection
				$this->mysqlRes = mysql_connect($this->config['host'], $this->config['user'], $this->config['pass']);

				# Check if it's okay
				if($this->mysqlRes == FALSE) {
					$this->echoError("Could not connect to MySQL.");
					$this->constructed = FALSE;
				}

				if($this->constructed) {
					# Open the database where the wordlist is/will be stored
					if(!mysql_select_db($this->config['db'])) {
						$this->echoError("Could not select the database \"$db\".");
						$this->constructed = FALSE;
					}
				}

			}

		}

	}

	# Do an SQL query

	function sqlQuery($query)
	{
		return mysql_query($query, $this->mysqlRes);
	}

	# Prepare the work table

	function createWorkTable()
	{

		# Check if the work table exists. If so, drop it.
		# You have been warned that b8 will do this, folks ;-)

		if($this->sqlQuery("
			DESCRIBE " . $this->config['tableName']
			)) {
			if(!$this->sqlQuery("DROP TABLE " . $this->config['tableName'])) {
				$this->echoError("Could not drop the existing table <kbd>" . $this->config['tableName'] . "</kbd>.");
				return FALSE;
			}
		}

		# Create the work table

		if(!$this->sqlQuery("
			CREATE TABLE " . $this->config['tableName'] . "(
				token      VARCHAR(255) BINARY PRIMARY KEY,
				count_ham  INT UNSIGNED,
				count_spam INT UNSIGNED,
				lastseen   DATE,
				rating     DECIMAL(6,5)
			)
			")) {

			$this->echoError("Could not create the work table <kbd>" . $this->config['tableName'] . "</kbd>");
			return FALSE;

		}

		# If we reached this line, we should have a new empty work table
		return TRUE;

	}

	# Return a properly escaped string

	function escapeString($string)
	{
		return mysql_real_escape_string($string, $this->mysqlRes);
	}

	# Get the results of a query

	function fetchQuery($res)
	{
		return mysql_fetch_assoc($res);
	}

	# Get the number of affected rows from the last query

	function affectedRows()
	{
		return mysql_affected_rows($this->mysqlRes);
	}

	# Get the number of returned rown from a resource

	function numRows($res)
	{
		return mysql_num_rows($res);
	}

	# Get the last SQL Error

	function sqlError()
	{
		return mysql_error($this->mysqlRes);
	}

	# Output the database's link resource, so that
	# b8's storage backend can use the same

	function dbResource()
	{
		return $this->mysqlRes;
	}

}

?>