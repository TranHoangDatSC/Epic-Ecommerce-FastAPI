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
  
  // Cấu hình phân trang
  skip: number = 0;
  limit: number = 5; // Đặt là 10 hoặc 20 để dễ quan sát phân trang khi nộp bài

  ngOnInit(): void {
    this.loadInitialData();
  }

  /**
   * Khởi tạo dữ liệu ban đầu
   */
  async loadInitialData() {
    this.isLoading = true;
    this.cdr.markForCheck();

    // Bước 1: Load danh sách User để mapping nếu cần (Dự phòng trường hợp backend ko trả username)
    this.adminService.getUsers(0, 100).pipe(
      catchError(() => of([])),
      finalize(() => {
        // Bước 2: Load danh sách Logs sau khi đã có Map User hoặc kết thúc gọi User
        this.loadLogs();
      })
    ).subscribe(users => {
      users.forEach((u: any) => this.userMap.set(u.user_id, u.username));
    });
  }

  /**
   * Tải danh sách log dựa trên skip và limit
   */
  rawLogsCount: number = 0;
  loadLogs() {
    this.isLoading = true;
    this.adminService.getViolationLogs(this.skip, this.limit).subscribe({
      next: (data: any[]) => {
        this.rawLogsCount = data.length; // Lưu số lượng gốc để check phân trang
        
        this.logs = data
          .filter(log => log.action_taken !== 'ADMIN_ACTION: UNLOCK' && log.action_taken !== 'ADMIN_ACTION: LOCK')
          .map(log => ({
            ...log,
            username: log.username || this.userMap.get(log.user_id) || 'Unknown'
          }));
          
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  nextPage() {
    // Check dựa trên rawLogsCount thay vì logs.length sau khi lọc
    if (!this.isLoading && this.rawLogsCount >= this.limit) {
      this.skip += this.limit;
      this.loadLogs();
      this.scrollToTop();
    }
  }
    // Kiểm tra lại hàm class đảm bảo trả về đúng tên class CSS
  getActionClass(action: string): string {
    const act = action?.toUpperCase() || '';
    
    if (act.includes('DEACTIVATE_MODERATOR')) return 'badge-danger';
    if (act.includes('ACTIVATE_MODERATOR')) return 'badge-success';
    
    if (act.includes('DEACTIVATE')) return 'badge-orange'; 
    if (act.includes('ACTIVATE')) return 'badge-warning';

    return 'badge-info';
  }

  /**
   * Mapping ngôn ngữ hiển thị
   */
  getFriendlyAction(action: string): string {
    const act = action?.toUpperCase() || '';
    if (act.includes('DEACTIVATE_MODERATOR')) return 'Khóa Kiểm duyệt';
    if (act.includes('ACTIVATE_MODERATOR')) return 'Mở Kiểm duyệt';
    if (act.includes('DEACTIVATE')) return 'Khóa Người dùng';
    if (act.includes('ACTIVATE')) return 'Mở Người dùng';
    return action;
  }

  /**
   * Giả lập người thực thi hành động
   * Theo yêu cầu: Khóa Mod là Admin, Khóa User là mod1
   */
  getExecutioner(action: string): string {
    const act = action?.toUpperCase() || '';
    return act.includes('MODERATOR') ? 'Admin' : 'mod1';
  }

  /**
   * Quay lại trang trước
   */
  prevPage() {
    if (!this.isLoading && this.skip > 0) {
      this.skip = Math.max(0, this.skip - this.limit);
      this.loadLogs();
      this.scrollToTop();
    }
  }

  /**
   * Cuộn lên đầu bảng khi chuyển trang (tiện ích UX)
   */
  private scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}