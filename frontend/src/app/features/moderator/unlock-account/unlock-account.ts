import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface UserDetail {
  user_id: number;
  email: string;
  first_name: string;
  last_name: string;
  role_id: number;
  is_active: boolean;
  created_at?: string;
}

@Component({
  selector: 'app-unlock-account',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './unlock-account.html',
  styleUrl: './unlock-account.scss'
})
export class UnlockAccountComponent implements OnInit {
  userId: number | null = null;
  lookupId: number | null = null;
  user: UserDetail | null = null;
  isLoading = false;
  message: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private moderatorService: ModeratorService
  ) {}

  ngOnInit() {
    this.userId = Number(this.route.snapshot.paramMap.get('userId')) || null;
    if (this.userId) {
      this.lookupId = this.userId;
      this.loadUser();
    }
  }

  loadUser() {
    const resolutionId = this.lookupId || this.userId;
    if (!resolutionId) {
      this.user = null;
      return;
    }

    this.isLoading = true;
    this.moderatorService.getUser(resolutionId).subscribe({
      next: (user) => {
        this.user = user as UserDetail;
        this.isLoading = false;
        this.message = null;
      },
      error: (err) => {
        console.error('Failed to load user:', err);
        this.message = 'Không thể tải thông tin người dùng.';
        this.user = null;
        this.isLoading = false;
      }
    });
  }

  unlockAccount() {
    if (!this.userId) return;
    this.isLoading = true;
    this.moderatorService.unbanUser(this.userId, 'Unbanned by moderator').subscribe({
      next: () => {
        this.message = 'Tài khoản đã được mở khóa thành công.';
        this.loadUser();
      },
      error: (err) => {
        console.error('Failed to unlock user:', err);
        this.message = 'Mở khóa tài khoản không thành công.';
        this.isLoading = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/moderator/dashboard']);
  }
}
