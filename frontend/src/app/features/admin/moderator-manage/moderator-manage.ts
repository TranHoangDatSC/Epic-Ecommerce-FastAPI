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
  isLoading = false;
  showModal = false;
  editingModerator: any = null;
  activeTab: 'active' | 'trash' = 'active';

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

    const includeDeleted = this.activeTab === 'trash';

    this.adminService.getModerators(includeDeleted).subscribe({
      next: (data: any) => {
        if (this.activeTab === 'trash') {
          this.moderators = data.filter((mod: any) => mod.is_deleted === true);
        } else {
          this.moderators = data
            .filter((mod: any) => mod.is_deleted !== true)
            .sort((a: any, b: any) => {
              if (a.is_active === b.is_active) return 0;
              return a.is_active ? -1 : 1;
            });
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

  switchTab(tab: 'active' | 'trash'): void {
    this.activeTab = tab;
    this.loadModerators();
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
        alert(err?.error?.detail || 'Tạo moderator thất bại.');
      }
    });
  }

  toggleStatus(moderator: any): void {
    const action = moderator.is_active ? 'lock' : 'unlock';
    const reason = prompt('Lý do ' + (moderator.is_active ? 'khóa' : 'mở khóa') + ' moderator:');
    if (!reason) {
      return;
    }

    this.adminService.toggleModeratorStatus(moderator.user_id, action as 'lock' | 'unlock', reason).subscribe({
      next: () => {
        moderator.is_active = !moderator.is_active;
        moderator.is_deleted = action === 'lock';
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
