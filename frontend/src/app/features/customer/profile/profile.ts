import { Component, OnInit, inject, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { User } from '../../../core/models/index';
import { AuthService } from '../../../core/services/auth.service';
import { take } from 'rxjs/operators';

@Component({
  selector: 'app-customer-profile',
  standalone: true,
  imports: [CommonModule, FormsModule], // Đã thêm các module cần thiết
  templateUrl: './profile.html',
  styleUrls: ['./profile.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush // Tối ưu hóa render
})

export class ProfileComponent implements OnInit {
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  
  user: User | null = null;
  readonly defaultAvatar = 'assets/images/default-avt.png';

  // Getter an toàn để template sử dụng
  get userProfile(): User {
    return this.user!; 
  }

  ngOnInit() { this.loadUserProfile(); }

  loadUserProfile() {
    this.authService.getMe().pipe(take(1)).subscribe({
      next: (data: User) => {
        this.user = data;
        this.cdr.markForCheck();
      },
      error: (err) => console.error('Lỗi tải profile:', err)
    });
  }

  getAvatarUrl(path: string | null | undefined): string {
    if (!path) return this.defaultAvatar;
    if (path.startsWith('http')) return path;
    return `http://localhost:8000${path}`; 
  }

  onImageError(event: any) { event.target.src = this.defaultAvatar; }
  
  triggerFileUpload() {
    document.getElementById('avatarInput')?.click();
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.authService.uploadAvatar(file).subscribe({
        next: (updatedUser: User) => {
          this.user = updatedUser;
          this.cdr.markForCheck();
          // alert('Avatar updated successfully!');
        },
        error: (err) => console.error('Error uploading avatar:', err)
      });
    }
  }

  saveChanges() {
    if (!this.user) return;

    this.authService.updateProfile(this.user).subscribe({
      next: (updatedUser: User) => {
        this.authService.updateLocalUser(updatedUser); 
        this.user = updatedUser;
        alert('Cập nhật thành công!');
      },
      error: (err: any) => {
        console.error('Lỗi khi lưu:', err);
      }
    });
  }
}