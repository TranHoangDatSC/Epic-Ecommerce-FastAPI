import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }
  router.navigate(['/auth/login']);
  return false;
};

// src/app/core/guards/auth.guard.ts
export const adminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const role = authService.getUserRole();
  const isAuthenticated = authService.isAuthenticated();
  console.log('[Guard] Role check:', role);

  if (isAuthenticated && role === 1) {
    return true;
  }
  console.warn('Truy cập bị chặn: Không phải Admin!');
  router.navigate(['/auth/login']); 
  return false;
};

export const guestGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  const role = authService.getUserRole();

  if (authService.isAuthenticated()) {
    if (Number(role) === 1) {
      router.navigate(['/admin/dashboard']);
    } else {
      router.navigate(['/home']);
    }
    return false;
  }
  return true;
};