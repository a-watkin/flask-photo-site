# Flask photo site

## General overview

A photo site made using the Flask and React, this was made as a replacement site for a Flickr user.

SQLite3 was used as a database and I decided against an ORM because I wanted to practice writing some SQL.

The database schema was dictated partly by how Flickr stores data as the data source was from the Flickr API.

The basic functionality of Flickr has been implimented without the social aspects. This was at the request of the end user.

## Features and further information

I used React for parts of the site where one of more things are selected. For example selecting photos to add to an album or selecting an album to place newly uploaded photos into.

I also implenented my own tag system that allows for tags with spaces and most special characters. Special characters are encoded for urls and made human readable for the end user.

Exif data is captured and stored but as of yet this is used only for the date the photo was taken.

Multiple images can be uploaded which are correctly orientated, resized and stored by year and month on the file system.

Bootstrap-filestyle was used for styling the buttons and input on the upload page.

Image previews are 300x300.

A login system exists but it is not intended for general registration and is purposfully limited.

For styling I used bootstrap 4 and some minimal CSS which I will hopefully be improving later.

The site is deployed on Ubuntu 16 using Gunicorn and Nginx.

## Live example

[See the live version of this site](https://www.photography-by-eigi.com/)

## Using

1. Flask
2. React
3. SQLite
4. Bootstrap-filestyle
5. jQuery
6. Ubuntu
7. Guincorn
8. Nginx
