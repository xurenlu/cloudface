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

$TITLE = "b8 database maintainance interface";
require "header.php";

echo <<<END
<h1>b8 database maintainance</h1>

<h2>b8 storage backend functions</h2>

<ul>
<li><a href="backup.php">Database backup/recovering</a></li>
<li><a href="dboptimize.php">Database optimization</a></li>
</ul>

<h2>Work database functions</h2>

<ul>
<li><a href="workdb.php">Work database creation / b8 database sync</a></li>
<li><a href="dbinfo.php">Database info</a> (needs a work database)</li>
<li><a href="dbedit.php">Database edit interface</a> (needs a work database)</li>
</ul>


END;

require "footer.php";

?>