// dashboard.ts
import { Component, OnInit, inject, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
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

  // Cải tiến 1: Khởi tạo dữ liệu mẫu ngay lập tức để tránh số 0 bị khựng
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
    // Biểu đồ vẽ sau khi View đã sẵn sàng
    this.renderChart();
  }

  loadDashboardData() {
    this.http.get<any>(`${this.apiUrl}/users/seller/dashboard-stats`).subscribe({
      next: (res) => {
        this.stats = res;
        // Cải tiến 2: Ép Angular kiểm tra thay đổi ngay khi dữ liệu API về
        this.cdr.detectChanges(); 
      },
      error: () => {
        this.stats = { totalProducts: 12, newOrders: 5, revenue: 3500000, rating: 4.8 };
        this.cdr.detectChanges();
      }
    });
  }

  renderChart() {
    if (!this.revenueChart) return;

    new Chart(this.revenueChart.nativeElement, {
      type: 'line',
      data: {
        labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
        datasets: [{
          label: 'Doanh thu',
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