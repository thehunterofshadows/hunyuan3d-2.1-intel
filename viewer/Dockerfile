FROM node:22-alpine AS deps
WORKDIR /deps
COPY viewer/package*.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
FROM nginx:alpine
COPY viewer/nginx.conf /etc/nginx/conf.d/default.conf
COPY viewer/site /usr/share/nginx/html
COPY --from=deps /deps/node_modules/three /usr/share/nginx/html/vendor/three
COPY assets/intel-bumper /usr/share/nginx/html/models/bumper
COPY assets/intel-railgun /usr/share/nginx/html/models/railgun
COPY assets/intel-woman /usr/share/nginx/html/models/woman
COPY assets/railgun-built /usr/share/nginx/html/models/railgun-built

COPY assets/trellis-railgun /usr/share/nginx/html/models/trellis-railgun
