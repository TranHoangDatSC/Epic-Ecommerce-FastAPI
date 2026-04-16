import { ChangeDetectorRef, Component, ElementRef, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../core/services/auth.service';
import { Router } from '@angular/router';
declare var bootstrap: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html'
})
export class LoginComponent {
  @ViewChild('loginModalElement') loginModalElement!: ElementRef;
  loginForm: FormGroup;
  isLoading = false;

  constructor(
    private fb: FormBuilder, 
    private authService: AuthService, 
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  onSubmit() {
    if (this.loginForm.invalid) return;

    this.isLoading = true;
    const { email, password } = this.loginForm.value;

    this.authService.login(email, password).subscribe({
      next: () => {
        this.isLoading = false;
        this.hideModal();
        this.loginForm.reset();
      },
      error: (err) => {
        this.isLoading = false;
        this.handleError(err);
        this.cdr.detectChanges();
      }
    });
  }

  private hideModal() {
    const modal = bootstrap.Modal.getInstance(this.loginModalElement.nativeElement);
    modal?.hide();
  }

  private handleError(err: any) {
    // Logic báo lỗi: Ở đây bạn nên dùng UIService.showError() thay vì tự vẽ modal lỗi
    console.error(err);
  }
}