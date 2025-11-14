FROM node:20.11.0-bookworm-slim as builder

WORKDIR /widget

ADD package.json package-lock.json tsconfig.json ./

RUN --mount=type=secret,id=npmrc,target=/widget/.npmrc npm ci --include=dev

COPY src src
COPY public public
ADD config-overrides.js .

RUN npm run build

FROM nginx:1.25.0-alpine3.17
COPY --from=builder /widget/build /usr/share/nginx/html
ADD assets/nginx/default.conf /etc/nginx/conf.d
