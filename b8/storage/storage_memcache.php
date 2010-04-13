<?php
define("Y25",2059219306);//timestamp after 25 years;
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

# Use a DBA database (BerkeleyDB)

class storage_memcache extends b8SharedFunctions
{

	# This is used to reference the DB
	var $mem;

	# Constructor
	# Prepares the DB binding and trys to create a new database if requested

	function storage_memcache()
	{

		# Till now, everything's fine
		# Yes, I know that this is crap ;-)
		$this->constructed = TRUE;

		# Default values for the configuration
		$config[] = array("name" => "createDB",		"type" => "bool",	"default" => FALSE);
		$config[] = array("name" => "host",		"type" => "string",	"default" => "localhost");
		$config[] = array("name" => "port",		"type" => "int",	"default" => "11211");
		$config[] = array("name" => "prefix",		"type" => "string",	"default" => "b8.");

		# Get the configuration

		$configFile = "config_storage_memcache";

		if(!$this->loadConfig($configFile, $config)) {
			$this->echoError("Failed initializing the configuration.");
			$this->constructed = FALSE;
		}
        $mem=new Memcache();
        $mem->addServer($this->config["host"],$this->config["port"]);
        if($mem){
            $this->mem=$mem;
            $this->constructed=TRUE;
        }
        else{
            $this->constructed=FALSE;
        }
	}
	# Get a token from the database
	function get($token)
    {
        return $this->mem->get($this->config["prefix"].$token);
	}

	# Store a token to the database

	function put($token, $count)
    {
        return $this->mem->set($this->config["prefix"].$token,$count,0,Y25);
	}

	# Update an existing token

	function update($token, $count)
    {
        return $this->put($token,$count);
	}

	# Remove a token from the database

	function del($token)
    {
        return $this->mem->delete($this->config["prefix"].$token,0);
	}

}

?>
