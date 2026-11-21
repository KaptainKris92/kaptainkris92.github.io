# Builds the Jekyll site and serves it with nginx.
# Build context is the repo root (see docker-compose.yml).
FROM ruby:3.4-alpine AS build
RUN apk add --no-cache build-base
ENV BUNDLE_GEMFILE=/site/deploy/Gemfile JEKYLL_ENV=production
WORKDIR /site
COPY deploy/Gemfile deploy/Gemfile.lock deploy/
RUN bundle install
COPY . .
RUN bundle exec jekyll build --config _config.yml,deploy/_config.selfhost.yml -d /out

FROM nginx:1.30-alpine
LABEL app=kreations
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /out /usr/share/nginx/html
