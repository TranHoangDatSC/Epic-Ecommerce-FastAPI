import { Routes } from '@angular/router';
import { AuthGuard } from '../../core/guards/auth.guard';

export const customerRoutes: Routes = [
  {
    path: 'cart',
    loadComponent: () => import('./cart/cart').then(m => m.CartComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'checkout',
    loadComponent: () => import('./checkout/checkout').then(m => m.CheckoutComponent),
    canActivate: [AuthGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./profile/profile').then(m => m.ProfileComponent),
    canActivate: [AuthGuard]
  }
];