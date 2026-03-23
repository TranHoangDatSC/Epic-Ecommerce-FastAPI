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
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Login</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form [formGroup]="loginForm" (ngSubmit)="onSubmit()">
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" formControlName="email">
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" formControlName="password">
              </div>
              <button type="submit" class="btn btn-primary w-100" [disabled]="loginForm.invalid">Login</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .bg-primary {
      background-color: #F39C12 !important;
    }
  `]
})
export class LoginComponent {
  loginForm: FormGroup;

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
          document.getElementById('closeLoginModal')?.click();
        },
        error: (error) => {
          console.error('Login failed', error);
          alert('Login failed: ' + (error.error?.detail || 'Unknown error'));
        }
      });
    }
  }
}
