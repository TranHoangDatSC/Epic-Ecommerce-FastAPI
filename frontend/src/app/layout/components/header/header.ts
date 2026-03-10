import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #F39C12;">
      <div class="container">
        <a class="navbar-brand" routerLink="/">Oldshop</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <a class="nav-link" routerLink="/home">Home</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" routerLink="/shop">Shop</a>
            </li>
            <!-- Customer Navigation -->
            <li class="nav-item" *ngIf="currentUser?.role === 'CUSTOMER'">
              <a class="nav-link" routerLink="/customer/cart">Cart</a>
            </li>
            <li class="nav-item" *ngIf="currentUser?.role === 'CUSTOMER'">
              <a class="nav-link" routerLink="/customer/profile">Profile</a>
            </li>
            <!-- Seller Navigation -->
            <li class="nav-item" *ngIf="currentUser?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/dashboard">Dashboard</a>
            </li>
            <li class="nav-item" *ngIf="currentUser?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/inventory">Inventory</a>
            </li>
            <!-- Admin Navigation -->
            <li class="nav-item" *ngIf="currentUser?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/user-manage">Users</a>
            </li>
            <li class="nav-item" *ngIf="currentUser?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/category-manage">Categories</a>
            </li>
            <!-- Moderator Navigation -->
            <li class="nav-item" *ngIf="currentUser?.role === 'MODERATOR'">
              <a class="nav-link" routerLink="/moderator/product-check">Product Check</a>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item" *ngIf="!currentUser">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#loginModal">Login</a>
            </li>
            <li class="nav-item" *ngIf="!currentUser">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#registerModal">Register</a>
            </li>
            <li class="nav-item dropdown" *ngIf="currentUser">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                {{ currentUser.firstName }} {{ currentUser.lastName }}
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" routerLink="/customer/profile" *ngIf="currentUser.role === 'CUSTOMER'">Profile</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" (click)="logout()">Logout</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  `,
  styles: [`
    .navbar-brand {
      font-weight: bold;
      font-size: 1.5rem;
    }
    .nav-link {
      font-weight: 500;
    }
  `]
})
export class HeaderComponent {
  currentUser: any = null; // TODO: Inject auth service

  logout() {
    // TODO: Implement logout logic
  }
}
