import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

@Component({
  selector: 'app-moderator-user-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-manage.html',
  styleUrl: './user-manage.scss'
})
export class ModeratorUserManageComponent implements OnInit {
  users: any[] = [];
  filteredUsers: any[] = [];
  isLoading = false;
  actionLoading = false;
  searchTerm = '';
  message: string | null = null;

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    this.moderatorService.getUsers().subscribe({
      next: (data) => {
        this.users = data.filter((user: any) => user.role_id === 3);
        this.filteredUsers = [...this.users];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.message = err?.error?.detail || 'Không tải được danh sách người dùng.';
        this.isLoading = false;
      }
    });
  }

  filterUsers(): void {
    const term = this.searchTerm.trim().toLowerCase();
    if (!term) {
      this.filteredUsers = [...this.users];
      return;
    }
    this.filteredUsers = this.users.filter((user) =>
      user.username?.toLowerCase().includes(term) ||
      user.email?.toLowerCase().includes(term) ||
      user.full_name?.toLowerCase().includes(term) ||
      user.user_id?.toString().includes(term)
    );
  }

  toggleLock(user: any): void {
    const action = user.is_active ? 'lock' : 'unlock';
    const label = user.is_active ? 'khóa' : 'mở khóa';
    const reason = prompt(`Lý do ${label} tài khoản:`);
    if (!reason) {
      return;
    }
    this.actionLoading = true;
    this.message = null;
    this.moderatorService.lockUnlockUser(user.user_id, action as 'lock' | 'unlock', reason).subscribe({
      next: () => {
        this.message = `Người dùng đã được ${label}.`;
        this.actionLoading = false;
        this.loadUsers();
      },
      error: (err) => {
        console.error('Error toggling user lock:', err);
        this.message = err?.error?.detail || 'Không thể thay đổi trạng thái người dùng.';
        this.actionLoading = false;
      }
    });
  }
}
