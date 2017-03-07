/* global require */

var gulp = require('gulp');
var mainBowerFiles = require('gulp-main-bower-files');
var uglify = require('gulp-uglify');
var cleanCSS = require('gulp-clean-css');
var gulpFilter = require('gulp-filter');
var eslint = require('gulp-eslint');
var stylelint = require('gulp-stylelint');

var lintPathsJS = [
    'moderator/moderate/static/js/*.js',
    'gulpfile.js'
];

var lintPathsCSS = [
    'moderator/moderate/static/css/*.css'
];

gulp.task('js:lint', () => {
    return gulp.src(lintPathsJS)
        .pipe(eslint())
        .pipe(eslint.format())
        .pipe(eslint.failAfterError());
});

gulp.task('css:lint', () => {
    return gulp.src(lintPathsCSS)
        .pipe(stylelint({
            reporters: [{ formatter: 'string', console: true}]
        }));
});

gulp.task('bower', function(){
    var filterJS = gulpFilter('**/*.js', { restore: true });
    var filterCSS = gulpFilter('**/*.css', { restore: true });
    return gulp.src('./bower.json')
        .pipe(mainBowerFiles())
        .pipe(filterJS)
        .pipe(uglify())
        .pipe(filterJS.restore)
        .pipe(filterCSS)
        .pipe(cleanCSS())
        .pipe(filterCSS.restore)
        .pipe(gulp.dest('./moderator/moderate/static/lib'));
});

gulp.task('default', function() {
    gulp.start('bower');
    gulp.start('js:lint');
    gulp.start('css:lint');
});
