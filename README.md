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

## Development with Docker

After cloning this repo, you need to create an .env file. Make a copy of .env-dist named .env.

    cp .env-dist .env

Now docker compose from the root directory of the repo

    docker compose up

Since this is Django, you will need to create a superuser for your dev work. Do this by attaching to the web container and running the command.

    docker compose exec web bash
    ./manage.py createsuperuser

You should now be able to login at /admin/

## CI & CD

This application is currently run through integration and deploy pipelines via both [GitHub Actions](https://github.com/mozilla/mozmoderator/actions/workflows/ci.yaml) & a background Kubernetes [Flux](https://fluxcd.io/) setup leveraging [Helm Charts](github.com/mozilla-it/helm-charts/).

Through those workflows, a Docker image is built, tagged, pushed to ECR, and deployed either to a staging [(itse-apps-stage-1)](https://github.com/mozilla-it/itse-apps-stage-1-infra/) or production [(itse-apps-prod-1)](https://github.com/mozilla-it/itse-apps-prod-1-infra/) Kubernetes cluster.

tl;dr: Push commits to main branch for a stage deploy, cut GitHub releases (following v1.2.3 format) for a production deploy.

### The pipelines work as followed:

#### CI & Docker Builds:

1. (manual) create your feature branch on this repository or a fork (_CI will run in our repository for PRs from forks now_) & add your work;
2. (manual) push your feature branch up to GitHub & create your PR;
3. (automated) upon push (if a branch off this repository) or PR (both our repository & forks), GitHub Actions will:
    - run linting & syntax checks on the code;
    - build the Docker image & tag it with the short git commit SHA of the latest commit to confirm the image can be built;
4. (manual) create a PR from your feature branch to the main branch, have it reviewed, then merged into main;
5. (automated) Upon merge into main, GitHub Actions will:
    - run linting & syntax checks on the code;
    - build the Docker image & tag it with "stg-{the 7-digit short git commit SHA of the latest commit};
    - push that Docker image & tag to our ECR repository for Moderator;

#### Stage Deploy:

6. (automated): upon creation & push of any Docker Images to our ECR moderator repository with the tag pattern `^(stg-[a-f0-9]{7})$`:
    - Flux will update our [Stage Helm Release of the Moderator Helm Chart](https://github.com/mozilla-it/itse-apps-stage-1-infra/blob/main/k8s/releases/moderator/moderator.yaml) with that new Stage image tag;
    - Flux will rollout that release;
    - Flux will update [Stage Helm Release of the Moderator Helm Chart](https://github.com/mozilla-it/itse-apps-stage-1-infra/blob/main/k8s/releases/moderator/moderator.yaml) with a git commit & the latest image changes upon successful deploy.

#### Production Deploy:

7. (manual) test / QA the stage deploy as desired (moderator.allizom.org).
8. (manual) Create a GitHub Release off of the main branch with appropriate semver updating (using the pattern `^(v[0-9]+.[0-9]+.[0-9]+)$`);
9. (automated): upon Release, GitHub Actions will:
    - run linting & syntax checks on the code;
    - pull the docker image of the latest commit in that release & tag that image with the release version;
    - push that Docker image with release tag to our ECR repository for Moderator;
10. (automated): upon creation & push of any Docker Images to our ECR moderator repository with the tag pattern `^(v[0-9]+.[0-9]+.[0-9]+)$`:
    - Flux will update our [Prod Helm Release of the Moderator Helm Chart](https://github.com/mozilla-it/itse-apps-prod-1-infra/blob/main/k8s/releases/moderator/moderator.yaml) with that new release tag;
    - Flux will rollout that release;
    - Flux will update [Prod Helm Release of the Moderator Helm Chart](https://github.com/mozilla-it/itse-apps-prod-1-infra/blob/main/k8s/releases/moderator/moderator.yaml) with a git commit & the latest image changes upon successful deploy.
