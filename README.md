# Mozilla Moderator

Mozilla Moderator is a panel moderation webapp that enables users to view, vote and ask questions on different events.

Then panel moderators can export the questions and use them during panel discussions and Q&A.

## License

All mozmoderator source files are made available under the terms of the GNU Affero General Public License (AGPL).

## Frontend testing

Use [npm](https://www.npmjs.com/) to install the necessary tools. If you use [docker](https://docker.com/) for development this step is not necessary.

    npm -g install yarn gulp-cli

Use [yarn](https://yarnpkg.com/) to download all required packages and frontend libraries.

    yarn

Use [gulp](http://gulpjs.com/) to check in all used assets and run the tests.

    gulp

Or run just the tests.

    gulp test
