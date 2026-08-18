# using multi stage build
# build
FROM node:20-alpine AS build

WORKDIR /usr/src/app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ .

RUN npm run build


# serving the content
FROM nginx:alpine AS serve

COPY --from=build /usr/src/app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
