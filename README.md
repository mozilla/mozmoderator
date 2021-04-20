# Mozilla Moderator

[![Code CI](https://github.com/mozilla/mozmoderator/actions/workflows/ci.yaml/badge.svg)](https://github.com/mozilla/mozmoderator/actions/workflows/ci.yaml)

Mozilla Moderator is a panel moderation webapp that enables users to view, vote and ask questions on different events.

Then panel moderators can export the questions and use them during panel discussions and Q&A.

## License

All mozmoderator source files are made available under the terms of the GNU Affero General Public License (AGPL).

## Frontend testing

Use [npm](https://www.npmjs.com/) to install the necessary tools. If you use [docker](https://docker.com/) for development this step is not necessary.

    npm -g install bower gulp-cli

Use [bower](https://bower.io/) to download all Frontend libraries.

    bower install

Install all required packages.

    npm install

Finally use [gulp](http://gulpjs.com/) to check in all main static files and run the tests.

    gulp
