import { Routes } from '@angular/router';

export const adminRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/admin-layout').then(m => m.AdminLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./dashboard/dashboard').then(m => m.AdminDashboardComponent)
      },
      {
        path: 'user-manage',
        loadComponent: () => import('./user-manage/user-manage').then(m => m.UserManageComponent)
      },
      {
        path: 'category-manage',
        loadComponent: () => import('./category-manage/category-manage').then(m => m.CategoryManageComponent)
      },
      {
        path: 'feedback-manage',
        loadComponent: () => import('./feedback-manage/feedback-manage').then(m => m.FeedbackManageComponent)
      }
    ]
  }
];