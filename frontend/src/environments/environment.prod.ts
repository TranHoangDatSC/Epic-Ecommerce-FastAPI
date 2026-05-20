export const environment = {
  production: true,
  apiUrl: '/api/v1',              // Nginx proxy /api/ → backend:8000
  imageBaseUrl: '',               // Chuỗi rỗng = dùng origin hiện tại, nginx proxy /media/ → backend
  imageUrl: '',
  googleScriptContact: ''
};