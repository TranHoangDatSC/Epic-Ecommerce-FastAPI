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

  const isAuthenticated = authService.isAuthenticated();
  const role = authService.getUserRole();

  console.log('[adminGuard] role from getUserRole():', role);

  if (isAuthenticated && Number(role) === 1) {
    return true;
  }

  console.warn('[adminGuard] access denied. role:', role);
  router.navigate(['/home']);
  return false;
};

export const moderatorGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const isAuthenticated = authService.isAuthenticated();
  const role = Number(authService.getUserRole());

  if (!isAuthenticated) {
    router.navigate(['/auth/login']);
    return false;
  }

  if (role === 1 || role === 2) {
    return true;
  }

  alert('Bạn không có quyền truy cập trang moderator.');
  router.navigate(['/home']);
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