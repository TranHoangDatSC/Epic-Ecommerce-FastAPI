import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';
import { catchError, finalize } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-violation-log',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './violation-log.html',
  styleUrl: './violation-log.scss'
})
export class ViolationLogComponent implements OnInit {
  private adminService = inject(AdminService);
  private cdr = inject(ChangeDetectorRef);

  logs: any[] = [];
  userMap = new Map<number, string>();
  isLoading = false;
  skip: number = 0; 
  limit: number = 100;

  ngOnInit(): void {
    this.loadInitialData();
  }

  async loadInitialData() {
    this.isLoading = true;
    this.cdr.markForCheck(); // Thông báo Angular chuẩn bị cập nhật UI

    // Bước 1: Load Users trước để có dữ liệu mapping tên
    this.adminService.getUsers(0, 1000).pipe(
      catchError(() => of([]))
    ).subscribe(users => {
      users.forEach((u: any) => this.userMap.set(u.user_id, u.username));
      
      // Bước 2: Sau khi có Map User, load Logs
      this.loadLogs();
    });
  }

  loadLogs() {
    this.isLoading = true;
    this.adminService.getViolationLogs(this.skip, this.limit).subscribe({
      next: (data: any[]) => {
        // Dữ liệu bây giờ đã có log.username trực tiếp từ Backend
        this.logs = data; 
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Lỗi:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  // Mapping text tiếng Việt
  getFriendlyAction(action: string): string {
    const act = action?.toUpperCase() || '';
    if (act.includes('DEACTIVATE_MODERATOR')) return 'Khóa Kiểm duyệt viên';
    if (act.includes('ACTIVATE_MODERATOR')) return 'Mở khóa Kiểm duyệt viên';
    if (act.includes('DEACTIVATE')) return 'Khóa Người dùng';
    if (act.includes('ACTIVATE')) return 'Kích hoạt Người dùng';
    return action;
  }

  getActionClass(action: string): string {
    const act = action?.toUpperCase() || '';
    if (act.includes('DEACTIVATE')) return 'badge-danger';
    if (act.includes('ACTIVATE')) return 'badge-success';
    return 'badge-info';
  }
}