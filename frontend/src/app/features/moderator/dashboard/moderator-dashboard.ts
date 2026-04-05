import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';

@Component({
  selector: 'app-moderator-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './moderator-dashboard.html',
  styleUrl: './moderator-dashboard.scss'
})
export class ModeratorDashboardComponent implements OnInit {
  pendingProducts: any[] = [];
  users: any[] = [];
  violationReviews: any[] = [];
  violationLogs: any[] = [];

  loadingProducts = false;
  loadingUsers = false;
  loadingReviews = false;
  loadingLogs = false;
  actionLoading = false;
  message: string | null = null;

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.loadPendingProducts();
    this.loadUsers();
    this.loadViolationReviews();
    this.loadViolationLogs();
  }

  loadPendingProducts(): void {
    this.loadingProducts = true;
    this.moderatorService.getPendingProducts().subscribe({
      next: (data) => {
        this.pendingProducts = data;
        this.loadingProducts = false;
      },
      error: (err) => {
        console.error('Error loading pending products:', err);
        this.loadingProducts = false;
      }
    });
  }

  loadUsers(): void {
    this.loadingUsers = true;
    this.moderatorService.getUsers().subscribe({
      next: (data) => {
        this.users = data;
        this.loadingUsers = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.loadingUsers = false;
      }
    });
  }

  loadViolationReviews(): void {
    this.loadingReviews = true;
    this.moderatorService.getViolationReviews().subscribe({
      next: (data) => {
        this.violationReviews = data;
        this.loadingReviews = false;
      },
      error: (err) => {
        console.error('Error loading violation reviews:', err);
        this.loadingReviews = false;
      }
    });
  }

  loadViolationLogs(): void {
    this.loadingLogs = true;
    this.moderatorService.getViolationLogs().subscribe({
      next: (data) => {
        this.violationLogs = data;
        this.loadingLogs = false;
      },
      error: (err) => {
        console.error('Error loading violation logs:', err);
        this.loadingLogs = false;
      }
    });
  }

  approveProduct(productId: number): void {
    this.performAction(() => this.moderatorService.approveProduct(productId, 1), 'Sản phẩm đã được duyệt.');
  }

  rejectProduct(productId: number): void {
    const reason = prompt('Lý do từ chối / yêu cầu sửa đổi:');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.approveProduct(productId, 2, reason), 'Sản phẩm đã bị từ chối.');
  }

  banUser(user: any): void {
    const reason = prompt('Lý do cấm tài khoản:');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.banUser(user.user_id, reason), 'Người dùng đã bị cấm.');
  }

  unbanUser(user: any): void {
    const reason = prompt('Lý do mở cấm tài khoản:');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.unbanUser(user.user_id, reason), 'Người dùng đã được gỡ cấm.');
  }

  lockUser(user: any): void {
    const reason = prompt('Lý do khóa tài khoản tạm thời:');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.lockUnlockUser(user.user_id, 'lock', reason), 'Người dùng đã bị khóa.');
  }

  unlockUser(user: any): void {
    const reason = prompt('Lý do mở khóa tài khoản:');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.lockUnlockUser(user.user_id, 'unlock', reason), 'Người dùng đã được mở khóa.');
  }

  handleViolation(review: any): void {
    const reason = confirm('Xác nhận xử lý báo cáo này?');
    if (!reason) {
      return;
    }
    this.performAction(() => this.moderatorService.handleViolation(review.review_id), 'Báo cáo vi phạm đã được xử lý.');
  }

  private performAction(action: () => import('rxjs').Observable<any>, successMessage: string): void {
    this.actionLoading = true;
    this.message = null;
    action().subscribe({
      next: () => {
        this.message = successMessage;
        this.actionLoading = false;
        this.loadDashboard();
      },
      error: (err: any) => {
        console.error('Action failed:', err);
        this.message = err?.error?.detail || 'Thực hiện hành động thất bại.';
        this.actionLoading = false;
      }
    });
  }
}
