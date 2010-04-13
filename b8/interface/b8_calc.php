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

# Get the b8 base class
require_once dirname(__FILE__) . "/../b8.php";

class b8Calc extends b8
{

	function b8Calc()
	{

		# As we just need b8's probability calculation of a given token that does
		# exist in the database (the calcProbability() function), we extend b8 and
		# create a new class constructor that does not set up the lexer and
		# storage class.

		# ... but we need b8's storage backend name

		# Till now, everything's fine
		# Yes, I know that this is crap ;-)
		$this->constructed = TRUE;

		# The default configuration
		$config[] = array("name" => "databaseType",	"type" => "string",	"default" => "dba");
		$config[] = array("name" => "useRelevant",	"type" => "int",	"default" => 15);
		$config[] = array("name" => "minDev",		"type" => "float",	"default" => 0.2);
		$config[] = array("name" => "robS",		"type" => "float",	"default" => 0.3);
		$config[] = array("name" => "robX",		"type" => "float",	"default" => 0.5);
		$config[] = array("name" => "sharpRating",	"type" => "bool",	"default" => FALSE);

		# This is just b8's default value and won't be used. But if not set here, we will get
		# error messages about the entry "lexerType" in the configuration file.
		$config[] = array("name" => "lexerType",	"type" => "string",	"default" => "default");

		if(!$this->loadConfig("config_b8", $config)) {
			$this->echoError("Failed initializing the configuration. Truncating.");
			$this->constructed = FALSE;
		}

	}

	# Dummy functions that overwrite the default ones, so that they aren't used accidentally

	# Tell the user all these functions don't exist ;-)

	function b8CalcError($functionName)
	{

		$this->echoError("This is just the b8Calc class. The function <kbd>$functionName</kbd> will be provided by the basic b8 class, not by this one.");

		return FALSE;

	}

	function checkCategory()
	{
		return $this->b8CalcError("checkCategory");
	}

	function learn()
	{
		return $this->b8CalcError("learn");
	}

	function unlearn()
	{
		return $this->b8CalcError("unlearn");
	}

	function classify()
	{
		return $this->b8CalcError("classify");
	}

	function getProbability()
	{
		return $this->b8CalcError("getProbability");
	}

	# This one is actually provided by this class ;-)
	#function calcProbability($data, $texts_ham, $texts_spam)

	function updateLastseen()
	{
		return $this->b8CalcError("updateLastseen");
	}

}

?>