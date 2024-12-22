FROM node:23-alpine AS builder

WORKDIR /build
ADD package* ./
RUN npm install
ADD ./src /build/src
ADD ./static /build/static
ADD *.json *.ts *.js /build/
ADD .svelte-kit /build/
RUN npm run build
ENTRYPOINT ["sh", "-o", "vi"]

FROM node:23-alpine

WORKDIR /work
COPY package* ./
RUN npm ci --omit dev
COPY --from=builder /build/build /work/build
ENTRYPOINT ["node", "build"]
