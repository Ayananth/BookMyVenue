FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL
ARG VITE_API_BASE_URL
ARG VITE_GOOGLE_CLIENT_ID

RUN npm run build
