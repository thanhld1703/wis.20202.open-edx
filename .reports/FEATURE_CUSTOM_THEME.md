In order to create our custom theme, we first follow the recommended theme structure from the edX repo as follows:

    custom-theme
    └── lms
        ├── static
        │   ├── images
        │   │   └── logo.png
        │   └── sass
        │       ├── _overrides.scss
        │       ├── lms-main-rtl.scss
        │       └── lms-main.scss
        └── templates
            ├── footer.html
            └── header.html

Images
------

Images is substituted simply by placing the new image at the right place
in the theme directory  lms/static/images/logo.png then, the image is overridden.

Sass/CSS
--------
In order to override the default style of the project, we need to mirror the scss files containing the custom style of our theme with the original scss files in LMS, these files are all desinated in static/sass directories, however, some of them are held in sub-folder of the sass folder, hence we also need to recreate those folder in order to successfully override the needed scss.

- For our two themes we follow these steps to change the appearance of edX sites:


HTML Templates
--------------

You can make changes to HTML templates by copying them to your theme directory
in the appropriate place, and making the changes you need.  Keep in mind that
in the future if you upgrade the Open edX code, you may have to update the
copied template in your theme also.

Template Names
==============

Here are the list of template names that you *should* use in your comprehensive
theme (so far):

* ``header.html``
* ``footer.html``

Installing your theme
---------------------

To use your theme, you need to add a configuration value pointing to your theme
directory. There are two ways to do this.

#.  If you usually edit server-vars.yml:

    #.  As the vagrant user, edit (or create)
        /edx/app/edx_ansible/server-vars.yml to add the
        ``edxapp_comprehensive_theme_dir`` value::

            edxapp_comprehensive_theme_dir: '/full/path/to/my-theme'

    #.  Run the update script::

            $ sudo /edx/bin/update configuration master
            $ sudo /edx/bin/update edx-platform HEAD

#.  Otherwise, edit the /edx/app/edxapp/lms.yml file to add the
    ``COMPREHENSIVE_THEME_DIRS`` value::

        "COMPREHENSIVE_THEME_DIRS": ["/full/path/to/my-theme"],

Restart your site.  Your changes should now be visible.