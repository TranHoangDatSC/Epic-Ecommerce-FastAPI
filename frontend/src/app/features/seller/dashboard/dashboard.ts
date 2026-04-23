import { Component, OnInit, inject, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-seller-dashboard',
  standalone: true,
  templateUrl: './dashboard.html',
  styleUrls: ['./dashboard.scss'],
  imports: [CommonModule, RouterModule]
})
export class SellerDashboardComponent implements OnInit, AfterViewInit {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;
  private cdr = inject(ChangeDetectorRef);

  @ViewChild('revenueChart') revenueChart!: ElementRef;

  stats = {
    totalProducts: 0,
    newOrders: 0,
    revenue: 0,
    rating: 0
  };

  quickActions = [
    { path: '/seller/product-manage', label: 'Quản lý sản phẩm', icon: 'bi-box-seam-fill', color: 'text-primary' },
    { path: '/seller/order-manage', label: 'Quản lý đơn hàng', icon: 'bi-cart-check-fill', color: 'text-success' }
  ];

  ngOnInit() {
    this.loadDashboardData();
  }

  ngAfterViewInit() {
    this.renderChart();
  }

  loadDashboardData() {
    // Gọi song song Sản phẩm và Đơn hàng để tính toán
    forkJoin({
      products: this.http.get<any[]>(`${this.apiUrl}/products/seller/my-products`).pipe(catchError(() => of([]))),
      orders: this.http.get<any[]>(`${this.apiUrl}/orders/seller`).pipe(catchError(() => of([])))
    }).subscribe({
      next: (res) => {
        // 1. Tổng số sản phẩm
        const totalProducts = res.products.length;

        // 2. Đơn hàng mới (Trạng thái 0: Chờ xác nhận)
        const newOrders = res.orders.filter(o => o.order_status === 0).length;

        // 3. Tính doanh thu: Chỉ cộng các đơn có trạng thái 3 (Đã giao)
        const totalRevenue = res.orders
          .filter(o => o.order_status === 3)
          .reduce((sum, order) => sum + Number(order.final_amount), 0);

        // 4. Đánh giá (Tạm thời fix cứng hoặc lấy từ profile seller nếu có)
        const avgRating = 4.8; 

        this.stats = {
          totalProducts: totalProducts,
          newOrders: newOrders,
          revenue: totalRevenue,
          rating: avgRating
        };

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Lỗi load dữ liệu dashboard:', err);
        this.cdr.detectChanges();
      }
    });
  }

  renderChart() {
    if (!this.revenueChart) return;

    // Giữ nguyên setup cứng đại của bạn
    new Chart(this.revenueChart.nativeElement, {
      type: 'line',
      data: {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        datasets: [{
          label: 'Doanh thu dự kiến',
          data: [500000, 1200000, 800000, 2500000, 1800000, 3000000, 2800000],
          borderColor: '#4285F4',
          backgroundColor: 'rgba(66, 133, 244, 0.1)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } }
      }
    });
  }
}