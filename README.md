Celutz
======

*Visualize a collection of panoramic photos.*

**Celutz** allows you to upload/share/visualize/reference panoramic photos.
It has been created for evaluating lines-of-sight for radio networks.

The first version of this tool was written in PHP/js by Marc Souviron,
Victor Pongnian, and subsequent work by Jocelyn Delalande.  The project
originated at [tetaneutral.net](http://tetaneutral.net), a non-profit radio
ISP in France.

This is version 2 of celutz, with a backend rewritten in Django.  For more
information, see `CHANGELOG.md.`

Features
--------

* **upload** panoramas to a web server (i.e: made with [Hugin](hugin.sf.net));
* **visualize**, pan and zoom panoramas, as if you were on site;
* **georeference** panoramas : set GPS coordinates and elevation of known
  reference points, and calibrate orientation of panoramas by visually pointing
  at these reference points;
* **visualize a point** by its lat/lon/altitude on your panorama;
* **see other panoramas** locations to evaluate the lines-of-sight;
* **locate a point** on all panoramas simultaneously.

Getting started: basic usage of celutz
--------------------------------------

### Add reference points

If this is a new installation, you first need to add reference points
to the database.

Reference points are needed to visually calibrate panoramic photos:
they can be high buildings, clock towers, radio towers, or even natural features
such as mountains.  In short, reference points should be easily and accurately
recognisable when seen on a picture.

To add new reference points, go to the Django admin, for instance at
<http://localhost:8000/admin/panorama/referencepoint>.

You need a name, GPS coordinates, and an altitude.  The altitude is relative to
the sea level, so you need to figure out the ground altitude and add the height
of the reference point (e.g. height of the building).
In the future, the ground altitude will be computed automatically.

*Hint: it is better to set the altitude of the topmost part of a building.
 This is because it will be much easier to aim when viewing a panorama.*

### Upload a new panoramic photo

You can upload a new panoramic photo from the home page.  Besides the actual
picture, you need to specify the GPS coordinates where the picture has been
made, and the altitude (exactly like reference points).  If the picture
encompasses 360° (i.e. the left-most edge connects to the right-most edge),
then tick the appropriate box.

Once the picture is uploaded, it may take a while for the tiles to be generated.
If the visualisation only show grey squares, wait a bit and try to refresh.
Depending on the size of the picture and the CPU of the server, generating tiles
can take from a few seconds to a minute.

### Calibrate the panoramic photo

Now, you should be able to zoom and pan in your picture.  But the azimuth and
elevation are completely wrong, because the panorama is not yet calibrated.

To calibrate it, you need to do the following:

1. Find a known reference point on your picture
2. Right-click on its location, and in the menu, select its name

You should repeat these steps for as much reference points as possible, since
it will increase the accuracy of the interpolation.  The minimum number of
reference points is two for normal pictures, and one for 360° pictures.

Once the panorama is calibrated, the azimuth and elevation should be meaningful!
You should also see colored circle indicating the location of other panoramas.

Panorama view
--------------

This is the main view, where you can pan and scroll a panorama.

### Color code

In a calibrated panorama, you should see colored circles:

* *Blue circle*: reference point that was referenced by a user during calibration;
* *Green circle*: estimated location of a reference point, determined by
  interpolation between known reference points (the blue circles);
* *Red circle*: estimated location of another panorama.  You can click on the circle
  to switch to the view from this panorama!

### Mouse interaction for panorama view ###

* *drag image* to move around
* *scroll* to zoom in/out
* *right-click* to get the Reference points menu, where you can add and remove
  reference points

### Keyboard shortcuts for panorama view ###

* `Pgup`/`Pgdown`: zoom in/out
* `←`/`↑`/`↓`/`→`: pan the image
* `Home`/`End`: turn backwards (180°)

Locating a point
----------------

You can use the "Locate a point" feature from the homepage.  It allows you
to locate a point (given its GPS coordinates) on all panoramas at the same time.

For each panorama that can "see" the target point, a direct link is provided to
orient the view to the estimated position.  This allows you to quickly ascertain
whether the target point is actually visible from at least one existing location.

Installing celutz
-----------------

See `INSTALL.md`.
