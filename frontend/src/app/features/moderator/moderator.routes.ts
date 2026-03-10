import { Routes } from '@angular/router';

export const moderatorRoutes: Routes = [
  {
    path: 'product-check',
    loadComponent: () => import('./product-check/product-check').then(m => m.ProductCheckComponent)
  }
];