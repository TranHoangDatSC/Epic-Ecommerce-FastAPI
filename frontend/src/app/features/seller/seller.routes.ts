import { Routes } from '@angular/router';

export const sellerRoutes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard').then(m => m.DashboardComponent)
  },
  {
    path: 'inventory',
    loadComponent: () => import('./inventory/inventory').then(m => m.InventoryComponent)
  },
  {
    path: 'inventory/add',
    loadComponent: () => import('./inventory/add-product/add-product.component').then(m => m.AddProductComponent)
  }
];