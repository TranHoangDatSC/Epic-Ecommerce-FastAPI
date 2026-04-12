import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AdminService } from '../../../shared/services/admin.service';

@Component({
  selector: 'app-moderator-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './moderator-manage.html',
  styleUrl: './moderator-manage.scss'
})
export class ModeratorManageComponent implements OnInit {
  moderators: any[] = [];
  skip = 0;
  limit = 4;
  isLoading = false;
  showModal = false;
  showStatusModal = false;
  showDuplicateModal = false;
  duplicateErrorMsg = '';
  duplicateErrorTitle = 'Dữ liệu bị trùng!';
  editingModerator: any = null;
  statusModalModerator: any = null;
  statusReason = '';
  statusAction: 'lock' | 'unlock' = 'lock';
  activeTab: 'active' | 'locked' = 'active';

  get pagedModerators(): any[] {
    return this.moderators.slice(this.skip, this.skip + this.limit);
  }

  moderatorForm = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
    address: ''
  };

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadModerators();
  }

  loadModerators(): void {
    this.isLoading = true;
    this.moderators = [];

    // Always fetch all to manage active/locked state in tabs
    this.adminService.getModerators(true).subscribe({
      next: (data: any) => {
        if (this.activeTab === 'locked') {
          // Locked tab: Show moderators where is_active is false
          this.moderators = data.filter((mod: any) => mod.is_active === false);
        } else {
          // Active tab: Show moderators where is_active is true
          this.moderators = data.filter((mod: any) => mod.is_active === true);
        }

        if (this.skip >= this.moderators.length) {
          this.skip = 0;
        }

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        console.error('Error loading moderators:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  switchTab(tab: 'active' | 'locked'): void {
    this.activeTab = tab;
    this.skip = 0;
    this.loadModerators();
  }

  nextPage(): void {
    if (this.skip + this.limit < this.moderators.length) {
      this.skip += this.limit;
    }
  }

  prevPage(): void {
    if (this.skip >= this.limit) {
      this.skip -= this.limit;
    }
  }

  openModal(moderator: any = null): void {
    this.editingModerator = moderator;
    if (moderator) {
      this.moderatorForm = {
        username: moderator.username,
        email: moderator.email,
        password: '',
        full_name: moderator.full_name || '',
        phone_number: moderator.phone_number || '',
        address: moderator.address || ''
      };
    } else {
      this.moderatorForm = {
        username: '',
        email: '',
        password: '',
        full_name: '',
        phone_number: '',
        address: ''
      };
    }
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.editingModerator = null;
  }

  saveModerator(): void {
    if (this.editingModerator) {
      // For now, we don't have an update API, so just close modal
      this.closeModal();
    } else {
      this.createModerator();
    }
  }

  createModerator(): void {
    if (!this.moderatorForm.username || !this.moderatorForm.email || !this.moderatorForm.password || !this.moderatorForm.full_name) {
      alert('Vui lòng điền đầy đủ thông tin bắt buộc.');
      return;
    }

    this.adminService.createModerator(this.moderatorForm).subscribe({
      next: () => {
        this.loadModerators();
        this.closeModal();
      },
      error: (err: any) => {
        console.error('Error creating moderator:', err);
        const detail = err?.error?.detail || 'Tạo moderator thất bại.';
        
        // Cập nhật câu điều kiện để bắt cả tiếng Việt và tiếng Anh cho lỗi trùng lặp
        const isDuplicate = detail.toLowerCase().includes('already exists') || 
                            detail.toLowerCase().includes('đã tồn tại') || 
                            detail.toLowerCase().includes('trùng');

        this.duplicateErrorMsg = detail;
        this.duplicateErrorTitle = isDuplicate ? 'Dữ liệu bị trùng!' : 'Lỗi khởi tạo!';
        this.showDuplicateModal = true;
        
        // Ẩn modal tạo để tránh chồng lấp
        this.showModal = false; 
      }
    });
  }

  closeDuplicateModal(): void {
    this.showDuplicateModal = false;
    this.duplicateErrorMsg = '';
    // Optional: reopen create modal
    this.showModal = true;
  }

  openStatusModal(moderator: any): void {
    this.statusModalModerator = moderator;
    this.statusAction = moderator.is_active ? 'lock' : 'unlock';
    this.statusReason = '';
    this.showStatusModal = true;
  }

  closeStatusModal(): void {
    this.showStatusModal = false;
    this.statusModalModerator = null;
    this.statusReason = '';
  }

  saveStatusChange(): void {
    if (!this.statusModalModerator) {
      return;
    }

    if (!this.statusReason.trim()) {
      alert('Vui lòng nhập lý do.');
      return;
    }

    this.adminService.toggleModeratorStatus(
      this.statusModalModerator.user_id,
      this.statusAction,
      this.statusReason.trim()
    ).subscribe({
      next: () => {
        this.closeStatusModal();
        this.loadModerators();
      },
      error: (err: any) => {
        console.error('Error toggling moderator status:', err);
        alert(err?.error?.detail || 'Không thể cập nhật trạng thái moderator.');
      }
    });
  }

  hardDeleteModerator(userId: number): void {
    if (confirm('CẢNH BÁO: Hành động này sẽ xóa vĩnh viễn moderator và không thể hoàn tác!')) {
      // For now, we don't have hard delete API for moderators
      alert('Chức năng xóa vĩnh viễn moderator chưa được implement.');
    }
  }
}
