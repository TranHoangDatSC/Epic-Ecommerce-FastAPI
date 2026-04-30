import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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
  message: string | null = null;
  
  currentTab: 'active' | 'locked' = 'active';
  searchTerm: string = '';
  
  // Phân trang
  currentPage = 1;
  pageSize = 5;

  // Modal Khóa/Mở Khóa
  showStatusModal = false;
  isBanAction = false;
  selectedUser: any = null;
  statusReason = '';

  constructor(
    private moderatorService: ModeratorService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  loadUsers(): void {
    this.isLoading = true;
    this.moderatorService.getUsers().subscribe({
      next: (data) => {
        // Lấy tất cả user có Role 3 (Seller/Khách)
        let role3Users = data.filter((u: any) => u.roles && u.roles.some((r: any) => r.role_id === 3));
        
        // Chia tab
        if (this.currentTab === 'active') {
          this.users = role3Users.filter((u: any) => u.is_active);
        } else {
          this.users = role3Users.filter((u: any) => !u.is_active);
        }
        this.filterUsers(); // Lọc tìm kiếm & Render
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  selectTab(tab: 'active' | 'locked'): void {
    this.currentTab = tab;
    this.searchTerm = ''; // Đổi tab thì reset search
    this.loadUsers();
  }

  filterUsers(): void {
    if (!this.searchTerm.trim()) {
      this.filteredUsers = [...this.users];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.filteredUsers = this.users.filter(u => 
        u.username?.toLowerCase().includes(term) ||
        u.email?.toLowerCase().includes(term) ||
        u.full_name?.toLowerCase().includes(term)
      );
    }
    this.currentPage = 1; // Search xong tự nhảy về trang 1
    this.isLoading = false;
    this.cdr.detectChanges();
  }

  // --- LOGIC PHÂN TRANG THÔNG MINH ---
  get paginatedUsers(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredUsers.slice(start, start + this.pageSize);
  }

  get totalPages(): number {
    return Math.ceil(this.filteredUsers.length / this.pageSize) || 1;
  }

  get visiblePages(): number[] {
    const pages: number[] = [];
    const total = this.totalPages;
    const current = this.currentPage;

    let start = Math.max(1, current - 1);
    let end = Math.min(total, current + 1);

    if (current === 1) end = Math.min(total, 3);
    if (current === total) start = Math.max(1, total - 2);

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    return pages;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  // --- MODAL & ACTIONS ---
  openStatusModal(user: any): void {
    this.selectedUser = user;
    this.isBanAction = user.is_active; // Đang active thì modal là KHÓA
    this.statusReason = '';
    this.showStatusModal = true;
  }

  closeStatusModal(): void {
    this.showStatusModal = false;
    this.selectedUser = null;
    this.statusReason = '';
  }

  confirmStatusChange(): void {
    if (!this.statusReason.trim()) return;
    this.actionLoading = true;
    const action = this.isBanAction ? 'lock' : 'unlock';
    
    this.moderatorService.lockUnlockUser(this.selectedUser.user_id, action, this.statusReason).subscribe({
      next: () => {
        this.message = `Thao tác thành công!`;
        this.actionLoading = false;
        this.closeStatusModal();
        this.loadUsers();
        setTimeout(() => this.message = null, 3000);
      },
      error: (err) => {
        this.actionLoading = false;
        alert(err?.error?.detail || 'Lỗi hệ thống');
      }
    });
  }
}