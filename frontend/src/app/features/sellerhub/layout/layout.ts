import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'layout',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './layout.html',
  styleUrl: './layout.scss'
})
export class SellerHubLayoutComponent {
  private authService = inject(AuthService);

  navSections = [
    {  
      items: [
        { path: 'dashboard', label: 'Bảng điều khiển', icon: 'bi bi-grid' },
        { path: 'sellproduct', label: 'Đăng sản phẩm', icon: 'bi bi-plus-circle-fill' },
        { path: 'category-manage', label: 'Quản lí kho hàng', icon: 'bi bi-boxes' }
       
      ]
    
    },
    {
      items: [
         { path: 'Home', label: 'Quay lại trang chủ', icon: 'bi bi-house-door-fill' }
      ]
    }

   
  ];

  constructor(private router: Router) {}

  logout() {
    this.authService.logout();
  }
}
