import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ModeratorService } from '../../../shared/services/moderator.service';
import { ProductService } from '../../../shared/services/product.service';
import { CategoryService } from '../../../shared/services/category.service';

declare var bootstrap: any

@Component({
  selector: 'app-moderator-product-manage',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './product-manage.html',
  styleUrl: './product-manage.scss'
})
export class ModeratorProductManageComponent implements OnInit {
  products: any[] = [];
  isLoading = false;
  actionLoading = false;
  message: string | null = null;
  activeTab: 'pending' | 'approved' | 'rejected' = 'pending';
  selectedProduct: any = null;
  targetStatus: number | null = null;
  rejectionReason: string = '';
  category: any[] = [];
  categoryMap: Map<number, string> = new Map();
  userMap: Map<number, string> = new Map();

  constructor(
    private moderatorService: ModeratorService,
    private cdr: ChangeDetectorRef,
    private productService: ProductService,
    private categoryService: CategoryService
  ) {}

  ngOnInit(): void {
    import('rxjs').then(rxjs => {
      rxjs.forkJoin({
        categories: this.categoryService.getCategories(),
        users: this.moderatorService.getUsers()
      }).subscribe(({ categories, users }) => {
        this.category = categories;
        users.forEach(u => this.userMap.set(u.user_id, u.username));
        this.loadProducts();
      });
    });
  }

  loadProducts(): void {
    this.isLoading = true;
    const statusMap = { 'pending': 0, 'approved': 1, 'rejected': 2 };
    const status = statusMap[this.activeTab]; // <--- Đã sửa lỗi thiếu khai báo status

    this.productService.getProductsByStatus(status).subscribe({
      next: (data) => {
        // Tạo map category
        this.category.forEach(c => this.categoryMap.set(c.category_id, c.name));

        this.products = (data || []).map(p => ({
          ...p,
          // Map thông tin
          category_name: this.categoryMap.get(p.category_id) || 'Chưa phân loại',
          seller_name: this.userMap.get(p.seller_id) || 'User #' + p.seller_id,
          product_name: p.title || 'Sản phẩm không tên' // Sửa lỗi lấy title
        }));
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => { this.isLoading = false; }
    });
  }

  selectTab(tab: 'pending' | 'approved' | 'rejected'): void {
    this.activeTab = tab;
    this.loadProducts();
  }

  updateStatus(product: any, targetStatus: 'approved' | 'rejected') {
    const statusMap = { 'approved': 1, 'rejected': 2 };
    const numericStatus = statusMap[targetStatus];
    let reason: string | undefined;

    if (targetStatus === 'rejected') {
      const input = prompt('Lý do từ chối sản phẩm:');
      if (!input || input.trim() === '') {
          return;
      }
      reason = input;
    }

    this.actionLoading = true;
    this.productService.updateProductStatus(product.product_id, numericStatus, reason).subscribe({
      next: () => {
        this.message = `Đã cập nhật trạng thái sản phẩm thành công.`;
        this.actionLoading = false;
        this.loadProducts(); // Tải lại danh sách
      },
      error: (err) => {
        this.message = 'Lỗi cập nhật: ' + (err.error?.detail || 'Vui lòng thử lại.');
        this.actionLoading = false;
      }
    });
  }

  openModal(product: any, status: 'approved' | 'rejected') {
    this.selectedProduct = product;
    this.targetStatus = status === 'approved' ? 1 : 2;
    this.rejectionReason = '';
    const modal = new bootstrap.Modal(document.getElementById('reasonModal'));
    modal.show();
  }

  confirmAction() {
    if (this.targetStatus === 2 && !this.rejectionReason.trim()) {
      alert('Vui lòng nhập lý do từ chối!');
      return;
    }
    
    this.productService.updateProductStatus(
      this.selectedProduct.product_id, 
      this.targetStatus!, 
      this.rejectionReason
    ).subscribe(() => {
      this.closeModal();
      this.loadProducts();
    });
  }

  closeModal() {
    const modalEl = document.getElementById('reasonModal');
    const modal = bootstrap.Modal.getInstance(modalEl);
    modal.hide();
  }

  showFullReason(reason: string) {
    alert("Chi tiết lý do: \n" + reason);
  }
}
