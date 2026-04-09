import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ModeratorService } from '../../../shared/services/moderator.service';

@Component({
  selector: 'app-moderator-product-manage',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './product-manage.html',
  styleUrl: './product-manage.scss'
})
export class ModeratorProductManageComponent implements OnInit {
  pendingProducts: any[] = [];
  isLoading = false;
  actionLoading = false;
  message: string | null = null;

  constructor(private moderatorService: ModeratorService) {}

  ngOnInit(): void {
    this.loadPendingProducts();
  }

  loadPendingProducts(): void {
    this.isLoading = true;
    this.moderatorService.getPendingProducts().subscribe({
      next: (data) => {
        this.pendingProducts = data || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading pending products:', err);
        this.message = err?.error?.detail || 'Không tải được sản phẩm đang chờ duyệt.';
        this.isLoading = false;
      }
    });
  }

  updateStatus(product: any, status: 'approved' | 'rejected'): void {
    let reason: string | null = null;
    if (status === 'rejected') {
      reason = prompt('Lý do từ chối sản phẩm:');
      if (!reason) {
        return;
      }
    }

    this.actionLoading = true;
    this.message = null;
    const numericStatus = status === 'approved' ? 1 : 2;

    this.moderatorService.approveProduct(product.product_id, numericStatus, reason ?? undefined).subscribe({
      next: () => {
        this.message = `Sản phẩm "${product.product_name}" đã được ${status === 'approved' ? 'phê duyệt' : 'từ chối'}.`;
        this.actionLoading = false;
        this.loadPendingProducts();
      },
      error: (err) => {
        console.error('Error updating product status:', err);
        this.message = err?.error?.detail || 'Không thể cập nhật trạng thái sản phẩm.';
        this.actionLoading = false;
      }
    });
  }
}
