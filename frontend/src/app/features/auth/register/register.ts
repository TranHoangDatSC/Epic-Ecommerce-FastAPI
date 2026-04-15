import { Component } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { AuthService } from '../../../shared/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <div class="modal fade" id="registerModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <form [formGroup]="registerForm" (ngSubmit)="onSubmit()">
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Username</label>
                    <input type="text" class="form-control" formControlName="username">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Full Name</label>
                    <input type="text" class="form-control" formControlName="full_name">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" formControlName="email">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Address</label>
                    <input type="text" class="form-control" formControlName="address">
                  </div>
                </div>

                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" formControlName="password">
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Confirm Password</label>
                    <input type="password" class="form-control" formControlName="confirmPassword">
                    <small class="text-danger" *ngIf="registerForm.hasError('passwordMismatch') && registerForm.get('confirmPassword')?.dirty">
                      Mật khẩu không khớp!
                    </small>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-control" formControlName="phone_number">
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="submit" class="btn btn-primary w-100" [disabled]="registerForm.invalid">Register</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  `
})
export class RegisterComponent {
  registerForm: FormGroup;

  constructor(private fb: FormBuilder, private authService: AuthService) {
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      full_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      address: [''],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required],
      phone_number: ['']
    }, { validators: this.passwordMatchValidator });
  }

  // Custom Validator để so khớp 2 mật khẩu
  passwordMatchValidator(g: AbstractControl): ValidationErrors | null {
    const password = g.get('password')?.value;
    const confirm = g.get('confirmPassword')?.value;
    return password === confirm ? null : { 'passwordMismatch': true };
  }

  onSubmit() {
    if (this.registerForm.valid) {
      // Loại bỏ confirmPassword trước khi gửi lên Backend
      const { confirmPassword, ...dataToSend } = this.registerForm.value;
      
      console.log(">>> Gửi dữ liệu:", dataToSend);
      this.authService.register(dataToSend).subscribe({
        next: (res) => alert('Đăng ký thành công!'),
        error: (err) => alert('Lỗi: ' + JSON.stringify(err.error))
      });
    }
  }
}