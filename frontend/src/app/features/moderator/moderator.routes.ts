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
        loadComponent: () => import('./dashboard/moderator-dashboard').then(m => m.ModeratorDashboardComponent)
      }
    ]
  }
];
