import { Routes } from '@angular/router';

export const customerRoutes: Routes = [
  {
    path: 'cart',
    loadComponent: () => import('./cart/cart').then(m => m.CartComponent)
  },
  {
    path: 'checkout',
    loadComponent: () => import('./checkout/checkout').then(m => m.CheckoutComponent)
  },
  {
    path: 'profile',
    loadComponent: () => import('./profile/profile').then(m => m.ProfileComponent)
  }
];