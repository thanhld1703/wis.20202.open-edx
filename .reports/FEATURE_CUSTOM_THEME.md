# Explanation for the custom theme creation process:

## Theme structure:

    custom-theme
    └── lms
        ├── static
        │   ├── images
        │   │   └── logo.png
        |   |   └── favicon.icon
        |   |   └── backgroud.jpg
        │   └── sass
        │       ├── elements
        |       |   └── _controls-v1.scss
        |       ├── multicourse
        |       |   └── _course-v1.scss
        |       |   └── _dashboard-v1.scss
        |       |   └── _home-v1.scss
        |       ├── partials
        |       |   ├── lms
        |       |   |   ├── theme
        |       |   |   |   └── _variables.scss
        |       ├── search
        |       |   └── _search-v1.scss
        |       ├── shared
        |       |   └── _header-v1.scss
        |       ├── views
        |       |   └── _login-register-v1.scss
        │       ├── _override-colors.scss
        |       ├── _main-v1.scss
        │       └── lms-main-v1.scss
        └── templates
            ├── footer.html
            ├── main.html
            └── index.html
Our theme structure is developed from the recommended theme structure from the original edX repository.

## Images
Images is substituted simply by placing the new image at the right place
in the theme directory  lms/static/images/logo.png then, the image is overridden.
We also provide an addition to the LMS home page by adding a background image for the Welcome To Site component in the LMS landing page as well as changing the favicon.icon file for the header of our custom theme.

## Sass/CSS
In order to override the default style of the project, we need to mirror the scss files containing the custom style of our theme with the original scss files in LMS, these files are all desinated in static/sass directories, however, some of them are held in sub-folders of the sass folder, hence we also need to recreate those folder in order to successfully override the needed scss (elements, multicourse, search, shared, views).

### For the creation of our first custom theme Geeks for Geeks, we follow these steps:
- First we change the $primary variable in the \_variables.scss file, this will be able to affect most of the website component's color. However, some element's color will remains unchanged since they are not set with respect to the primary color but with other variables that have fixed value.
- Because of that, to manually change these componenent's color to our desire value, we created a seperated file \_override-colors.scss. In this file, we will redefind all the color variables used on our site that were set with a fixed value to be set with a value created from the primary color by using saturate() or lighten() function. After this step, the only components that we still can't changed yet is the ones having their color set directly with a fixed value in the code. 
- Finally, in order to change these components, we need to search for their names in the original LMS folder, then, we will have to mirror the files responsible for the styling of these components (same folder structure also) and write the overriding part to successfully change the style of said components.

### For the creation of our second theme Agile Academy:
#### Following the Geeks for Geeks theme creation approach, we created another theme called the "Agile Academy". 

- With the help of our \_override-colors.scss file, the creation of Agile Academy or any custom theme from now on become rather straight forward, just by changing the $primary variable in the \_variables.scss and $base-color in \_override-colors.scss should be able to change the color of almost all the website components since now all the color variables is dependent of the base color.  
- The remaining works is just to nitpicking the components that have not been successfully changed color and mirror the files responsible for their styling and write the override code to fully change their style. This works will also become very simple now since the Geeks for Geeks theme have provided almost all of the necessary files as well as structure that need to be changed and we only need to cover very few if any component.

## HTML Templates
The templates file we used to create our theme is cloned from edx.org theme and red-theme. 

However, we made some modifications to enable the dynamic data loading of the pages, including
- main.html: Change the code that dislay the Platform (Site) name, so it can retrieve the Platform Name from the Site 
  Configuration instead of hardcoded the name of the organization.
  ```python
   <h1>${_(HTML("Free courses from <strong>{org_name}</strong>")).format(org_name=configuration_helpers.get_value('PLATFORM_NAME', settings.PLATFORM_NAME))}</h1>  
  ```
- index.html: 
  - Change to archive same goal as main.html
  - Add the background image to the Welcome to Site area, helping it more attractive
- footer.html: 
  - Change to archive same goal as main.html.
  - Enhance footer style and fix bugs related to display Logo
  - Add dynamic social links that can be retrieved fully from the Site Configuration.
[Insert report about SOCIAL FOOTER here](FEATURE_SOCIAL-FOOTER.md)


## Theme installation
To deploy the themes onto the Docker stack, execute the following step in orders:
1. Copy the theme folder into the `edx-platform/themes` directory or `edx-themes/platform` directory
    ```bash
    cp -R /path/of/theme-name /hust-edutech/edx-platform/themes/theme-name
    cp -R /path/of/theme-name /hust-edutech/themes/edx-platform/theme-name
    ```
2. Tell the services to update static assets of the new theme by changing position to `devstack` directory and run the 
   following commands:
    ```bash
    make dev.static.lms && make lms-restart
    make dev.static.studio && make studio-restart  
    ```
3. To switch to the target theme, go to `<edx-host>:18000/admin/theming/sitetheme/` and edit the theme-dir-name of the 
corresponding site to the name of the theme folder.
