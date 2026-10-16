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
COPY assets/trellis-railgun-ultra /usr/share/nginx/html/models/trellis-railgun-ultra

COPY assets/trellis-bumper /usr/share/nginx/html/models/trellis-bumper

COPY assets/trellis-woman /usr/share/nginx/html/models/trellis-woman

COPY assets/portable-pinball /usr/share/nginx/html/models/portable-pinball
COPY assets/trellis-pinball-flipper /usr/share/nginx/html/models/trellis-pinball-flipper
COPY assets/trellis-pinball-plunger /usr/share/nginx/html/models/trellis-pinball-plunger
COPY assets/trellis-pinball-slingshot /usr/share/nginx/html/models/trellis-pinball-slingshot
COPY assets/trellis-pinball-target /usr/share/nginx/html/models/trellis-pinball-target
COPY assets/trellis-pinball-pop-bumper /usr/share/nginx/html/models/trellis-pinball-pop-bumper

# Content-based URLs keep model-list updates fresh even behind CDN browser TTL rules.
RUN cd /usr/share/nginx/html && \
    digest=$(sha256sum part-inspector.js | cut -c1-16); \
    cp part-inspector.js "part-inspector.$digest.js"; \
    sed -i "s|./part-inspector.js|./part-inspector.$digest.js|g" app.js; \
    for asset in app.js style.css; do \
      digest=$(sha256sum "$asset" | cut -c1-16); \
      name="${asset%.*}.$digest.${asset##*.}"; \
      cp "$asset" "$name"; \
      sed -i "s|/$asset[^\"]*|/$name|g" index.html; \
    done
