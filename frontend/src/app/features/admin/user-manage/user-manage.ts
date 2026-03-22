import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-user-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './user-manage.html',
  styleUrl: './user-manage.scss'
})
export class UserManageComponent implements OnInit {
  users: any[] = [];
  skip = 0;
  limit = 20;
  isLoading = false;

  constructor(private adminService: AdminService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers() {
    this.isLoading = true;
    this.adminService.getUsers(this.skip, this.limit).subscribe({
      next: (data) => {
        this.users = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.isLoading = false;
      }
    });
  }

  toggleBan(user: any) {
    const reason = prompt('Reason for action:');
    if (!reason) return;

    if (user.is_active) {
      this.adminService.banUser(user.user_id, reason).subscribe(() => this.loadUsers());
    } else {
      this.adminService.unbanUser(user.user_id, reason).subscribe(() => this.loadUsers());
    }
  }

  deleteUser(userId: number) {
    if (confirm('Are you sure you want to delete this user?')) {
      this.adminService.deleteUser(userId).subscribe(() => this.loadUsers());
    }
  }

  nextPage() {
    this.skip += this.limit;
    this.loadUsers();
  }

  prevPage() {
    if (this.skip >= this.limit) {
      this.skip -= this.limit;
      this.loadUsers();
    }
  }
}
