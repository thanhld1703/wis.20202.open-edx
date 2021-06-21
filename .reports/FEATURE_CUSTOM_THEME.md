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
            ├── index.html
            └── header.html
Our theme structure is developed from the recommended theme structure from the original edX repository.

## Images
Images is substituted simply by placing the new image at the right place
in the theme directory  lms/static/images/logo.png then, the image is overridden.
We also provide an addition to the LMS home page by adding a background image for the Welcome To Site component in the LMS landing page as well as changing the favicon.icon file for the header of our custom theme.

## Sass/CSS
In order to override the default style of the project, we need to mirror the scss files containing the custom style of our theme with the original scss files in LMS, these files are all desinated in static/sass directories, however, some of them are held in sub-folders of the sass folder, hence we also need to recreate those folder in order to successfully override the needed scss (elements, multicourse, search, shared, views).

### For the creation of our two themes, we follow these steps to change the color of edX sites:
- First we change the $primary variable in the \_variables.scss file, this will be able to affect most of the website component's color. However, some element's color will remains unchanged since they are not set with respect to the primary color but with other variables that have fixed value.
- Because of that, to manually change these componenent's color to our desire value, we created a seperated file \_override-colors.scss. In this file, we will redefind various color variables that were set with a fixed value to be set with a value created from the primary color by using saturate() or lighten() function. After this step, the only components that we still can't changed yet is the ones having their color set directly with a fixed value in the code. 
- Finally, in order to change these components, we need to search for their names in the original LMS folder, then, we will have to mirror the files responsible for the styling of these components (same folder structure also) and write the overriding part to success fully change the style of said components.

## HTML Templates
As can be seen from the theme structure, our theme changed 4 html files each for a different reason:
- header.html: changing the header content
- main.html: fixing the title of website (original title failed to get the platform name)
- index.html: adding the background image to the Welcome to Site div
- footer.html: changing footer style, adding social links, fixing logo import 


## Theme instalation
//TODO
