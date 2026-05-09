import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ProductService } from '../../../shared/services/product.service';
import { AdminService } from '../../../shared/services/admin.service';
import { UIService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-review-manage',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './review-manage.html',
  styleUrl: './review-manage.scss'
})
export class ReviewManageComponent implements OnInit {
  reportedReviews: any[] = [];
  isLoading = false;

  constructor(
    private productService: ProductService,
    private adminService: AdminService,
    private uiService: UIService
  ) {}

  ngOnInit(): void {
    this.loadReportedReviews();
  }

  loadReportedReviews() {
    this.isLoading = true;
    this.productService.getReportedReviews().subscribe({
      next: (data) => {
        this.reportedReviews = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.uiService.showError('Không thể tải danh sách báo cáo');
        this.isLoading = false;
      }
    });
  }

  rejectProduct(productId: number) {
    if (confirm('Bạn có chắc chắn muốn từ chối sản phẩm này?')) {
      this.productService.updateProductStatus(productId, 2, 'Vi phạm chính sách (Từ báo cáo)').subscribe({
        next: () => {
          this.uiService.showSuccess('Đã từ chối sản phẩm');
          this.loadReportedReviews();
        },
        error: (err) => {
          this.uiService.showError('Lỗi khi từ chối sản phẩm: ' + (err.error?.detail || ''));
        }
      });
    }
  }

  lockUser(review: any) {
    // Nếu Backend chưa trả về seller_id trong ReviewResponse, ta phải xử lý.
    // Tạm thời hiển thị cảnh báo nếu không có seller_id.
    const sellerId = review.product?.seller_id; 
    if (!sellerId) {
      this.uiService.showError('Không tìm thấy thông tin người bán. Vui lòng xem chi tiết sản phẩm để khóa.');
      return;
    }

    if (confirm('Bạn có chắc chắn muốn khóa tài khoản người bán này?')) {
      this.adminService.banUser(sellerId, 'Vi phạm chính sách bán hàng').subscribe({
        next: () => {
          this.uiService.showSuccess('Đã khóa tài khoản');
        },
        error: (err) => {
          this.uiService.showError('Lỗi khi khóa tài khoản: ' + (err.error?.detail || ''));
        }
      });
    }
  }
}
