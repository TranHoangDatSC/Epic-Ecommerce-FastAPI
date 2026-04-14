import { Component, OnInit, inject } from '@angular/core';
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

  orders: any[] = [];
  selectedOrder: any = null;
  showDetailModal = false;

  ngOnInit() {
    this.loadOrders();
  }

  loadOrders() {
    // Note: Backend endpoint may only return orders the user bought, unless a seller endpoint is available.
    // For UI demonstration we will fetch from standard orders endpoint.
    this.http.get<any[]>(`${this.apiUrl}/orders`).subscribe({
      next: (data) => {
        this.orders = data;
      },
      error: (err) => console.error('Error loading orders', err)
    });
  }

  viewOrderDetails(orderId: number) {
    this.http.get<any>(`${this.apiUrl}/orders/${orderId}`).subscribe({
      next: (data) => {
        this.selectedOrder = data;
        this.showDetailModal = true;
      },
      error: (err) => {
        this.uiService.showError('Không thể tải chi tiết đơn hàng', 'Lỗi');
      }
    });
  }

  closeDetailModal() {
    this.showDetailModal = false;
    this.selectedOrder = null;
  }

  getOrderStatus(status: number) {
    switch(status) {
      case 0: return { class: 'badge bg-warning text-dark', label: 'Chờ xác nhận' };
      case 1: return { class: 'badge bg-info text-dark', label: 'Đã xác nhận' };
      case 2: return { class: 'badge bg-primary', label: 'Đang giao hàng' };
      case 3: return { class: 'badge bg-success', label: 'Đã giao' };
      case 4: return { class: 'badge bg-danger', label: 'Đã hủy' };
      default: return { class: 'badge bg-secondary', label: 'Không xác định' };
    }
  }

  updateOrderStatus(orderId: number, newStatus: number) {
    if (confirm(`Cập nhật trạng thái đơn hàng thành ${this.getOrderStatus(newStatus).label}?`)) {
      this.http.put(`${this.apiUrl}/v1/orders/${orderId}`, { order_status: newStatus }).subscribe({
        next: () => {
          this.uiService.showSuccess('Cập nhật trạng thái thành công', 'Thành công');
          this.loadOrders();
          this.closeDetailModal();
        },
        error: () => {
          this.uiService.showError('Cập nhật trạng thái thất bại', 'Lỗi');
        }
      });
    }
  }
}
