import { Component, inject } from '@angular/core';
import { AsyncPipe, CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
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
              <a class="nav-link d-flex align-items-center" routerLink="/home"><i class="bi bi-house-door me-1"></i>Trang chủ</a>
            </li>
            <li class="nav-item">
              <a class="nav-link d-flex align-items-center" routerLink="/shop"><i class="bi bi-bag me-1"></i>Cửa hàng</a>
            </li>
            <!-- Customer Navigation -->
            <li class="nav-item">
              <a class="nav-link d-flex align-items-center" href="#" (click)="goToCart($event)">
                <i class="bi bi-cart3 me-1"></i>
                Giỏ hàng
                <span class="badge rounded-pill bg-danger border border-light ms-1" *ngIf="(cartCount$ | async) !== 0">
                  {{ cartCount$ | async }}
                </span>
              </a>
            </li>
            <li class="nav-item">
              <a class="nav-link d-flex align-items-center" routerLink="/contact">
                <i class="bi bi-telephone me-1"></i>
                Liên hệ
              </a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'CUSTOMER'">
              <a class="nav-link" routerLink="/customer/profile">Thông tin cá nhân</a>
            </li>
            <!-- Seller Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/dashboard">Cửa hàng của tôi</a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'SELLER'">
              <a class="nav-link" routerLink="/seller/inventory">Quản lý sản phẩm</a>
            </li>
            <!-- Admin Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/user-manage">Quản lý người dùng</a>
            </li>
            <li class="nav-item" *ngIf="user()?.role === 'ADMIN'">
              <a class="nav-link" routerLink="/admin/category-manage">Quản lý danh mục</a>
            </li>
            <!-- Moderator Navigation -->
            <li class="nav-item" *ngIf="user()?.role === 'MODERATOR'">
              <a class="nav-link" routerLink="/moderator/dashboard">Dashboard</a>
            </li>
          </ul>
          <ul class="navbar-nav">
            <li class="nav-item" *ngIf="!isLoggedIn()">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#loginModal">Đăng nhập</a>
            </li>
            <li class="nav-item" *ngIf="!isLoggedIn()">
              <a class="nav-link" href="#" data-bs-toggle="modal" data-bs-target="#registerModal">Đăng ký</a>
            </li>
            <li class="nav-item" *ngIf="isLoggedIn()">
              <a class="nav-link" href="#" (click)="logout(); $event.preventDefault()">Đăng xuất</a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Premium Error Modal -->
    <div class="modal fade" [class.show]="isErrorModalOpen" [style.display]="isErrorModalOpen ? 'block' : 'none'" id="errorModalHeader" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-2xl glass-effect text-dark">
          <div class="modal-header bg-gradient-danger text-white border-0">
            <h5 class="modal-title d-flex align-items-center">
              <i class="bi {{ errorIcon }} me-2 fs-4"></i>
              {{ errorTitle }}
            </h5>
            <button type="button" class="btn-close btn-close-white shadow-none" (click)="closeErrorModal()"></button>
          </div>
          <div class="modal-body p-5 text-center">
            <div class="status-icon-wrapper mb-4 text-center d-flex justify-content-center">
              <div class="status-icon bg-light-danger shadow-sm">
                <i class="bi {{ errorIcon }} text-danger fs-1"></i>
              </div>
            </div>
            <h4 class="fw-bold text-dark mb-3">{{ errorTitle }}</h4>
            <p class="text-muted fs-5 px-3">
              {{ errorDescription }}
            </p>
          </div>
          <div class="modal-footer border-0 p-4 justify-content-center">
            <button type="button" class="btn btn-outline-secondary px-4 me-2 rounded-pill" (click)="closeErrorModal()">Bỏ qua</button>
            <button *ngIf="errorTitle === 'Account Restricted'" type="button" class="btn btn-primary px-4 rounded-pill shadow-sm" (click)="contactSupport()">
              <i class="bi bi-headset me-2"></i>Liên hệ hỗ trợ
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show" *ngIf="isErrorModalOpen"></div>
    
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
              <button type="submit" class="btn btn-primary w-100 py-2 shadow-sm fw-bold">Đăng nhập</button>
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
      color: #fff !important;
    }
    .nav-link {
      font-weight: 500;
      color: rgba(255, 255, 255, 0.95) !important;
      transition: all 0.2s ease-in-out;
    }
    .nav-link:hover {
      color: #fff !important;
      transform: translateY(-1px);
    }
    .nav-link i {
      font-size: 1.1rem;
    }
    .bg-gradient-danger {
      background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
    }
    .status-icon-wrapper {
      display: flex;
      justify-content: center;
    }
    .status-icon {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #fdf2f2;
    }
    .glass-effect {
      backdrop-filter: blur(10px);
      background: rgba(255, 255, 255, 0.95);
    }
    .shadow-2xl {
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
  `]
})
export class HeaderComponent {
  private cartService = inject(CartService);
  private authService = inject(AuthService);
  private router = inject(Router);
  
  isLoggedIn = this.authService.isLoggedIn;
  user = this.authService.currentUser;

  email = '';
  password = '';

  cartCount$ = this.cartService.cartCount$;

  isErrorModalOpen = false;
  errorTitle = '';
  errorDescription = '';
  errorIcon = '';

  login() {
    const returnUrl = this.router.url || '/home';

    this.authService.login(this.email, this.password, returnUrl).subscribe({
      next: () => {
        document.getElementById('closeLoginModal')?.click();
        this.email = '';
        this.password = '';
      },
      error: (err: any) => {
        console.error('Login failed', err);
        document.getElementById('closeLoginModal')?.click();
        
        if (err.status === 401 && err.error?.detail === 'User account is inactive') {
          this.errorTitle = 'Account Restricted';
          this.errorDescription = 'Tài khoản của bạn đã bị vô hiệu hóa hoặc xóa. Vui lòng liên hệ bộ phận hỗ trợ để được trợ giúp.';
          this.errorIcon = 'bi-shield-lock-fill';
          this.isErrorModalOpen = true;
        } else {
          this.errorTitle = 'Authentication Failed';
          this.errorDescription = err.error?.detail || 'Email hoặc mật khẩu không hợp lệ. Yêu cầu thử lại.';
          this.errorIcon = 'bi-exclamation-octagon-fill';
          this.isErrorModalOpen = true;
        }
      }
    });
  }

  logout() {
    this.authService.logout();
  }

  goToCart(event: Event) {
    event.preventDefault();
    if (this.authService.isLoggedIn()) {
      this.router.navigate(['/customer/cart']);
    } else {
      // Show login modal
      const modal = document.getElementById('loginModal');
      if (modal) {
        (window as any).bootstrap.Modal.getOrCreateInstance(modal).show();
      }
    }
  }

  closeErrorModal() {
    this.isErrorModalOpen = false;
  }

  contactSupport() {
    this.closeErrorModal();
    this.router.navigate(['/contact']);
  }
}
