import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../shared/services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <div class="modal fade" id="loginModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title font-weight-bold">Login</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" id="closeLoginModal"></button>
          </div>
          <div class="modal-body p-4">
            <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
              <div class="mb-3">
                <label for="email" class="form-label font-weight-bold">Email address</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-envelope"></i></span>
                  <input type="email" class="form-control border-start-0" id="email" formControlName="email" placeholder="example@email.com">
                </div>
              </div>
              <div class="mb-4">
                <label for="password" class="form-label font-weight-bold">Password</label>
                <div class="input-group">
                  <span class="input-group-text bg-light border-end-0"><i class="bi bi-lock"></i></span>
                  <input type="password" class="form-control border-start-0" id="password" formControlName="password" placeholder="••••••••">
                </div>
              </div>
              <button type="submit" class="btn btn-primary w-100 py-2 shadow-sm" [disabled]="loginForm.invalid">
                <i class="bi bi-box-arrow-in-right me-2"></i>Sign In
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Premium Error Modal -->
    <div class="modal fade" [class.show]="isErrorModalOpen" [style.display]="isErrorModalOpen ? 'block' : 'none'" id="errorModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-2xl glass-effect">
          <div class="modal-header bg-gradient-danger text-white border-0">
            <h5 class="modal-title d-flex align-items-center">
              <i class="bi {{ errorIcon }} me-2 fs-4"></i>
              {{ errorTitle }}
            </h5>
            <button type="button" class="btn-close btn-close-white shadow-none" (click)="closeErrorModal()"></button>
          </div>
          <div class="modal-body p-5 text-center">
            <div class="status-icon-wrapper mb-4">
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
  `,
  styles: [`
    .bg-primary {
      background-color: #F39C12 !important;
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
export class LoginComponent {
  loginForm: FormGroup;
  isErrorModalOpen = false;
  errorTitle = '';
  errorDescription = '';
  errorIcon = '';

  constructor(private fb: FormBuilder, private authService: AuthService, private router: Router) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.loginForm.valid) {
      const returnUrl = this.router.url || '/home';

      this.authService.login(this.loginForm.value.email, this.loginForm.value.password, returnUrl).subscribe({
        next: () => {
          console.log('Login successful');
          this.loginForm.reset();
          this.closeLoginModal();
        },
        error: (error) => {
          console.error('Login failed', error);
          this.closeLoginModal();
          
          if (error.status === 401 && error.error?.detail === 'Tài khoản không hoạt động') {
            this.errorTitle = 'Tài khoản bị hạn chế';
            this.errorDescription = 'Tài khoản của bạn đã bị vô hiệu hóa hoặc xóa. Vui lòng liên hệ bộ phận hỗ trợ để được trợ giúp.';
            this.errorIcon = 'bi-shield-lock-fill';
            this.isErrorModalOpen = true;
          } else {
            this.errorTitle = 'Sai thông tin đăng nhập';
            this.errorDescription = error.error?.detail || 'Sai email hoặc mật khẩu. Vui lòng thử lại.';
            this.errorIcon = 'bi-exclamation-octagon-fill';
            this.isErrorModalOpen = true;
          }
        }
      });
    }
  }

  closeLoginModal() {
    const closeBtn = document.getElementById('closeLoginModal');
    if (closeBtn) {
      closeBtn.click();
    } else {
      // Fallback if ID is different
      const modalElement = document.getElementById('loginModal');
      if (modalElement) {
        // Trigger BS close if possible or just use display none
        modalElement.classList.remove('show');
        document.body.classList.remove('modal-open');
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
      }
    }
  }

  closeErrorModal() {
    this.isErrorModalOpen = false;
  }

  contactSupport() {
    // Navigate to contact page or open support link
    window.location.href = '/contact';
    this.closeErrorModal();
  }
}
