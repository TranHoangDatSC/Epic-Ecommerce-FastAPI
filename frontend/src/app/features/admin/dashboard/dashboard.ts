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
    
    // Gradient cho biểu đồ
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(66, 153, 225, 0.4)');
    gradient.addColorStop(1, 'rgba(66, 153, 225, 0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'CN'],
        datasets: [{
          label: 'Doanh thu hệ thống (VND)',
          data: [1250000, 2800000, 1900000, 4500000, 3200000, 6800000, 5400000], // Data cứng tuần
          borderColor: '#4299e1',
          borderWidth: 3,
          backgroundColor: gradient,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: '#4299e1',
          pointBorderColor: '#fff',
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#a0aec0' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#a0aec0' }
          }
        }
      }
    });
  }
}