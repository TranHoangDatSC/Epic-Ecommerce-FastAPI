import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <header class="bg-primary text-white py-3">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <h1 class="h4 mb-0 me-4">Oldshop Ecommerce</h1>
            <nav class="navbar navbar-expand-lg navbar-dark p-0">
              <ul class="navbar-nav">
                <li class="nav-item">
                  <a class="nav-link" routerLink="/home" routerLinkActive="active">Trang chủ</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" routerLink="/shop" routerLinkActive="active">Cửa hàng</a>
                </li>
                <!-- Customer navigation -->
                <li class="nav-item" *ngIf="userRole === 'CUSTOMER'">
                  <a class="nav-link" routerLink="/customer/cart" routerLinkActive="active">Giỏ hàng</a>
                </li>
                <li class="nav-item" *ngIf="userRole === 'CUSTOMER'">
                  <a class="nav-link" routerLink="/customer/profile" routerLinkActive="active">Thông tin cá nhân</a>
                </li>
                <!-- Seller navigation -->
                <li class="nav-item" *ngIf="userRole === 'SELLER'">
                  <a class="nav-link" routerLink="/seller/dashboard" routerLinkActive="active">Cửa hàng của tôi</a>
                </li>
                <!-- Admin/Mod navigation -->
                <li class="nav-item" *ngIf="userRole === 'ADMIN' || userRole === 'MOD'">
                  <a class="nav-link" routerLink="/admin" routerLinkActive="active">Quản trị viên</a>
                </li>
              </ul>
            </nav>
          </div>
          <div class="d-flex align-items-center">
            <button class="btn btn-outline-light me-2" *ngIf="!isLoggedIn" data-bs-toggle="modal" data-bs-target="#loginModal">Đăng nhập</button>
            <button class="btn btn-success" *ngIf="!isLoggedIn" data-bs-toggle="modal" data-bs-target="#registerModal">Đăng ký</button>
            <button class="btn btn-outline-light" *ngIf="isLoggedIn" (click)="logout()">Đăng xuất</button>
          </div>
        </div>
      </div>
    </header>
  `,
  styles: [`
    header {
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    .bg-primary {
      background-color: #F39C12 !important;
    }

    .navbar-nav .nav-link.active {
      font-weight: bold;
    }
  `]
})
export class HeaderComponent {
  userRole: string | null = 'CUSTOMER'; // This should come from auth service
  isLoggedIn: boolean = false; // This should come from auth service

  logout() {
    // TODO: Implement logout
  }
}