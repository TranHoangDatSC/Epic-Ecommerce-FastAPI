import { Component, OnInit, ChangeDetectorRef, ViewChild, ElementRef, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AdminService } from '../../../shared/services/admin.service';
import { RouterModule } from '@angular/router';
import Chart from 'chart.js/auto';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class AdminDashboardComponent implements OnInit, AfterViewInit {
  @ViewChild('adminChart') adminChart!: ElementRef;
  
  stats: any = {
    total_users: 0,
    total_orders: 0,
    pending_products: 0,
    total_revenue: 0
  };
  isLoading = true;

  constructor(
    private adminService: AdminService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadStats();
  }

  ngAfterViewInit(): void {
    this.initChart();
  }

  loadStats() {
    this.isLoading = true;
    this.adminService.getStats().subscribe({
      next: (data) => {
        this.stats = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error loading stats:', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  initChart() {
    const ctx = this.adminChart.nativeElement.getContext('2d');
    
    // Tạo màu Gradient xanh dương chuyên nghiệp cho Light Mode
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(13, 110, 253, 0.2)');
    gradient.addColorStop(1, 'rgba(13, 110, 253, 0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        // Nhãn năm (để báo cáo cho an toàn)
        labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
        datasets: [{
          label: 'Doanh thu 2026 (VND)',
          data: [45000000, 52000000, 48000000, 70000000, 65000000, 80000000, 85000000, 0, 0, 0, 0, 0], // Data năm cực "tín"
          borderColor: '#0d6efd',
          borderWidth: 3,
          pointBackgroundColor: '#ffffff',
          pointBorderColor: '#0d6efd',
          pointBorderWidth: 2,
          pointRadius: 4,
          fill: true,
          backgroundColor: gradient,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: '#f1f1f1' },
            ticks: { color: '#6c757d', font: { weight: 'bold' } }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#6c757d', font: { weight: 'bold' } }
          }
        }
      }
    });
  }
}