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

echo <<<END
<?xml version="1.0" encoding="iso-8859-1"?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
   "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>

<title>b8 DBA version check</title>

<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />

<meta name="dc.creator" content="Tobias Leupold" />
<meta name="dc.rights" content="Copyright (c) by Tobias Leupold" />

</head>

<body>

<div>

<h1>DBA version check</h1>

<p>The following table shows all availible DBA handlers.</p>


END;

echo "<table border=\"1\">\n";

$possible = array();

foreach(dba_handlers(true) as $name => $version) {

	$version = str_replace("$", "", $version);
	echo "<tr><td><b>$name</b></td><td>$version</td></tr>\n";

	if(strpos($version, "Berkeley DB") !== FALSE) {
		$possible[$name] = $version;
	}

}

echo "</table>\n\n";

echo "<p>The following hanlder(s) seem to be suitable for b8's DBA storage backend:</p>\n\n";

if(count($possible) == 0) {
	echo "<p><i>No suitable DBA handlers found</i></p>\n\n";
}

else {

	echo "<table border=\"1\">\n";

	foreach($possible as $name => $version)
		echo "<tr><td><b>$name</b></td><td>$version</td></tr>\n";

	echo "</table>\n\n";

}

echo <<<END
</div>

</body>

</html>
END;

?>