import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http'; // Thêm withInterceptors vào đây
import { authInterceptor } from './core/interceptors/auth.interceptor'; // Import đúng đường dẫn file interceptor
import { APP_INITIALIZER } from '@angular/core';
import { AuthService } from './core/services/auth.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    {
      provide: APP_INITIALIZER,
      useFactory: (authService: AuthService) => () => {
        // Trả về Promise đợi cho đến khi authService đã check xong
        return new Promise((resolve) => {
          // Logic đợi cho đến khi isInitialized là true
          const interval = setInterval(() => {
            if (authService.isInitialized()) {
              clearInterval(interval);
              resolve(true);
            }
          }, 50);
        });
      },
      deps: [AuthService],
      multi: true
    }
  ]
};
