import { Routes } from '@angular/router';

export const adminRoutes: Routes = [
  {
    path: '',
    redirectTo: 'user-manage',
    pathMatch: 'full'
  },
  {
    path: 'user-manage',
    loadComponent: () => import('./user-manage/user-manage').then(m => m.UserManageComponent)
  },
  {
    path: 'category-manage',
    loadComponent: () => import('./category-manage/category-manage').then(m => m.CategoryManageComponent)
  }
];