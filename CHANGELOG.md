Changelog
=========

celutz-2.0.0 (unreleased)
-------------------------

  * New home for the project: <https://code.ffdn.org/FFDN/celutz>.
  * First release with a brand new backend, completely rewritten in Django.
  * Distances are now computed as straight-line distance, instead of
    great-circle distance.  This should mostly matter for points that are
    very close together, but with different altitudes.
  * The URL of the panorama view acts as an auto-generated permalink
    (à la openstreetmap.org).
  * Existing panoramas can be used as reference points as well.
  * Tile generation is now done in pure Python, instead of the existing shell
    script that used Imagemagick's `convert` tool.

The map (and related features) are not yet integrated in this new version.

celutz-1.x
----------

Between March 2013 and February 2015, lots of improvements:

  * Allow to calibrate the panorama directly from the web interface, by
    simply clicking on the picture to add reference points.  This is done
    with AJAX requests.
  * Add a map displaying the panoramas.
  * Allow to draw a line on the map by pointing at a direction in a panorama.
    This can be very useful to pinpoint an unknown building in a picture,
    because the line on the map gives a good indication of the location of
    the building.
  * Make the code less specific to tetaneutral.net.

The code is available at <https://redmine.tetaneutral.net/projects/celutz>.

29 March 2013: celutz-1.0
-------------------------

  * First public version of celutz, with a PHP backend and a Javascript interface.
