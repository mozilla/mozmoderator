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

## CI & CD

This application is currently run through integration and deploy pipelines via both [GitHub Actions](https://github.com/mozilla/mozmoderator/actions/workflows/ci.yaml) & a background Kubernetes [Flux](https://fluxcd.io/) & [Kustomize](https://kustomize.io/) setup.

Through those workflows, a Docker image is built, tagged (based on the latest git commit SHA), pushed to ECR, and deployed either to a staging or production environment in our k8s-apps-prod-us-west-2 Kubernetes cluster. 

The pipelines work as followed:

CI & Docker Builds:
1. (manual) create your feature branch on this repository & add your work;
2. (manual) push your feature branch up to GitHub;
3. (automated) upon push, GitHub Actions will:
    a. run linting & syntax checks on the code;
    b. build the Docker image & tag it with the short git commit SHA of the latest commit;
    c. push that Docker image to our ECR repository for Moderator (this may be removed from the non-master branch commits, fyi);
4. (manual) create a PR from your feature branch to the master branch, have it reviewed, then merged into master;
5. (automated) Upon merge into master, GitHub Actions will:
    a. run linting & syntax checks on the code;
    b. build the Docker image & tag it with the short git commit SHA of the latest commit;
    c. push that Docker image to our ECR repository for Moderator;

Stage Deploy:
6. (manual) pull the Docker image from step 5 down, test locally as desired, & when ready to deploy to stage, edit kubernetes/stage/deployment.yaml#21, only replacing that docker image tag with the tag for the image from step 5.
7. (manual) push the work from step 6 up & create a PR into master;
8. (automated): upon push & PR, GitHub Actions will:
    a. run linting & syntax checks on the code;
    b. build yet another Docker image & tag it with the short git commit SHA of the latest commit (just ignore this for k8s deployment purposes);
    c. push that Docker image to our ECR repository for Moderator (again, just ignore this for k8s deployment purposes);
9. (manual): review the PR, approve/edit, & merge into master.
10. (automated): upon merge into master, GHA will do all of the above, _and_ Flux will:
    a. Apply the manifests found in the kubernetes/ directory;
    b. as there will be a change in those manifests for the stage application (our new docker image tag), kubernetes will pull that image down and redeploy the application.

Production Deploy:
6. (manual) test / QA the stage deploy as desired, & when ready to deploy to stage, edit kubernetes/prod/deployment.yaml#21, only replacing that docker image tag with the tag for the image from the stage deployment.
7. (manual) push the work from step 6 up & create a PR into master;
8. (automated): upon push & PR, GitHub Actions will:
    a. run linting & syntax checks on the code;
    b. build yet another Docker image & tag it with the short git commit SHA of the latest commit (just ignore this for k8s deployment purposes);
    c. push that Docker image to our ECR repository for Moderator (again, just ignore this for k8s deployment purposes);
9. (manual): review the PR, approve/edit, & merge into master.
10. (automated): upon merge into master, GHA will do all of the above, _and_ Flux will:
    a. Apply the manifests found in the kubernetes/ directory;
    b. as there will be a change in those manifests for the production application, (our new docker image tag), kubernetes will pull that image down and redeploy the application.
