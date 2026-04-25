# Stage 1: Build Angular
FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build --configuration=production

# Stage 2: Chạy bằng Nginx
FROM nginx:alpine
# Copy file build từ stage 1 vào thư mục nginx
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
# Copy file cấu hình nginx (để xử lý lỗi 404 khi reload trang trong SPA)
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 80