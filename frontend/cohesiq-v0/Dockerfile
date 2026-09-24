# ──────────────────────────────────────────────
# Development Dockerfile — cohesiq-v0 (Next.js 16)
# ──────────────────────────────────────────────

# Node 22 matches @types/node ^22 in package.json
FROM node:22-alpine

# Install pnpm globally (pinned to v9 for stable Docker builds)
# Use npm to avoid corepack network issues inside minimal images
RUN npm install -g pnpm@9

WORKDIR /app

# Copy package manifests first for better layer caching.
# Dependencies are reinstalled only when these files change.
COPY package.json pnpm-lock.yaml ./

# Allow sharp to run its native build scripts
RUN pnpm config set onlyBuiltDependencies '["sharp"]'

# Install all dependencies (including devDependencies needed for dev server)
RUN pnpm install --frozen-lockfile

# Copy the rest of the source
# Note: in docker-compose dev mode, the volume mount overrides this,
# but it ensures the image is self-contained for standalone builds.
COPY . .

EXPOSE 3000

# docker-compose overrides this with `pnpm dev`
CMD ["pnpm", "dev"]
