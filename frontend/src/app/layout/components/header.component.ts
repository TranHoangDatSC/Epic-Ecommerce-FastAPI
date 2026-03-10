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
                  <a class="nav-link" routerLink="/home" routerLinkActive="active">Home</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" routerLink="/shop" routerLinkActive="active">Shop</a>
                </li>
                <!-- Customer navigation -->
                <li class="nav-item" *ngIf="userRole === 'CUSTOMER'">
                  <a class="nav-link" routerLink="/customer/cart" routerLinkActive="active">Cart</a>
                </li>
                <li class="nav-item" *ngIf="userRole === 'CUSTOMER'">
                  <a class="nav-link" routerLink="/customer/profile" routerLinkActive="active">Profile</a>
                </li>
                <!-- Seller navigation -->
                <li class="nav-item" *ngIf="userRole === 'SELLER'">
                  <a class="nav-link" routerLink="/seller/dashboard" routerLinkActive="active">My Store</a>
                </li>
                <!-- Admin/Mod navigation -->
                <li class="nav-item" *ngIf="userRole === 'ADMIN' || userRole === 'MOD'">
                  <a class="nav-link" routerLink="/admin" routerLinkActive="active">Admin Panel</a>
                </li>
              </ul>
            </nav>
          </div>
          <div class="d-flex align-items-center">
            <button class="btn btn-outline-light me-2" *ngIf="!isLoggedIn" (click)="openLoginModal()">Login</button>
            <button class="btn btn-success" *ngIf="!isLoggedIn" (click)="openRegisterModal()">Register</button>
            <button class="btn btn-outline-light" *ngIf="isLoggedIn" (click)="logout()">Logout</button>
          </div>
        </div>
      </div>
    </header>
  `,
  styles: [`
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

  openLoginModal() {
    // TODO: Implement modal opening
  }

  openRegisterModal() {
    // TODO: Implement modal opening
  }

  logout() {
    // TODO: Implement logout
  }
}