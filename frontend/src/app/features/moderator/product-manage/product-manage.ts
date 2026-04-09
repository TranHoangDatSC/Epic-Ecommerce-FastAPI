import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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
  products: any[] = [];
  isLoading = false;
  actionLoading = false;
  message: string | null = null;
  activeTab: 'pending' | 'approved' | 'rejected' = 'pending';

  constructor(
    private moderatorService: ModeratorService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadProducts();
  }

  loadProducts(): void {
    this.isLoading = true;
    this.message = null;
    this.products = [];
    this.cdr.detectChanges();
    
    const obs = this.activeTab === 'pending' 
    ? this.moderatorService.getPendingProducts() 
    : this.activeTab === 'approved' 
      ? this.moderatorService.getArchivedProducts() 
      : this.moderatorService.getRejectedProducts();

    obs.subscribe({
      next: (data) => {
        console.log(`Data for ${this.activeTab}:`, data);
        this.products = data || [];
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading products:', err);
        this.message = err?.error?.detail || 'Không tải được danh sách sản phẩm.';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  selectTab(tab: 'pending' | 'approved' | 'rejected'): void {
    this.activeTab = tab;
    this.loadProducts();
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
        this.loadProducts();
      },
      error: (err) => {
        console.error('Error updating product status:', err);
        this.message = err?.error?.detail || 'Không thể cập nhật trạng thái sản phẩm.';
        this.actionLoading = false;
      }
    });
  }
}
