FROM node:20-slim

ENV NODE_ENV=production
WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

COPY index.js ./

CMD ["node", "index.js"]
