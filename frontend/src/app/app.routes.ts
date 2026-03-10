import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home').then(m => m.HomeComponent)
  },
  {
    path: 'shop',
    loadComponent: () => import('./features/shop/shop').then(m => m.ShopComponent)
  },
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.authRoutes)
  },
  {
    path: 'customer',
    loadChildren: () => import('./features/customer/customer.routes').then(m => m.customerRoutes)
  },
  {
    path: 'seller',
    loadChildren: () => import('./features/seller/seller.routes').then(m => m.sellerRoutes)
  },
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.adminRoutes)
  },
  {
    path: 'moderator',
    loadChildren: () => import('./features/moderator/moderator.routes').then(m => m.moderatorRoutes)
  },
  {
    path: '**',
    redirectTo: '/home'
  }
];
