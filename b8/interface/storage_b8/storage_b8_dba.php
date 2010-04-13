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

# Get the base DBA storage class (and the shared functions)
require_once dirname(__FILE__) . "/../../storage/storage_dba.php";

# Use a DBA database

class storage_b8_dba extends storage_dba
{

	# This contains a pointer in the database
	var $cursor;

	# Read the whole database entry by entry (excluding database internals)

	function getCursor()
	{

		# Check if this is called for the first time

		if(!$this->cursor) {
			# If so, the cursor is the first key
			$this->cursor = dba_firstkey($this->db);
		}
		else {
			# Otherwise, we want the next key
			$this->cursor = dba_nextkey($this->db);
		}

		# If the current token is a database internal, choose the next one

		while(strpos($this->cursor, "bayes*") !== FALSE and $this->cursor !== FALSE)
			$this->cursor = dba_nextkey($this->db);

		# Check if there remains data to fetch

		if($this->cursor !== FALSE) {
			# The key exists, so return the key and the value
			return array($this->cursor, dba_fetch($this->cursor, $this->db));
		}
		else {
			# We reached the end of the database
			return FALSE;
		}

	}

	# Delete all tokens

	function wipeTokens()
	{

		# Read all token names and delete them if they aren't database internals

		for($key = dba_firstkey($this->db); $key !== FALSE; $key = dba_nextkey($this->db)) {
			if(strpos($key, "bayes*") === FALSE) {
				if(!$this->del($key))
					return FALSE;
			}
		}

		return TRUE;

	}

	# Empty the whole database

	function drop()
	{

		# Read all token names and delete them

		for($key = dba_firstkey($this->db); $key !== FALSE; $key = dba_nextkey($this->db)) {
			if(!$this->del($key))
				return FALSE;
		}

		return TRUE;

	}

	# Optimize the Database

	function optimize()
	{
		if(dba_optimize($this->db) == TRUE)
			return "Optimized the database";
		else
			return "Failed to optimize the database";
	}

}

?>