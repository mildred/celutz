Upgrading from celutz 1.0
=========================

Here are some instructions to migrate from celutz 1.0 (PHP version)
to the new Django version.  All data will be migrated: panorama images,
panorama meta-data, reference points, and "references" (calibration of a
panorama using several reference points).  Tiles will not be migrated,
since they can easily be regenerated.

Pre-requisite
-------------

These instructions assume that the old PHP version and the new Django version
are installed on distinct machines ("old server" and "new server" respectively).
Of course, they can actually be the same machine.

You need:

- access to the files of the old celutz instance (no need to be able to run
  the code itself);

- ability to run simple command-line PHP5 scripts (no dependencies) on the old
  server;

- the Django version of celutz is installed and configured on the new server;

- the Django database is up-to-date with respect to migrations, but empty
  (no panorama or reference point);

- enough disk space to store panorama and tiles on the new server.


Export data from the old server
-------------------------------

There are three PHP scripts that export the relevant data to JSON: information
about panoramas, reference points, and references.

    # Export panoramas
    php upgrade/export_panorama.php /path/to/old/celutz | tee panoramas.json
    # Export one or more set of reference points
    php upgrade/export_refpoints.php /path/to/old/celutz/ref_points/my_ref_points.php | tee refpoints.json
    # Export references
    php upgrade/export_references.php /path/to/old/celutz | tee references.json

Besides these three JSON files, you also need to copy panorama images
(everything in `upload/`).
You don't need to copy the tiles.

Import data on the new server
-----------------------------

First copy all panorama images to `media/pano/` (create it if necessary).

**Warning**: for the next step, make sure the Django database is empty!
That is, if you already have panorama or reference points, they will likely
be overriden by the import (and the database might end up in an inconsistent 
state).

    # Enter virtualenv if necessary
    # Import panoramas
    python manage.py loaddata panoramas.json
    # Then import reference points
    python manage.py loaddata refpoints.json
    # For importing references, a more complex conversion is needed
    python manage.py import_references references.json

If all commands run without error, you're probably all good.  If the first
import command complains about missing images, make sure they are available
in the `media/pano/` directory, under the expected file name.

Regenerate all tiles
--------------------

Simply connect to the Django admin at <http://www.example.com/admin/panorama/panorama/>,
tick all panorama, and choose "Regenerate tiles for the selected panoramas"
in the dropdown list of actions.

This will take a few minutes to complete, you can follow the progress by
reloading the admin page (look at the "Has tiles" column).

Manually importing a panorama
-----------------------------

Sometimes, things are not that simple, and you need to "manually" import a
panorama.  For instance, if the panorama image is at an unusual place or
has an unusual name.

In this case, you can use the two scripts `upgrade/export_single_pano.php`
and `./manage.py import_single_pano` to manually export and import a
panorama.  Usage:

    php upgrade/export_single_pano.php /path/to/site.params | ./manage.py import_single_pano /path/to/panorama.tif

The PHP script will convert the parameters file to a JSON representation,
which is then passed to a Django command (along with the actual panorama
image) for importing into the database.  The Django command then launches
the tile generation process on the new panorama.

A copy of the image file will be put into the `media/pano` directory,
meaning you can remove the original image file once you ensured that
the import process went smoothly.

For convenience, a simple shell script that does exactly the above is provided:
`upgrade/import_single_pano.sh`.
