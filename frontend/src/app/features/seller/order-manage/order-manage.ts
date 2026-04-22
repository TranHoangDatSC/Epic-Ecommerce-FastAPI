import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { UIService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-order-manage',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './order-manage.html',
  styleUrl: './order-manage.scss'
})
export class OrderManageComponent implements OnInit {
  private http = inject(HttpClient);
  private uiService = inject(UIService);
  private apiUrl = environment.apiUrl;
  private cdr = inject(ChangeDetectorRef);

  orders: any[] = [];
  selectedOrder: any = null;
  showDetailModal = false;
  filterStatus: number | null = 0;

  get filteredOrders() {
    const filtered = this.orders.filter(o => o.order_status === this.filterStatus);
    console.log(`Status ${this.filterStatus} has ${filtered.length} orders`); // <--- Debug
    return filtered;
  }

  ngOnInit() {
    this.loadOrders();
  }

  loadOrders() {
    this.http.get<any[]>(`${this.apiUrl}/orders/seller`).subscribe({
      next: (data) => {
        console.log('API Response:', data);
        this.orders = data;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.uiService.showError('Không thể tải danh sách đơn hàng', 'Lỗi');
      }
    });
  }

  viewOrderDetails(orderId: number) {
    this.http.get<any>(`${this.apiUrl}/orders/${orderId}`).subscribe({
      next: (data) => {
        this.selectedOrder = data;
        this.showDetailModal = true;
        this.cdr.detectChanges();
      },
      error: () => {
        this.uiService.showError('Không thể tải chi tiết đơn hàng', 'Lỗi');
        this.cdr.detectChanges();
      }
    });
  }

  closeDetailModal() {
    this.showDetailModal = false;
    this.selectedOrder = null;
  }

  getNextStatusLabel(currentStatus: number): string {
    const statusLabels: Record<number, string> = {
      0: 'Xác nhận',
      1: 'Giao hàng',
      2: 'Đã giao'
    };
    return statusLabels[currentStatus] || 'Cập nhật';
  }

  getOrderStatus(status: number): { class: string, label: string } {
    const statusMap: Record<number, { class: string, label: string }> = {
      0: { class: 'badge bg-warning text-dark', label: 'Chờ xác nhận' },
      1: { class: 'badge bg-info text-dark', label: 'Đã xác nhận' },
      2: { class: 'badge bg-primary', label: 'Đang giao hàng' },
      3: { class: 'badge bg-success', label: 'Đã giao' },
      4: { class: 'badge bg-danger', label: 'Đã hủy' }
    };
    return statusMap[status] || { class: 'badge bg-secondary', label: 'Không xác định' };
  }

  updateOrderStatus(orderId: number, newStatus: number) {
    // Sử dụng PUT theo đúng Backend API đã định nghĩa
    this.http.put(`${this.apiUrl}/orders/${orderId}`, { 
      order_status: newStatus 
    }).subscribe({
      next: () => {
        this.uiService.showSuccess('Cập nhật trạng thái thành công', 'Thành công');
        this.loadOrders(); // Tải lại danh sách
        this.closeDetailModal();
      },
      error: (err) => {
        console.error(err);
        this.uiService.showError(err.error?.message || 'Cập nhật thất bại', 'Lỗi');
      }
    });
  }
}