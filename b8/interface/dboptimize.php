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

$TITLE = "b8 interface database optimization";
require "header.php";

echo "<h1>Database optimization</h1>";

if(!isset($_GET['optimize'])) {

echo <<<END
<p>
From time to time, it is useful to optimize the structure of the used database, when a lot of updating or deleting data was done (as perhaps, the database will insert a new entry and mark the existing as deleted if a token was updated instead of really updating this token).
</p>

<p>
This will delete wasted space and optimize the database's structure. Anyway, it won't hurt even if everything is okay ;-) So, if you want to optimize your database, click on the following link:
</p>

<p>
<a href="?optimize">Optimize the database</a>
</p>


END;

}

else {

	# Set up the interface
	require "interface_functions.php";
	$interface = new interfaceFunctions("noWorkStorage");

	# Check if everything worked smoothly
	if(!$interface->constructed) {
		echo "<b>workdb:</b> Failed to initialize the interface class. Truncating.<br />\n";
		require "footer.php";
		exit;
	}

	echo "<p>" . $interface->b8Storage->optimize() . "</p>\n\n";

}

require "footer.php";

?>