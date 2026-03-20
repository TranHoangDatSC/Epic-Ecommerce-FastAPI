import { Component, inject } from '@angular/core';
import { AsyncPipe, CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { CartService } from '../../../core/services/cart.service';
import { AuthService } from '../../../core/services/auth.service';
import { map } from 'rxjs/operators';
import { FormsModule } from '@angular/forms';
import { CartItem } from '../../../core/services/cart.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterLink, FormsModule, AsyncPipe],
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
            <li class="nav-item">
              <a class="nav-link d-flex align-items-center" routerLink="/customer/cart">
                <i class="bi bi-cart3 me-1"></i>
                Cart
                <span class="badge rounded-pill bg-danger border border-light ms-1" *ngIf="(cartCount$ | async) !== 0">
                  {{ cartCount$ | async }}
                </span>
              </a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'CUSTOMER'">
              <a class="nav-link" routerLink="/customer/profile">Profile</a>
            </li>
            <!-- Seller Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/dashboard">Dashboard</a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/inventory">Inventory</a>
            </li>
            <!-- Admin Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/user-manage">Users</a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/category-manage">Categories</a>
            </li>
            <!-- Moderator Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'MODERATOR'">
              <a class="nav-link" routerLink="/moderator/dashboard">Dashboard</a>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item" *ngIf="!isLoggedIn()">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#loginModal">Login</a>
            </li>
            <li class="nav-item" *ngIf="!isLoggedIn()">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#registerModal">Register</a>
            </li>
            <li class="nav-item dropdown" *ngIf="isLoggedIn()">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                {{ user()?.full_name || 'My Account' }}
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" routerLink="/customer/profile">Profile</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" (click)="logout()">Logout</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    
    <!-- Login Modal (Moved inside component for easier state access) -->
    <div class="modal fade" id="loginModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content text-dark">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Login with Gmail</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" id="closeLoginModal"></button>
          </div>
          <div class="modal-body">
            <form (ngSubmit)="login()">
              <div class="mb-3 text-start">
                <label for="loginEmail" class="form-label">Gmail Address</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                  <input type="email" class="form-control" id="loginEmail" name="email" [(ngModel)]="email" required placeholder="example@gmail.com">
                </div>
              </div>
              <div class="mb-3 text-start">
                <label for="loginPassword" class="form-label">Password</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-lock"></i></span>
                  <input type="password" class="form-control" id="loginPassword" name="password" [(ngModel)]="password" required>
                </div>
              </div>
              <button type="submit" class="btn btn-primary w-100 py-2 shadow-sm fw-bold">Login</button>
            </form>
          </div>
        </div>
      </div>
    </div>
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
  private cartService = inject(CartService);
  private authService = inject(AuthService);
  
  isLoggedIn = this.authService.isLoggedIn;
  user = this.authService.currentUser;

  email = '';
  password = '';

  cartCount$ = this.cartService.cartItems$.pipe(
    map((items: CartItem[]) => items.reduce((acc: number, item: CartItem) => acc + item.quantity, 0))
  );

  login() {
    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        document.getElementById('closeLoginModal')?.click();
        this.email = '';
        this.password = '';
      },
      error: (err: any) => {
        alert(err.error?.detail || 'Login failed');
      }
    });
  }

  logout() {
    this.authService.logout();
  }
}
