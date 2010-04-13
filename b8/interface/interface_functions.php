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
require_once dirname(__FILE__) . "/../shared_functions.php";

# The interface's base class that provides all functionality used by the interface

class interfaceFunctions extends b8SharedFunctions
{

	# This will contain the modified b8 class
	var $b8Calc;

	# This will contain b8's storage backend
	var $b8Storage;

	# This will contain the work storage backend
	var $workStorage;

	# Constructor
	# Load and check all the stuff we need

	function interfaceFunctions()
	{

		# Till now, everything's fine
		# Yes, I know that this is crap ;-)
		$this->constructed = TRUE;

		$thisDir = dirname(__FILE__);

		# The default configuration
		$config[] = array("name" => "workStorage",	"type" => "string",	"default" => "mysql");
		$config[] = array("name" => "shareConnection",	"type" => "bool",	"default" => FALSE);

		# Check if a parameter was passed

		$passedArgsNum = func_num_args();

		if($passedArgsNum > 0) {
			for($i = 0; $i < $passedArgsNum; $i++) {
				$passedArg[func_get_arg($i)] = 1;
			}
		}
		else {
			$passedArg = FALSE;
		}

		# Get the configuration

		$configFile = "config_interface";

		# Check if everything worked smoothly

		if(!$this->loadConfig($configFile, $config)) {
			$this->echoError("Failed initializing the configuration.");
			$this->constructed = FALSE;
		}

		if($this->constructed) {

			# Set up the modified b8 class
			$this->loadClass("$thisDir/b8_calc.php", "b8Calc", "b8Calc", FALSE);

			# Check if everything worked smoothly

			if(!$this->b8Calc->constructed) {
				$this->echoError("Could not initialize the modified b8 class. Truncating.");
				$this->constructed = FALSE;
			}

		}

		# Check if we need a relational database

		if($this->constructed and !isset($passedArg['noWorkStorage'])) {

			# Set up the work storage class
			$this->loadClass("$thisDir/storage_work/storage_work_" . $this->config['workStorage'] . ".php", "storage_work_" . $this->config['workStorage'], "workStorage", FALSE);

			# Check if everything worked smoothly

			if(!$this->workStorage->constructed) {
				$this->echoError("Could not initialize the work storage class. Truncating.");
				$this->constructed = FALSE;
			}

		}

		if($this->constructed) {

			# Set up b8's storage class

			# First, we assume that b8's storage backend does not need the work storage's db link
			$dbLink = FALSE;

			# Check if we share the interface's database link
			if($this->config['shareConnection'])
				$dbLink = $this->workStorage->dbResource();

			# get the storage class
			$classFile = "$thisDir/storage_b8/storage_b8_" . $this->b8Calc->config['databaseType'] . ".php";
			$className = "storage_b8_" . $this->b8Calc->config['databaseType'];

			# Load the proper class file and set up the new storage object
			$this->loadClass($classFile, $className, "b8Storage", $dbLink);

			# Check if everything worked smoothly

			if(!$this->b8Storage->constructed) {
				$this->echoError("Could not initialize b8's storage class. Truncating.");
				$this->constructed = FALSE;
			}

		}

	}

}

?>