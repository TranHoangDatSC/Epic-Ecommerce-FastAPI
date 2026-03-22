import { Routes } from '@angular/router';
import { adminGuard, guestGuard, authGuard } from './core/guards/auth.guard'; // Thêm authGuard vào đây

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', loadComponent: () => import('./features/home/home').then(m => m.HomeComponent) },
  { path: 'shop', loadComponent: () => import('./features/shop/shop').then(m => m.ShopComponent) },
  { path: 'shop/product/:id', loadComponent: () => import('./features/shop/product-detail/product-detail.component').then(m => m.ProductDetailComponent) },
  
  // Nhóm Auth
  { 
    path: 'auth', 
    canActivate: [guestGuard], 
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.authRoutes) 
  },
  
  // Nhóm User/Customer
  { 
    path: 'customer', 
    canActivate: [authGuard], 
    loadChildren: () => import('./features/customer/customer.routes').then(m => m.customerRoutes) 
  },
  
  // Nhóm Admin
  { 
    path: 'admin', 
    canActivate: [adminGuard], 
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.adminRoutes) 
  },

  { path: 'contact', loadComponent: () => import('./features/contact/contact').then((m) => m.ContactComponent) },
  { path: '**', redirectTo: '/home' }
];