import { Routes } from '@angular/router';

export const moderatorRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/moderator-layout').then(m => m.ModeratorLayoutComponent),
    children: [
      {
        path: '',
        redirectTo: 'dashboard',
        pathMatch: 'full'
      },
      {
        path: 'dashboard',
        loadComponent: () => import('./dashboard/dashboard').then(m => m.ModeratorDashboardComponent)
      },
      {
        path: 'product-check',
        loadComponent: () => import('./product-check/product-check').then(m => m.ProductCheckComponent)
      },
      {
        path: 'rejected-products',
        loadComponent: () => import('./rejected-products/rejected-products').then(m => m.RejectedProductsComponent)
      },
      {
        path: 'archived-products',
        loadComponent: () => import('./archived-products/archived-products').then(m => m.ArchivedProductsComponent)
      },
      {
        path: 'violation-report',
        loadComponent: () => import('./violation-report/violation-report').then(m => m.ViolationReportComponent)
      },
      {
        path: 'processing-history',
        loadComponent: () => import('./processing-history/processing-history').then(m => m.ProcessingHistoryComponent)
      },
      {
        path: 'seller-appeals',
        loadComponent: () => import('./seller-appeals/seller-appeals').then(m => m.SellerAppealsComponent)
      },
      {
        path: 'unlock',
        loadComponent: () => import('./unlock-account/unlock-account').then(m => m.UnlockAccountComponent)
      },
      {
        path: 'unlock/:userId',
        loadComponent: () => import('./unlock-account/unlock-account').then(m => m.UnlockAccountComponent)
      }
    ]
  }
];