import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-seller-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="seller-content-wrapper p-4">
      <div class="seller-page-header">
        <div>
          <h2>Tổng quan Cửa hàng</h2>
          <p>Thống kê nhanh hoạt động kinh doanh của bạn</p>
        </div>
      </div>
      
      <div class="row g-4">
        <div class="col-md-3">
          <div class="seller-card text-center dashboard-stat-card">
            <div class="icon-wrapper bg-primary-light">
              <i class="bi bi-box-seam text-primary"></i>
            </div>
            <h3 class="mt-3 fw-bold">0</h3>
            <p class="text-muted mb-0">Sản phẩm</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="seller-card text-center dashboard-stat-card">
            <div class="icon-wrapper bg-success-light">
              <i class="bi bi-cart-check text-success"></i>
            </div>
            <h3 class="mt-3 fw-bold">0</h3>
            <p class="text-muted mb-0">Đơn hàng mới</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="seller-card text-center dashboard-stat-card">
            <div class="icon-wrapper bg-warning-light">
              <i class="bi bi-wallet2 text-warning"></i>
            </div>
            <h3 class="mt-3 fw-bold">0₫</h3>
             <p class="text-muted mb-0">Doanh thu tạm tính</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="seller-card text-center dashboard-stat-card">
            <div class="icon-wrapper bg-danger-light">
              <i class="bi bi-star text-danger"></i>
            </div>
            <h3 class="mt-3 fw-bold">0.0</h3>
            <p class="text-muted mb-0">Đánh giá trung bình</p>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-stat-card {
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      cursor: pointer;
    }
    .dashboard-stat-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
    }
    .icon-wrapper {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 0 auto;
      font-size: 1.8rem;
    }
    .bg-primary-light { background: rgba(13, 110, 253, 0.1); }
    .bg-success-light { background: rgba(25, 135, 84, 0.1); }
    .bg-warning-light { background: rgba(255, 193, 7, 0.1); }
    .bg-danger-light { background: rgba(220, 53, 69, 0.1); }
  `]
})
export class SellerDashboardComponent implements OnInit {
  ngOnInit() {
  }
}
