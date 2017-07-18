/* global require */

var gulp = require('gulp');
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

gulp.task('assets', function(){
    var filterJS = gulpFilter('**/*.js', { restore: true });
    var filterCSS = gulpFilter('**/*.css', { restore: true });
    var p = require('./package.json');
    var assets = p.assets;
    return gulp.src(assets, {cwd : 'node_modules/**'})
        .pipe(filterJS)
        .pipe(uglify())
        .pipe(filterJS.restore)
        .pipe(filterCSS)
        .pipe(cleanCSS({rebase: false}))
        .pipe(filterCSS.restore)
        .pipe(gulp.dest('./moderator/moderate/static/lib'));
});

gulp.task('test', () => {
    gulp.start('js:lint');
    gulp.start('css:lint');
});

gulp.task('default', function() {
    gulp.start('assets');
    gulp.start('test');
});
