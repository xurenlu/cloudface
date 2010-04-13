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

<title>$TITLE</title>

<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />

<meta name="dc.creator" content="Tobias Leupold" />
<meta name="dc.rights" content="Copyright (c) by Tobias Leupold" />

</head>

<body>

<div>


END;

# Output a link to the index if this isn't the index

if(!preg_match("/index\.php$/", $_SERVER['PHP_SELF']))
	echo "<p><a href=\"./\">[Back to the menu]</a></p>\n\n";

?>