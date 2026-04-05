import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ModeratorService } from '../../../shared/services/moderator.service';

interface UserDetail {
  user_id: number;
  username: string;
  email: string;
  full_name: string;
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
  users: UserDetail[] = [];
  isLoading = false;
  message: string | null = null;

  constructor(
    private router: Router,
    private moderatorService: ModeratorService
  ) {}

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.isLoading = true;
    this.message = null;
    this.moderatorService.getUsers().subscribe({
      next: (users) => {
        this.users = users as UserDetail[];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.message = 'Không thể tải danh sách người dùng.';
        this.users = [];
        this.isLoading = false;
      }
    });
  }

  toggleUserStatus(user: UserDetail) {
    this.isLoading = true;
    this.message = null;

    const reason = user.is_active ? 'Locked by moderator' : 'Unlocked by moderator';
    const request$ = user.is_active
      ? this.moderatorService.banUser(user.user_id, reason)
      : this.moderatorService.unbanUser(user.user_id, reason);

    request$.subscribe({
      next: () => {
        this.message = user.is_active
          ? 'Tài khoản đã bị khóa thành công.'
          : 'Tài khoản đã được mở khóa thành công.';
        this.loadUsers();
      },
      error: (err) => {
        console.error('Error changing user status:', err);
        this.message = user.is_active
          ? 'Khóa tài khoản không thành công.'
          : 'Mở khóa tài khoản không thành công.';
        this.isLoading = false;
      }
    });
  }

  goBack() {
    this.router.navigate(['/moderator/dashboard']);
  }
}
