var gulp = require('gulp');
var mainBowerFiles = require('gulp-main-bower-files');
var uglify = require('gulp-uglify');
var cleanCSS = require('gulp-clean-css');
var gulpFilter = require('gulp-filter');

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
});
