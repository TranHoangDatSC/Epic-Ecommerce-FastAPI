import { Routes } from '@angular/router';

export const sellerhubRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/layout').then(m => m.SellerHubLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./dashboard/dashboard').then(m => m.SellerHubDashboardComponent)
      },

      {
        path: 'sellproduct',
        loadComponent: () => import('./sellproduct/sellproduct').then(m => m.PostProductComponent)
      },
      {
        path: 'category-manage',
        loadComponent: () => import('./category-manage/category-manage').then(m => m.CategoryManageComponent)
      }
   
    ]
  }
];